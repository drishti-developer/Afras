from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
import datetime
import time
class account_fiscal_journal(osv.osv):
    _name = 'account.fiscal.journal'
    _columns = {
        'position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', required=True, ondelete='cascade'),
        'journal_src_id': fields.many2one('account.journal', 'Journal Source', required=True, ondelete='restrict'),
        'journal_dest_id': fields.many2many('account.journal', 'account_fiscal_journal_rel','name','code','Journal Destination',  ondelete='restrict'),
        'inter_journal_dest_id': fields.many2one('account.journal','Journal Destination', ondelete='restrict'),
        'company_id' : fields.related('inter_journal_dest_id','company_id',type='many2one',relation='res.company',string='Company',readonly=True,store=True),
        'company_ids': fields.many2many('res.company', 'account_fiscal_company_rel','name','code','Share/Tech Company',  ondelete='restrict'),
        }
account_fiscal_journal()

class account_fiscal_default_account(osv.osv):
    _name = 'account.fiscal.default.account'
    _rec_name = 'type'
    _columns = {
        'type':fields.selection([('in_invoice','Income Account'),('out_invoice','Expenses Account')],'Type',required=True),  
        'account_id': fields.many2one('account.account', 'Account', required=True, ondelete='cascade'),     
        'company_id' : fields.related('account_id','company_id',type='many2one',relation='res.company',string='Company',readonly=True,store=True),
        
        }
account_fiscal_default_account()


class account_fiscal_position(osv.osv):
    _inherit = 'account.fiscal.position'
    _columns = {
                'type':fields.selection([('st','Standard'),('icb','Inter-Company Billing'),('T','Technology'),('ss','Share Service')],'Type'),
               'journal_ids': fields.one2many('account.fiscal.journal', 'position_id', 'Journal Mapping'),
               'journal_ids1':fields.one2many('account.fiscal.journal', 'position_id', 'Journal Mapping'),
                 }
account_fiscal_position()
   
class supplier_account_invoice(osv.osv):
    _name='supplier.account.invoice'
    _columns={
              'journal_id':fields.many2one('account.journal','Journal Id'),
              'account_id':fields.many2one('account.account','Account Id'),
              'percentage':fields.float('Percentage'),
              'company_id':fields.many2one('res.company','Company Id'),
              'invoice_ids':fields.many2one('account.invoice','Account Invoice'),
              'partner_id':fields.many2one('res.partner','Partner Id'),
              'position_id': fields.many2one('account.fiscal.position', 'Fiscal Position',  ondelete='cascade'),
              'date' : fields.related('invoice_ids','date_invoice',type='date',string='Date',store=True),
              'fiscal_type' : fields.related('invoice_ids','fiscal_type',type='char',string='Fiscal Position Type',readonly=True,store=True),
              'split_done': fields.boolean('Split Done'),
              
              }
class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
              'customer_account_invoice_ids':fields.one2many('supplier.account.invoice','invoice_ids','Journal'),
              'is_intragroup_invoice_company': fields.boolean('Is an intra-group company'),
              'fiscal_type':fields.selection([('icb','Inter-Company Billing'),('T','Technology'),('ss','Share Service')],'Fiscal Position Type'),
              }
    
    #########################################################################################################
    
    def split_tech_invoice(self, cr, uid, ids, context=None):
        
        tech_invoice_obj = self.pool.get('supplier.account.invoice')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        company_obj = self.pool.get('res.company')
        period_obj = self.pool.get('account.period')
        res_partner = self.pool.get('res.partner')
        fiscal_jurnl_obj = self.pool.get('account.fiscal.journal')
        fiscal_obj = self.pool.get('account.fiscal.position')
        property_obj = self.pool.get('ir.property')
        
        
        date = datetime.datetime.strptime(time.strftime('%Y-%m-01'), '%Y-%m-%d') 
        to_date = datetime.datetime.strptime(date.strftime('%Y-%m-01'), '%Y-%m-%d') - datetime.timedelta(days=1)   
        from_date =  datetime.datetime.strptime(to_date.strftime('%Y-%m-01'), '%Y-%m-%d')
         
        company_ids = company_obj.search(cr, uid,[])
        company_brws = company_obj.browse(cr, uid, company_ids)
        partner_ids = []
        partner_dict = {}
        
        # Get Related Partner ID of all company
        for company_brw in company_brws:
            partner_id = company_brw.partner_id.id
            partner_ids.append(partner_id)
            partner_dict[partner_id] = company_brw
        
        
        #For each partner related to share company create two journal entry
        # one entry in share company and other entry in partner company
        for partner_id in partner_ids:
            
            total_debit_amt = 0
            total_credit_amt = 0
            ctx = {}
            ctx1 = {}
            move_id = False
            move_id1 = False
            currency = False
            position_id = False
            date1 = False
            journal_id1 = False
            period_id =False
            account_id = False 
            tech_invoice_line = tech_invoice_obj.search(cr, uid, [('split_done','!=',True),('date','<',date),('date','>=',from_date)\
                                                                  ('fiscal_type','=','ss'),('partner_id','=',partner_id)])
            tech_invoice_obj.write(cr, uid, tech_invoice_line,{'split_done': True})
            
            # As of now creating account move base on first journal id and date
           
            for tech_invoice_brw in tech_invoice_obj.browse(cr, uid,tech_invoice_line):
                
                # Get Currency of company
                currency = tech_invoice_brw.journal_id.currency.id
                #Get Company ID of both company
                company_id = tech_invoice_brw.company_id.id
                company_id1 = partner_dict[partner_id].id
                
                # Get the period id of both intercompany
                ctx.update(company_id=company_id,account_period_prefer_normal=True)
                period_ids = period_obj.find(cr, uid, to_date, context=ctx)
                period_id = period_ids and period_ids[0] or False
                
                ctx1.update(company_id=company_id1,account_period_prefer_normal=True)
                period_ids1 = period_obj.find(cr, uid, to_date, context=ctx1)
                period_id1 = period_ids1 and period_ids1[0] or False
                
                # Get journal_id and position id of share company
                journal_id = tech_invoice_brw.journal_id.id
                position_id = tech_invoice_brw.position_id.id
                
                fiscal_jurnl_id = fiscal_jurnl_obj.search(cr,uid,[('journal_src_id','=',journal_id),('position_id','=',position_id)])
                if fiscal_jurnl_id: 
                     fiscal_jurnl_brw = fiscal_jurnl_obj.browse(cr,uid,fiscal_jurnl_id[0])
                     fiscal_type = fiscal_jurnl_brw.position_id.type
                     if fiscal_type == 'icb':
                        for journ in fiscal_jurnl_brw.journal_dest_id:
                            if journ.company_id.id == partner_dict[partner_id].id:
                                journal_id1 =journ.id
                partner_id1 = tech_invoice_brw.company_id.partner_id.id
                
                account_move = {
                                  'partner_id' : partner_id, 'date': to_date,
                                  'period_id': period_id, 'journal_id': journal_id,
                                  'state' : 'draft', 'company_id': company_id,
                                  }
                account_move1 = {
                                  'partner_id' : partner_id1,  'date': to_date,
                                  'period_id': period_id1,'journal_id': journal_id1,
                                  'state' : 'draft','company_id': company_id1
                                  }
                
                # Create two move for both company
                move_id = move_obj.create(cr ,uid, account_move)
                move_id1 = move_obj.create(cr ,uid, account_move1)
                break
            
            for tech_invoice_brw in tech_invoice_obj.browse(cr, uid,tech_invoice_line):
                invoice_type = tech_invoice_brw.invoice_ids.type
                for line in tech_invoice_brw.invoice_ids.invoice_line:
                    debit_amt = 0
                    credit_amt  = 0
                    if type == 'out_invoice':
                       credit_amt = line.price_subtotal*(tech_invoice_brw.percentage/100)
                    else:
                       debit_amt = line.price_subtotal*(tech_invoice_brw.percentage/100)    
                    
                    account_id = line.account_id.id
                    move_line = {
                    'journal_id': journal_id, 'period_id': period_id,
                    'name': line.name or '/',  'account_id': account_id,
                    'move_id': move_id, 'partner_id': partner_id,
                    'currency_id': currency, 'date': tech_invoice_brw.date,
                    'credit': credit_amt,'debit' : debit_amt,
                    'company_id' :company_id,
                     #'quantity': 1,
                    #'price_unit':line.price_unit,
                   # 'quantity':line.quantity,
                   # 'cost_analytic_id': voucher.cost_analytic_id and voucher.cost_analytic_id.id or False
                    }
                    
                    account_id1 = self.get_fiscal_position_id(cr, uid, position_id, line.account_id.id,company_id1,'out_invoice', context),
                    
                    move_line1 = {
                    'period_id': period_id1, 'account_id': account_id1,
                    'name': line.name or '/',
                    'move_id': move_id1,'partner_id': partner_id1,
                    'currency_id': currency,
                    'credit': debit_amt, 'debit': credit_amt,
                    'date': tech_invoice_brw.date,'company_id' :company_id1,
                    
                    }
                    
                    move_line_obj.create(cr, uid, move_line)
                    move_line_obj.create(cr, uid, move_line1)
                    total_debit_amt += credit_amt
                    total_credit_amt += debit_amt

            
            if move_id :
                if total_debit_amount > total_credit_amt:
                    debit1 = total_debit_amount - total_credit_amt
                    credit1 = 0  
                else:
                    credit1 = total_credit_amt - total_debit_amount
                    debit1 = 0
                move_line = {
                    'period_id': period_id,
                    'name': '/',
                    'move_id': move_id,'partner_id': partner_id,
                    'currency_id': currency,
                    'credit': credit1,
                    'debit': debit1,
                    'date': date,
                    'company_id' :company_id,
                 
                    }
                
                rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                if not rec_pro_id:
                            rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                if not pay_pro_id:
                            pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                move_line['account_id'] = rec_res_id
                                 
                move_line_obj.create(cr, uid, move_line)
                rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id1)+''),('company_id','=',company_id1)])
                pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id1)+''),('company_id','=',company_id1)])
                if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id1)])
                if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id1)])
                rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                rec_res_id1 = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                pay_res_id1 = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False                 
                move_line1 = {
                   # 'journal_id': tech_invoice_brw.journal_id.id,
                    'period_id': period_id1,
                    'name': '/',
                    'account_id': pay_res_id1,
                    'move_id': move_id1,
                   'partner_id': partner_id1,
                    'currency_id': currency,
                 
                    'quantity': 1,
                    'credit':debit1,
                    'debit': credit1,
                    'date': date,
                    'company_id' :company_id1,
                
                    }
                move_line_obj.create(cr, uid, move_line1)
         
              
        return True
    
    def get_fiscal_position_id(self, cr, uid, fiscal_position, account_id,company_id,type, context=None):
        fiscal_account_obj = self.pool.get('account.fiscal.position.account')
        default_account_obj = self.pool.get('account.fiscal.default.account')
        print "here",fiscal_position,account_id,company_id
        fiscal_account_id = fiscal_account_obj.search(cr,uid,[('position_id','=',fiscal_position),('account_src_id','=',account_id),('company_id','=',company_id)])        
        if fiscal_account_id:
            return fiscal_account_obj.browse(cr, uid, fiscal_account_id)[0].account_dest_id.id
        else:
            default_id = default_account_obj.search(cr,uid,[('type','=',type),('company_id','=',company_id)])
            if default_id:
                return default_account_obj.browse(cr ,uid,default_id[0]).account_id.id
            return True
    def _get_invoice_lines(self, cr, uid, invoice,company_id,percentage, context=None):
        invoice_lines = []
        for line in invoice.invoice_line:
            name = line.name
            product_id = line.product_id and line.product_id.id or False
            uos_id = line.uos_id and line.uos_id.id or False
            quantity = line.quantity
            price_unit = line.price_unit
            origin = line.origin
                
#             invoice_line_vals = self.pool.get('account.invoice.line').product_id_change(cr, uid, False, product_id, uos_id,
#                 lneine.quantity, name, context.get('invoice_type', False), context.get('invoice_partner_id', False),
#                 context.get('invoice_fiscal_position', False), price_unit, context.get('partner_address_invoice_id', False),
#                 context.get('invoice_currency_id', False), context)['value']
            invoice_line_vals ={
                'name': name,
                'origin': line.origin,
                'uos_id': uos_id,
                'product_id': product_id,
                'price_unit': line.price_unit,
                'quantity': quantity,
                'discount': line.discount,
                #'note': line.note,
               
            }
            if invoice.fiscal_type == 'icb':
                 invoice_type = invoice.type.startswith('in_') and invoice.type.replace('in_', 'out_') or invoice.type.replace('out_', 'in_')
                 invoice_line_vals['account_id'] = self.get_fiscal_position_id(cr, uid, invoice.fiscal_position.id, line.account_id.id,company_id,invoice_type, context),
            else:
                invoice_line_vals['account_id'] =line.account_id.id
                invoice_line_vals['price_unit'] = line.price_unit/(100/percentage)
            invoice_lines.append(invoice_line_vals)
        return invoice_lines
    
    def create_inter_company_invoices(self, cr, uid, ids, context=None):
        context_copy = dict(context or {})
        if isinstance(ids, (int, long)):
            ids = [ids]
        for invoice in self.browse(cr, uid, ids, context):
#             if  invoice.partner_id.partner_company_id:
             for line in invoice.customer_account_invoice_ids:
                    invoice_type = invoice.type.startswith('in_') and invoice.type.replace('in_', 'out_') or invoice.type.replace('out_', 'in_')
                    partner_id = line.partner_id.id
                    date_invoice = invoice.date_invoice
                    payment_term = invoice.payment_term.id
                    partner_bank_id = invoice.partner_bank_id.id
                    company_id = line.company_id.id
                    currency_id = invoice.currency_id.id
                    journal_id = line.journal_id.id
                    fiscal_position = line.position_id and line.position_id.id or False
                    fiscal_type = False
                    customer_account_invoice_ids = False
                    if line.position_id:
                        fiscal_type = line.position_id.type
                        customer_account_invoice_ids = self.onchange_journal_id(cr, uid, False, \
                                                                                journal_id,fiscal_position,fiscal_type,partner_id,)['value']['customer_account_invoice_ids']
                        
                        print "customer_account_invoice_ids",customer_account_invoice_ids
                    invoice_vals = self.onchange_partner_id(cr, uid, False, invoice_type, partner_id, date_invoice, \
                                                        payment_term, partner_bank_id, company_id)['value']
                    print "invoice_vals",invoice_vals
                    context_copy.update({
                        'company_id': company_id,
                        'invoice_type': invoice_type,
                        'invoice_partner_id': partner_id,
                      #  'invoice_fiscal_position': invoice_vals.get('fiscal_position', False),
                        'invoice_currency_id': currency_id,
                        'partner_address_invoice_id': invoice_vals.get('address_invoice_id', False),
                    })
                    invoice_vals.update({
                        'origin': invoice.origin,
                        'original_invoice_id': invoice.id,
                        'type': invoice_type,
                        'reference': invoice.number,
                        'date_invoice': date_invoice,
                        'date_due': invoice.date_due,
                        'partner_id': partner_id,
                        'currency_id': currency_id,
                        'journal_id': journal_id,
                        'company_id': company_id,
                        'fiscal_type' : fiscal_type,
                        'fiscal_position': fiscal_position,
                        'user_id': False,
                        'invoice_line': map(lambda x: (0, 0, x), self._get_invoice_lines(cr, uid, invoice, company_id,line.percentage, context_copy)),
                        'check_total': invoice.amount_total,
                        'customer_account_invoice_ids': customer_account_invoice_ids
                    })
                    
                    print "hhhhh"
                    invoice_id = self.create(cr, 1, invoice_vals, context) #To bypass access and record rules
                    # if both invoice want to validate at a time then remove if condition
#                     if 1 ==1:
                    if invoice_vals['fiscal_position']:
                         wf_service = netsvc.LocalService("workflow")
                         wf_service.trg_validate(uid, 'account.invoice',
                                        invoice_id, 'invoice_open', cr)
                       
        return True
    
    def action_number(self, cr, uid, ids, context=None):
        """Override this original method to create invoice for the supplier/customer company"""
        res = super(account_invoice, self).action_number(cr, uid, ids, context)
        fiscal_type = self.browse(cr, uid,ids)[0].fiscal_type
        if fiscal_type == 'icb' or fiscal_type == 'T':
             self.create_inter_company_invoices(cr, uid, ids, context)
        return res
    
 #################################################################################################################
     
    def onchange_journal_id(self, cr, uid, ids, journal_id=False,position_id=False,fiscal_type=False,partner_id=False, context=None):
        result = {}
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            company_id = journal.company_id.id
            result = {'value': {
                    'currency_id': currency_id,
                    'company_id': company_id,
                    }
                }
            company_id2 = journal.company_id.id
            lst = []
            
            if position_id:
                print "here"
                fiscal_jurnl_obj = self.pool.get('account.fiscal.journal')
                fiscal_obj = self.pool.get('account.fiscal.position')
                fiscal_jurnl_id = fiscal_jurnl_obj.search(cr,uid,[('journal_src_id','=',journal_id),('position_id','=',position_id)])
                print "fiscal_jurnl_id",fiscal_jurnl_id
                position_id1 = False
                if fiscal_jurnl_id: 
                     fiscal_jurnl_brw = fiscal_jurnl_obj.browse(cr,uid,fiscal_jurnl_id[0])
                     print "fiscal_jurnl_brw",fiscal_jurnl_brw,fiscal_jurnl_brw.position_id.name
                     fiscal_type = fiscal_jurnl_brw.position_id.type
                     if fiscal_type == 'icb':
                        comp_id = self.pool.get('res.company').search(cr, uid, [('partner_id','=', partner_id)])  
                        for journ in fiscal_jurnl_brw.journal_dest_id:
                            print "here"   
                            if journ.company_id.id == comp_id[0]:
                                part_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.partner_id.id
                                if journ.company_id.is_shared_company:
                                    print "Hereeeeee"
                                    position_id1 = fiscal_obj.search(cr,uid,[('company_id','=',journ.company_id.id),('type','=','ss')])  
                                    if position_id1:
                                        position_id1 = position_id1[0]
                                lst.append((0,0,{'journal_id':journ.id,'company_id':comp_id[0],'partner_id' : part_id,'percentage': 100,'position_id':position_id1})),
                                
                     else:                                              
                             for comp in fiscal_jurnl_brw.company_ids :
                                  if comp.is_shared_company:
                                      type = 'ss'
                                  else:
                                      type = 'icb'
                                     
                                  position_id1 = fiscal_obj.search(cr,uid,[('company_id','=',company_id),('type','=','icb')])      
                                  if position_id1:
                                          position_id1 = position_id1[0]  
                                      
                                  lst.append((0,0,{'journal_id':fiscal_jurnl_brw.inter_journal_dest_id.id,'company_id':company_id,'position_id': position_id1,'partner_id':comp.partner_id.id,'percentage':100/len(fiscal_jurnl_brw.company_ids)})),
                     result['value']['customer_account_invoice_ids'] = lst 
                     result['value']['fiscal_type'] =fiscal_type                             
        return result 
 
   
        
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        lst=[]
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False
        fiscal_type = ''
        is_intragroup_company = False
        opt = [('uid', str(uid))]
        user_obj = self.pool.get('res.users').browse(cr, uid, uid)    
        if partner_id:
            currnet_cmpny=self.pool.get('res.users').browse(cr,uid,uid).company_id
            print'======current_company====',currnet_cmpny
            opt.insert(0, ('id', partner_id))
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            comp_id=self.pool.get('res.company').search(cr,uid,[('name','=',p.name)])
            acc_fiscal_posi=self.pool.get('account.fiscal.position')
            if company_id:

                
                if (p.property_account_receivable.company_id and (p.property_account_receivable.company_id.id != company_id)) and (p.property_account_payable.company_id and (p.property_account_payable.company_id.id != company_id)):

                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
                partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            else:
                acc_id = p.property_account_payable.id
                partner_payment_term = p.property_supplier_payment_term and p.property_supplier_payment_term.id or False
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id

            if p.is_intragroup_company ==True:
                value1=True

               
            
            print "user_obj.company_id.is_shared_company",user_obj.company_id.is_shared_company
            if  p.is_intragroup_company:
                  fiscal_type  = 'icb'
                  is_intragroup_company = True
            elif user_obj.company_id.is_shared_company:
                fiscal_type  = 'ss'

                
            elif user_obj.company_id.technology_company:
                fiscal_type  = 'T'
            fiscal_id =  acc_fiscal_posi.search(cr,uid, [('type','=',fiscal_type),('company_id','=',user_obj.company_id.id)])
            if fiscal_id:
                      fiscal_position = fiscal_id[0]
                   
        result = {'value': {
            'is_intragroup_invoice_company':is_intragroup_company,
            'fiscal_type' :fiscal_type,
            'account_id': acc_id,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position
            }
        }

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr, uid, ids, partner_payment_term, date_invoice)
                result['value'].update(to_update['value'])
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        return result   
             
class account_fiscal_position_account(osv.osv):
    _name='account.fiscal.position.account'
    _inherit='account.fiscal.position.account'    
    _columns={
               'company_id' : fields.related('account_dest_id','company_id',type='many2one',relation='res.company',string='Company',readonly=True,store=True),
              
              }
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        