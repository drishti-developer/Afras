from openerp.osv import fields, osv, orm
import time
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
import datetime
#from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
from openerp.tools import float_compare
from openerp import netsvc
import openerp.addons.decimal_precision as dp

def extend(class_to_extend):
    """
    Decorator to use to extend a existing class with a new method
    Example :
    @extend(Model)
    def new_method(self, *args, **kwargs):
        print 'I am in the new_method', self._name
        return True
    Will add the method new_method to the class Model
    """
    def decorator(func):
#         if hasattr(class_to_extend, func.func_name):
#             raise except_osv(_("Developper Error"),
#                 _("You can extend the class %s with the method %s.",
#                 "Indeed this method already exist use the decorator 'replace' instead"))
        setattr(class_to_extend, func.func_name, func)
        return class_to_extend
    return decorator

@extend(fields.property)
def _get_by_id( self,obj, cr, uid, prop_name, ids, context=None):
        prop = obj.pool.get('ir.property')
        vids = [obj._name + ',' + str(oid) for oid in  ids]
        
        domain = [('fields_id.model', '=', obj._name), ('fields_id.name', 'in', prop_name)]
        #domain = prop._get_domain(cr, uid, prop_name, obj._name, context)
        if vids:
            domain = [('res_id', 'in', vids)] + domain

        cid = [obj.pool.get('res.users').browse(cr,uid,uid).company_id.id]
        if cid:
             domain =  [('company_id','in',cid)] + domain
        
        return prop.search(cr, uid, domain, context=context)

class account_account(osv.osv):
    _inherit = "account.account"
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        try:
            if name and str(name).startswith('partner:'):
                part_id = int(name.split(':')[1])
                part = self.pool.get('res.partner').browse(cr, user, part_id, context=context)
                args += [('id', 'in', (part.property_account_payable.id, part.property_account_receivable.id))]
                name = False
            if name and str(name).startswith('type:'):
                type = name.split(':')[1]
                args += [('type', '=', type)]
                name = False
        except:
            pass
        
        journal = self.pool.get('account.journal')
        if 'journal_id1' in context:
           if context['journal_id1']: 
            journal_obj = journal.browse(cr,user,context['journal_id1'])
            
            
            if journal_obj.account_control_ids:
                
                account_ids = [account_obj.id for account_obj in journal_obj.account_control_ids]
                args += [('id', 'in', account_ids)]
                
        if name:
            ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('shortcut', '=', name)]+ args, limit=limit)
            if not ids:
                ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit)
            if not ids and len(name.split()) >= 2:
                #Separating code and name of account for searching
                operand1,operand2 = name.split(' ',1) #name can contain spaces e.g. OpenERP S.A.
                ids = self.search(cr, user, [('code', operator, operand1), ('name', operator, operand2)]+ args, limit=limit)
        else:
            ids = self.search(cr, user, args, context=context, limit=limit)
        return self.name_get(cr, user, ids, context=context)
    
    
    
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    
    _columns = {
                'cost_analytic_id' : fields.many2one('account.analytic.account','Cost Center',),
                'vehicle_id': fields.many2one('fleet.vehicle','Vehicle'),
                }

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        
        return {
            'date_maturity': x.get('date_maturity', False),
            'partner_id': part,
            'name': x['name'][:64],
            'date': date,
            'debit': x['price']>0 and x['price'],
            'credit': x['price']<0 and -x['price'],
            'account_id': x['account_id'],
            'analytic_lines': x.get('analytic_lines', []),
            'amount_currency': x['price']>0 and abs(x.get('amount_currency', False)) or -abs(x.get('amount_currency', False)),
            'currency_id': x.get('currency_id', False),
            'tax_code_id': x.get('tax_code_id', False),
            'tax_amount': x.get('tax_amount', False),
            'ref': x.get('ref', False),
            'quantity': x.get('quantity',1.00),
            'product_id': x.get('product_id', False),
            'product_uom_id': x.get('uos_id', False),
            'analytic_account_id': x.get('account_analytic_id', False),
            'vehicle_id':x.get('vehicle_id', False),
            'from_date':x.get('from_date', False),
            'to_date':x.get('to_date', False),
            # Add entry_type
            'entry_type' : x.get('account_analytic_id', False) and self.pool['account.analytic.account'].browse(cr, uid, x.get('account_analytic_id', False)).entry_type,
        }
        
        
    def _get_analytic_lines(self, cr, uid, id, context=None):
        
        if context is None:
            context = {}
        inv = self.browse(cr, uid, id)
        cur_obj = self.pool.get('res.currency')

        company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
        if inv.type in ('out_invoice', 'in_refund'):
            sign = 1
        else:
            sign = -1

        iml = self.pool.get('account.invoice.line').move_line_get(cr, uid, inv.id, context=context)
        for il in iml:
            if il['account_analytic_id']:
                if inv.type in ('in_invoice', 'in_refund'):
                    ref = inv.reference
                else:
                    ref = self._convert_ref(cr, uid, inv.number)
                if not inv.journal_id.analytic_journal_id:
                    raise osv.except_osv(_('No Analytic Journal!'),_("You have to define an analytic journal on the '%s' journal!") % (inv.journal_id.name,))
                il['analytic_lines'] = [(0,0, {
                    'name': il['name'],
                    'date': inv['date_invoice'],
                    'account_id': il['account_analytic_id'],
                    'unit_amount': il['quantity'],
                    'amount': cur_obj.compute(cr, uid, inv.currency_id.id, company_currency, il['price'], context={'date': inv.date_invoice}) * sign,
                    'product_id': il['product_id'],
                    'product_uom_id': il['uos_id'],
                    'general_account_id': il['account_id'],
                    'journal_id': inv.journal_id.analytic_journal_id.id,
                    'ref': ref,
                    'vehicle_id' : il['vehicle_id'],
                    'from_date':il['from_date'],
                    'to_date':il['to_date'],
                    'entry_type' : self.pool['account.analytic.account'].browse(cr, uid, il['account_analytic_id']).entry_type,
                    
                })]
                
        return iml
    
    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines"""
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        payment_term_obj = self.pool.get('account.payment.term')
        journal_obj = self.pool.get('account.journal')
        move_obj = self.pool.get('account.move')
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            
            date_invoice = inv.date_invoice or datetime.datetime.today()
            cost_analytic_id = False
            vehicle_id = False
            if inv.cost_analytic_id and inv.cost_analytic_id.entry_type == 'car':
                vehicle_ids= self.pool.get('fleet.vehicle').search(cr, uid, [('analytic_id','=',inv.cost_analytic_id.id)]) 
                vehicle_id = vehicle_ids and vehicle_ids[0] or False
            fleet_analytic_account_obj = self.pool.get('fleet.analytic.account')
            fleet_analytic = fleet_analytic_account_obj.search(cr, uid, [('date_from','<=',date_invoice),('date_to', '=', False),('vehicle_id','=',vehicle_id)]) or fleet_analytic_account_obj.search(cr, uid, [('date_from','<=',date_invoice),('date_to', '!=', False),('date_to','>=',date_invoice),('vehicle_id','=',vehicle_id)])
            
            if fleet_analytic:
                  fleet_obj = fleet_analytic_account_obj.browse(cr ,uid,fleet_analytic[0] )
                  cost_analytic_id = fleet_obj.branch_id and fleet_obj.branch_id.project_id and fleet_obj.branch_id.project_id.id    
                  self.write(cr,uid, inv.id,{'cost_analytic_id' : cost_analytic_id, 'vehicle_id' : vehicle_id})  
            
            
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice': fields.date.context_today(self,cr,uid,context=context)}, context=ctx)
            company_currency = self.pool['res.company'].browse(cr, uid, inv.company_id.id).currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id, context=ctx)
            # check if taxes are all computed
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            # I disabled the check_total feature
            group_check_total_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'group_supplier_inv_check_total')[1]
            group_check_total = self.pool.get('res.groups').browse(cr, uid, group_check_total_id, context=context)
            if group_check_total and uid in [x.id for x in group_check_total.users]:
                if (inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0)):
                    raise osv.except_osv(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml, context=ctx)
            acc_id = inv.account_id.id

            name = inv['name'] or inv['supplier_invoice_number'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = payment_term_obj.compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False, context=ctx)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')

            part = self.pool.get("res.partner")._find_accounting_partner(inv.partner_id)

            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part.id, date, context=ctx)),iml)

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = journal_obj.browse(cr, uid, journal_id, context=ctx)
            if journal.centralisation:
                raise osv.except_osv(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
                'cost_analytic_id': inv.cost_analytic_id and inv.cost_analytic_id.id or False
            }
            
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update(company_id=inv.company_id.id,
                       account_period_prefer_normal=True)
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id
            
            
            ctx.update(invoice=inv)
            
            
            move_id = move_obj.create(cr, uid, move, context=ctx)
            new_move_name = move_obj.browse(cr, uid, move_id, context=ctx).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name}, context=ctx)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move_obj.post(cr, uid, [move_id], context=ctx)
        self._log_event(cr, uid, ids)
        return True
    
    
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    _columns = {
                'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle'),
                'from_date' : fields.date('From Date'),
                'to_date' : fields.date('To Date'),
                }
    
    def _default_account_id(self, cr, uid, context=None):
        # XXX this gets the default account for the user's company,
        # it should get the default account for the invoice's company
        # however, the invoice's company does not reach this point
        
        if context is None:
            context = {}
        if context.get('type') in ('out_invoice','out_refund'):
            prop = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context)
        else:
            if context.get('journal_id'):
                prop= self.pool.get('account.journal').browse(cr, uid ,context['journal_id']).default_debit_account_id
                
                if not prop:
                    prop = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
            else:    
                prop = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
        return prop and prop.id or False

    _defaults = {
       
        'account_id': _default_account_id,
    }

    def onchange_vehicle(self, cr, uid, ids, vehicle_id,date,context=None):
        """
        onchange Vehicle.
        """
        
        fleet_analytic_obj = self.pool.get('fleet.analytic.account')
        if not date:
            date = datetime.datetime.today()
        fleet_analytic_id = fleet_analytic_obj.search(cr, uid, [('vehicle_id','=',vehicle_id),
                                                    ('date_from','<=',date),
                                                    ('date_to','>=',date)])
        if vehicle_id and fleet_analytic_id:
            fleet_obj = fleet_analytic_obj.browse(cr,uid,fleet_analytic_id[0] )
            return {'value': {'account_analytic_id': fleet_obj.analytic_id.id,}}
        else:
            return {'value': {'account_analytic_id': False, }}
    
    def move_line_get_item(self, cr, uid, line, context=None):
        
        
        return {
            'type':'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit':line.price_unit,
            'quantity':line.quantity,
            'price':line.price_subtotal,
            'account_id':line.account_id.id,
            'product_id':line.product_id.id,
            'uos_id':line.uos_id.id,
            'account_analytic_id':line.account_analytic_id.id,
            'taxes':line.invoice_line_tax_id,
            'vehicle_id' : line.vehicle_id.id,
            'from_date':line.from_date,
            'to_date':line.to_date,
            'entry_type' : line.account_analytic_id.entry_type,
        }
        
    def asset_create(self, cr, uid, lines, context=None):
        context = context or {}
        asset_obj = self.pool.get('account.asset.asset')
        for line in lines:
            if line.asset_category_id:
                 
                vals = {
                    'name': line.vehicle_id and line.vehicle_id.name or line.name,
                    'code': line.invoice_id.number or False,
                    'category_id': line.asset_category_id.id,
                    'purchase_value': line.price_subtotal,
                    'period_id': line.invoice_id.period_id.id,
                    'partner_id': line.invoice_id.partner_id.id,
                    'company_id': line.invoice_id.company_id.id,
                    'currency_id': line.invoice_id.currency_id.id,
                    'purchase_date' : line.invoice_id.date_invoice,
                    'cost_analytic_id':line.invoice_id.cost_analytic_id and line.invoice_id.cost_analytic_id.id or False,
                    'vehicle_id': line.vehicle_id and line.vehicle_id.id,
                    'analytic_id' :   line.vehicle_id and line.vehicle_id.analytic_id and  line.vehicle_id.analytic_id.id or False 
                    
                }
                if not line.asset_category_id.non_depreciation_period:
                   vals['depreciation_start_date'] =line.invoice_id.date_invoice,
                elif  line.asset_category_id.non_depreciation_period == 'months': 
                    vals['depreciation_start_date'] =   datetime.datetime.strptime(line.invoice_id.date_invoice, '%Y-%m-%d')+relativedelta(months=+line.asset_category_id.non_depreciation_value)
                elif line.asset_category_id.non_depreciation_period == 'days':
                      vals['depreciation_start_date'] =   datetime.datetime.strptime(line.invoice_id.date_invoice, '%Y-%m-%d')+relativedelta(days=+line.asset_category_id.non_depreciation_value)
                changed_vals = asset_obj.onchange_category_id(cr, uid, [], vals['category_id'],vals['purchase_date'], context=context)
                vals.update(changed_vals['value'])
                asset_id = asset_obj.create(cr, uid, vals, context=context)
                if line.asset_category_id.open_asset:
                    asset_obj.validate(cr, uid, [asset_id], context=context)
        return True
    
class advance_expense_line(osv.osv):
    _name = "account.expense.line"
    
    def _get_move_check(self, cr, uid, ids, name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = bool(line.move_id)
        return res
    _rec_name = "date"
    _columns = {
                'date' : fields.date('Expense date',required=True),
                'amount' : fields.float('Amount',required=True),
                'voucher_id' : fields.many2one('account.voucher','Voucher ID'),
                'debit_account_id' : fields.many2one('account.account','Debit A/C'),
                'account_id' : fields.many2one('account.account','Credit A/C'),
                'period_id' : fields.many2one('account.period','Period'),
                'account_analytic_id' : fields.many2one('account.analytic.account', 'Analytic Account'),
                'move_id': fields.many2one('account.move', 'Journal Entry'),
                'parent_state': fields.related('voucher_id', 'state', type='char', string='State of Voucher'),
                'move_check': fields.function(_get_move_check, method=True, type='boolean', string='Posted', store=True)
                } 
    
    
    def create_move(self, cr, uid, ids, context=None):
        can_close = False
        if context is None:
            context = {}
        asset_obj = self.pool.get('account.asset.asset')
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        created_move_ids = []
        asset_ids = []
        if not ids:
            ids = self.search(cr,uid,[('date' ,'<=', datetime.datetime.today()),('move_check','=',False),('parent_state','=','posted')])
        for line in self.browse(cr, uid, ids, context=context):
            date = line.date
            period_id = line.period_id and line.period_id.id or False
            company_currency = line.voucher_id.company_id.currency_id.id
            journal  = line.voucher_id.rent_jounral_id
            if journal.currency:
              current_currency = journal.currency and journal.currency.id or False
            else:
                  current_currency = journal.company_id.currency_id.id
                  
            
            context.update({'date': date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = 1 # (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
            voucher_name = line.voucher_id.name or 'test'
            reference = line.voucher_id.number or 'Advance payment adjustment'
             
            journal_id = journal.id
            partner_id = line.voucher_id.partner_id.id
            
       
            move_vals = {
                'name': '/',
                'date': date,
                'ref': reference,
                'period_id': period_id,
                'journal_id': line.voucher_id.rent_jounral_id.id,
                'cost_analytic_id': line.voucher_id.cost_analytic_id and line.voucher_id.cost_analytic_id.id or False
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
           
            move_line_obj.create(cr, uid, {
                'name': '/',
                'ref': reference,
                'move_id': move_id,
                'account_id': line.account_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_id,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': date,
            })
            move_line_obj.create(cr, uid, {
                'name': '/',
                'ref': reference,
                'move_id': move_id,
                'account_id': line.debit_account_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_id,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': line.account_analytic_id.id,
                'date': date,
                
            })
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
#             asset_ids.append(line.asset_id.id)
#         # we re-evaluate the assets to determine whether we can close them
#         for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
#             if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
#                 asset.write({'state': 'close'})
        return created_move_ids
  
class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
    _columns = {
                'from_date': fields.date('From Date'),
                'no_months': fields.integer('No of Months'),
                'analytic_id': fields.many2one('account.analytic.account','Analytic Account'),
                'rent_jounral_id': fields.property(
                    'account.journal',
                    type='many2one',
                    relation='account.journal',
                    string="Rent Expenses Journal",
                    view_load=True,
                    store=True,
                    domain="[('type', 'in', ['purchase','general'])]",
                    
                    ),
                 'adjust_journal_id': fields.many2one('account.journal','Shared Service journal'),
                 'exp_account_id' : fields.many2one('account.account','Expenses Account'),
                 'entry_type': fields.selection([('car', 'Car'), ('branch', 'Branch'),
                                                 ('area', 'Area'), ('city', 'City'),
                                                 ('region', 'Region'), ('segment', 'Segment'),('company','Company'),
                                                 ], 'Cost Center Type',),  
                'car_id' : fields.many2one('fleet.vehicle','Car'),      
                'branch_id': fields.many2one('sale.shop',  'Branch'), 
                'area_id': fields.many2one('res.city.area',  'Area'),
                'city_id': fields.many2one('res.state.city',  'City'), 
                'region_id': fields.many2one('res.country.state',  'State'),
                'segment': fields.selection([('retail','Retail'),('corporate','Corporate')],'Segment'),
                'country_id': fields.many2one('res.country',  'Country'),  
                'cost_analytic_id' : fields.many2one('account.analytic.account','Cost Center'),  
                'advance_payment': fields.boolean('Advance Payment'), 
                'account_expense_id' : fields.one2many('account.expense.line', 'voucher_id', 'Expense Line'),
                'vehicle_id': fields.many2one('fleet.vehicle','Vehicle'),
                

                
                  
                }
    _defaults = {
                 'entry_type' : 'branch',
                }
    
    
    def account_move_get1(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference
            
        period_pool = self.pool.get('account.period')   
        ctx = context.copy()
        ctx.update({'company_id': voucher.adjust_journal_id.company_id.id, 'account_period_prefer_normal': True})
        
        pids = period_pool.find(cr, uid, voucher.date, context=ctx)
        
        move = {
            'name': name,
            'journal_id': voucher.adjust_journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': pids and pids[0],
            
        }
        return move

    def account_move_get(self, cr, uid, voucher_id, context=None):
        '''
        This method prepare the creation of the account move related to the given voucher.

        :param voucher_id: Id of voucher for which we are creating account_move.
        :return: mapping between fieldname and value of account move to create
        :rtype: dict
        '''
        seq_obj = self.pool.get('ir.sequence')
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.number:
            name = voucher.number
        elif voucher.journal_id.sequence_id:
            if not voucher.journal_id.sequence_id.active:
                raise osv.except_osv(_('Configuration Error !'),
                    _('Please activate the sequence of selected journal !'))
            c = dict(context)
            c.update({'fiscalyear_id': voucher.period_id.fiscalyear_id.id})
            name = seq_obj.next_by_id(cr, uid, voucher.journal_id.sequence_id.id, context=c)
        else:
            raise osv.except_osv(_('Error!'),
                        _('Please define a sequence on the journal.'))
        if not voucher.reference:
            ref = name.replace('/','')
        else:
            ref = voucher.reference

        move = {
            'name': name,
            'journal_id': voucher.journal_id.id,
            'narration': voucher.narration,
            'date': voucher.date,
            'ref': ref,
            'period_id': voucher.period_id.id,
        }
        return move
    
    def onchange_exp_journal(self, cr, uid, ids, journal_id, context=None):
        if journal_id:
            journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_id, context)
            exp_account_id = journal_obj.default_debit_account_id.id
            
            return {'value':{'exp_account_id':exp_account_id,}}
        return {}
    
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        
        
        for voucher in self.browse(cr, uid, ids, context):
            fleet_analytic_account_obj = self.pool.get('fleet.analytic.account')
            
            cost_analytic_id = False
            vehicle_id = False
            
            
            if voucher.cost_analytic_id and voucher.cost_analytic_id.entry_type == 'car':
                vehicle_ids= self.pool.get('fleet.vehicle').search(cr, uid, [('analytic_id','=',voucher.cost_analytic_id.id)]) 
                vehicle_id = vehicle_ids and vehicle_ids[0] or False
            
            fleet_analytic = fleet_analytic_account_obj.search(cr, uid, [('date_from','<=',voucher.date),('date_to', '=', False),('vehicle_id','=',vehicle_id)]) or fleet_analytic_account_obj.search(cr, uid, [('date_from','<=',voucher.date),('date_to', '!=', False),('date_to','>=',voucher.date),('vehicle_id','=',vehicle_id)])
            if fleet_analytic:
                  fleet_obj = fleet_analytic_account_obj.browse(cr ,uid,fleet_analytic[0] )
                  cost_analytic_id = fleet_obj.branch_id and fleet_obj.branch_id.project_id and fleet_obj.branch_id.project_id.id
                  self.write(cr,uid, voucher.id,{'cost_analytic_id' : cost_analytic_id, 'vehicle_id' : vehicle_id})    
             
            if voucher.from_date and voucher.no_months and voucher.cost_analytic_id:
                self.purchase_receipt(cr, uid, ids, context=None)
                
            self.action_move_line_create(cr, uid, ids, context=context)
        return True
    
    
    def purchase_receipt(self, cr, uid, ids, context=None):
        expense_line_obj = self.pool.get('account.expense.line')
        voucher_obj = self.pool.get('account.voucher') 
        voucher_line_obj = self.pool.get('account.voucher.line') 
        period_pool = self.pool.get('account.period')
        voucher_ids = []
        for voucher in self.browse(cr, uid, ids, context):
          for voucher_line in voucher.line_ids:  
            #try:
            from_date = datetime.datetime.strptime(voucher.from_date[:10],"%Y-%m-%d")
#             except:
#                 from_date = datetime.datetime.strptime(voucher.from_date,"%Y-%m-%d %H:%M:%S")   
            analytic_ids = [voucher.cost_analytic_id.id]
            per_month = voucher_line.amount/voucher.no_months
            account_id = voucher.account_id.id
            
            if voucher_line.type == 'dr':
                voucher_type = 'purchase'
            else:
                voucher_type = 'sale' 
                
            for month in range(voucher.no_months):
                from_date1 = from_date + relativedelta(months=month+1) - relativedelta(days=1)
                pids = period_pool.find(cr, uid, from_date1, context=None)
    
            
              
                
                expense_line_dic = { 'date': from_date1,
                                     'amount' : per_month,
                                     'voucher_id': voucher.id,
                                      'period_id': pids and pids[0],
                                     'account_id' : voucher_line.account_id.id, 
                                     'debit_account_id' : voucher.exp_account_id.id,
                                     'account_analytic_id' : analytic_ids and analytic_ids[0] or False,
                                
                                }
                line_id = expense_line_obj.create(cr,uid,expense_line_dic )
        
            
            
        return True
    def purchase_receipt1(self, cr, uid, ids, context=None):
        analytic_obj = self.pool.get('account.analytic.account')
        voucher_obj = self.pool.get('account.voucher') 
        voucher_line_obj = self.pool.get('account.voucher.line') 
        period_pool = self.pool.get('account.period')
        voucher_ids = []
        for voucher in self.browse(cr, uid, ids, context):
          for voucher_line in voucher.line_ids:  
            try:
               from_date = datetime.datetime.strptime(voucher.from_date,"%Y-%m-%d")
            except:
                from_date = datetime.datetime.strptime(voucher.from_date,"%Y-%m-%d %H:%M:%S")   
            analytic_ids = [voucher.cost_analytic_id.id]
            per_month = voucher_line.amount/voucher.no_months
            account_id = voucher.account_id.id
            
            if voucher_line.type == 'dr':
                voucher_type = 'purchase'
            else:
                voucher_type = 'sale'
            for month in range(voucher.no_months):
                from_date1 = from_date + relativedelta(months=month+1) - relativedelta(days=1)
                pids = period_pool.find(cr, uid, from_date1, context=None)
    
            
                voucher_dict = { 'partner_id' : voucher.partner_id.id,
                                'company_id' : voucher.company_id.id,
                                'date': from_date1,
                                'date_due': from_date1,
                                'type' : voucher_type,
                                'account_id' : voucher_line.account_id.id,
                                'journal_id' : voucher.rent_jounral_id.id,
                                'amount' :per_month,
                                'cost_analytic_id': voucher.cost_analytic_id.id,
                                'period_id': pids and pids[0],
                               # 'line_dr_ids' :[],                    
                 }
                voucher_id = voucher_obj.create(cr,uid,voucher_dict)
                voucher_ids.append(voucher_id)
                voucher_line_dic = { 'account_id' : voucher.exp_account_id.id, 
                                'account_analytic_id' : analytic_ids and analytic_ids[0] or False,
                                'amount' : per_month,
                                'voucher_id': voucher_id,
                                'type': voucher_line.type,
                                }
                line_id = voucher_line_obj.create(cr,uid,voucher_line_dic )
        wf_service = netsvc.LocalService("workflow")
        for vid in voucher_ids:
            wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)   
            
            
        return True
    
    
    def basic_onchange_partner(self, cr, uid, ids, partner_id, journal_id, ttype, context=None):
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        res = {'value': {'account_id': False}}
        
        if not partner_id and  not journal_id:
            return res

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        account_id = False
        if partner_id and journal.type in ('sale','sale_refund'):
            account_id = partner.property_account_receivable.id
        elif partner_id and journal.type in ('purchase', 'purchase_refund','expense'):
            account_id = partner.property_account_payable.id
        else:
            account_id = journal.default_credit_account_id.id or journal.default_debit_account_id.id
        
        res['value']['account_id'] = account_id
        return res
    
    
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
       
        if not context:
             context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        vals['value'].update({'currency_id': currency_id})
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
        res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
        
        for key in res.keys():
            vals[key].update(res[key])
        return vals

    def first_move_line_get1(self, cr, uid, voucher_id, move_id, company_currency, current_currency, context=None):
        '''
        Return a dict to be use to create the first account move line of given voucher.

        :param voucher_id: Id of voucher what we are creating account_move.
        :param move_id: Id of account move where this line will be added.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: mapping between fieldname and value of account move line to create
        :rtype: dict
        '''
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        debit = credit = 0.0
        # TODO: is there any other alternative then the voucher type ??
        # ANSWER: We can have payment and receipt "In Advance".
        # TODO: Make this logic available.
        # -for sale, purchase we have but for the payment and receipt we do not have as based on the bank/cash journal we can not know its payment or receipt
        if voucher.type in ('purchase', 'payment'):
            credit = voucher.paid_amount_in_company_currency
        elif voucher.type in ('sale', 'receipt'):
            debit = voucher.paid_amount_in_company_currency
        if debit < 0: credit = -debit; debit = 0.0
        if credit < 0: debit = -credit; credit = 0.0
        sign = debit - credit < 0 and -1 or 1
        #set the first line of the voucher
        period_pool = self.pool.get('account.period')   
        ctx = context.copy()
        ctx.update({'company_id': voucher.adjust_journal_id.company_id.id, 'account_period_prefer_normal': True})
        
        pids = period_pool.find(cr, uid, voucher.date, context=ctx)
        move_line = {
                'name': voucher.name or '/',
                'debit': debit,
                'credit': credit,
                'account_id': voucher.adjust_journal_id.default_debit_account_id.id,
                'move_id': move_id,
                'journal_id': voucher.adjust_journal_id.id,
                'period_id': pids and pids[0],
                'partner_id': voucher.company_id.partner_id.id,
                'currency_id': company_currency <> current_currency and  current_currency or False,
                'amount_currency': company_currency <> current_currency and sign * voucher.amount or 0.0,
                'date': voucher.date,
                'date_maturity': voucher.date_due
            }
        return move_line
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            if voucher.adjust_journal_id:
                move_id1 = move_pool.create(cr, uid, self.account_move_get1(cr, uid, voucher.id, context=context), context=context)
                move_line_id1 = move_line_pool.create(cr, uid, self.first_move_line_get1(cr,uid,voucher.id, move_id1, company_currency, current_currency, context), context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
            
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)
            if voucher.adjust_journal_id:
                self.voucher_move_line_create1(cr, uid, voucher.id, line_total, move_id1, company_currency, current_currency, context)
            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True

    def voucher_move_line_create1(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = voucher.type in ('payment', 'purchase') and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
                
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'vehicle_id': line.vehicle_id and line.vehicle_id.id or False,
                'from_date':line.from_date,
                'to_date':line.to_date,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date,
                'cost_analytic_id': voucher.cost_analytic_id and voucher.cost_analytic_id.id or False
            }
            if voucher.adjust_journal_id:
                period_pool = self.pool.get('account.period')   
                ctx = context.copy()
                ctx.update({'company_id': voucher.adjust_journal_id.company_id.id, 'account_period_prefer_normal': True})
#                 voucher_currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, voucher.adjust_journal_id.company_id.id, context=ctx).currency_id.id
                pids = period_pool.find(cr, uid, date, context=ctx) 
                move_line1 = {
                    'journal_id': voucher.adjust_journal_id.id,
                    'period_id': pids and pids[0] or False,
                    'name': line.name or '/',
                    'account_id': 4646,
                    'move_id': move_id,
                    'partner_id': voucher.company_id.partner_id.id,
                    'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                    #'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                   # 'vehicle_id': line.vehicle_id and line.vehicle_id.id or False,
                    'from_date':line.from_date,
                    'to_date':line.to_date,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': voucher.date,
                    'company_id': voucher.adjust_journal_id.company_id.id,
                   # 'cost_analytic_id': voucher.cost_analytic_id and voucher.cost_analytic_id.id or False
            } 
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
                move_line1['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount
                move_line1['credit'] = amount
            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    sign = voucher.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            move_line1['amount_currency'] = amount_currency
#             voucher_line = move_line_obj.create(cr, uid, move_line)
            voucher_line = move_line_obj.create(cr, uid, move_line1)
            
        return True
    
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = voucher.type in ('payment', 'purchase') and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
                
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'vehicle_id': line.vehicle_id and line.vehicle_id.id or False,
                'from_date':line.from_date,
                'to_date':line.to_date,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date,
                'cost_analytic_id': voucher.cost_analytic_id and voucher.cost_analytic_id.id or False
            }
            
                
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
                
            else:
                tot_line -= amount
                move_line['credit'] = amount
                
            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    sign = voucher.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            
            voucher_line = move_line_obj.create(cr, uid, move_line)
#             voucher_line1 = move_line_obj.create(cr, uid, move_line1)
            rec_ids = [voucher_line, line.move_line_id.id]

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
        return (tot_line, rec_lst_ids)

    
    
class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'
   

    _columns = {
                'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle'),
                 'from_date' : fields.date('From Date'),
                'to_date' : fields.date('To Date'),
                }
    
    def onchange_vehicle(self, cr, uid, ids, vehicle_id,date,context=None):
        """
        onchange Vehicle.
        """
        
        fleet_analytic_obj = self.pool.get('fleet.analytic.account')
        if not date:
            date = datetime.datetime.today()
        fleet_analytic_id = fleet_analytic_obj.search(cr, uid, [('vehicle_id','=',vehicle_id),
                                                    ('date_from','<=',date),
                                                    ('date_to','>=',date)])
        if vehicle_id and fleet_analytic_id:
            fleet_obj = fleet_analytic_obj.browse(cr,uid,fleet_analytic_id[0] )
            return {'value': {'account_analytic_id': fleet_obj.analytic_id.id,}}
        else:
            return {'value': {'account_analytic_id': False, }}

class account_move(osv.osv):
    _inherit = "account.move"
    _columns = {
                'cost_analytic_id' : fields.many2one('account.analytic.account','Cost Center',),
                }
       

    
class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    
    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        if ids != [47]:
            
            for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
                for line in move.line_id:
                    result.append(line.id)
                
        return result 
    
    _columns = {
                'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle'),
                'from_date' : fields.date('From Date'),
                'to_date' : fields.date('To Date'),
                'cost_analytic_id': fields.related('move_id','cost_analytic_id', string='Cost Center', type='many2one' ,relation='account.analytic.account',
                                store = {
                             'account.move' : (_get_move_lines, ['cost_analytic_id',], 20)
                                }),
                 
                }
    
    def _query_get(self, cr, uid, obj='l', context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        fiscalperiod_obj = self.pool.get('account.period')
        account_obj = self.pool.get('account.account')
        analytic_obj = self.pool.get('account.analytic.account')
        fiscalyear_ids = []
        if context is None:
            context = {}
        initial_bal = context.get('initial_bal', False)
        company_clause = " "
        if context.get('company_id', False):
            company_clause = " AND " +obj+".company_id = %s" % context.get('company_id', False)
        if not context.get('fiscalyear', False):
            if context.get('all_fiscalyear', False):
                #this option is needed by the aged balance report because otherwise, if we search only the draft ones, an open invoice of a closed fiscalyear won't be displayed
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [])
            else:
                fiscalyear_ids = fiscalyear_obj.search(cr, uid, [('state', '=', 'draft')])
        else:
            #for initial balance as well as for normal query, we check only the selected FY because the best practice is to generate the FY opening entries
            fiscalyear_ids = [context['fiscalyear']]

        fiscalyear_clause = (','.join([str(x) for x in fiscalyear_ids])) or '0'
        state = context.get('state', False)
        
        where_move_state = ''
        where_move_lines_by_date = ''

        if context.get('date_from', False) and context.get('date_to', False):
            if initial_bal:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date < '" +context['date_from']+"')"
            else:
                where_move_lines_by_date = " AND " +obj+".move_id IN (SELECT id FROM account_move WHERE date >= '" +context['date_from']+"' AND date <= '"+context['date_to']+"')"

        if state:
            if state.lower() not in ['all']:
                where_move_state= " AND "+obj+".move_id IN (SELECT id FROM account_move WHERE account_move.state = '"+state+"')"
        if context.get('period_from', False) and context.get('period_to', False) and not context.get('periods', False):
            if initial_bal:
                period_company_id = fiscalperiod_obj.browse(cr, uid, context['period_from'], context=context).company_id.id
                first_period = fiscalperiod_obj.search(cr, uid, [('company_id', '=', period_company_id)], order='date_start', limit=1)[0]
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, first_period, context['period_from'])
            else:
                context['periods'] = fiscalperiod_obj.build_ctx_periods(cr, uid, context['period_from'], context['period_to'])
        if context.get('periods', False):
            if initial_bal:
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)
                period_ids = fiscalperiod_obj.search(cr, uid, [('id', 'in', context['periods'])], order='date_start', limit=1)
                if period_ids and period_ids[0]:
                    first_period = fiscalperiod_obj.browse(cr, uid, period_ids[0], context=context)
                    ids = ','.join([str(x) for x in context['periods']])
                    query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND date_start <= '%s' AND id NOT IN (%s)) %s %s" % (fiscalyear_clause, first_period.date_start, ids, where_move_state, where_move_lines_by_date)
            else:
                ids = ','.join([str(x) for x in context['periods']])
                query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s) AND id IN (%s)) %s %s" % (fiscalyear_clause, ids, where_move_state, where_move_lines_by_date)
        else:
            query = obj+".state <> 'draft' AND "+obj+".period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (%s)) %s %s" % (fiscalyear_clause, where_move_state, where_move_lines_by_date)

        if initial_bal and not context.get('periods', False) and not where_move_lines_by_date:
            #we didn't pass any filter in the context, and the initial balance can't be computed using only the fiscalyear otherwise entries will be summed twice
            #so we have to invalidate this query
            raise osv.except_osv(_('Warning!'),_("You have not supplied enough arguments to compute the initial balance, please select a period and a journal in the context."))


        if context.get('journal_ids', False):
            query += ' AND '+obj+'.journal_id IN (%s)' % ','.join(map(str, context['journal_ids']))
        
         
        if context.get('cost_analytic_ids', False):
            if context.get('child_cost_center', False):
                child_ids = analytic_obj._get_children(cr, uid, context['cost_analytic_ids'], context=context)
            else:
                child_ids = context['cost_analytic_ids']
            query += ' AND '+obj+'.cost_analytic_id IN (%s)' % ','.join(map(str,child_ids))

        if context.get('chart_account_id', False):
            child_ids = account_obj._get_children_and_consol(cr, uid, [context['chart_account_id']], context=context)
            query += ' AND '+obj+'.account_id IN (%s)' % ','.join(map(str, child_ids))

        query += company_clause
        
        return query
    
    
    
    def _prepare_analytic_line(self, cr, uid, obj_line, context=None):
        """
        Prepare the values given at the create() of account.analytic.line upon the validation of a journal item having
        an analytic account. This method is intended to be extended in other modules.

        :param obj_line: browse record of the account.move.line that triggered the analytic line creation
        """
        return {'name': obj_line.name,
                'date': obj_line.date,
                'account_id': obj_line.analytic_account_id.id,
                'unit_amount': obj_line.quantity,
                'product_id': obj_line.product_id and obj_line.product_id.id or False,
                'product_uom_id': obj_line.product_uom_id and obj_line.product_uom_id.id or False,
                'amount': (obj_line.credit or  0.0) - (obj_line.debit or 0.0),
                'general_account_id': obj_line.account_id.id,
                'journal_id': obj_line.journal_id.analytic_journal_id.id,
                'ref': obj_line.ref,
                'move_id': obj_line.id,
                'user_id': uid,
                'vehicle_id':  obj_line.vehicle_id and  obj_line.vehicle_id.id,
                'from_date': obj_line.from_date,
                'to_date' : obj_line.to_date,
                'next_split_date' : obj_line.from_date or obj_line.date,
                'entry_type' : obj_line.analytic_account_id.entry_type,
               }  
      
        
