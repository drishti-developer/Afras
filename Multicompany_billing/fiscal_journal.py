from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
class account_fiscal_journal(osv.osv):
    _name = 'account.fiscal.journal'
    _columns = {
        'position_id': fields.many2one('account.fiscal.position', 'Fiscal Position', required=True, ondelete='cascade'),
        'journal_src_id': fields.many2one('account.journal', 'Journal Source', required=True, ondelete='restrict'),
        'journal_dest_id': fields.many2many('account.journal', 'account_fiscal_journal_rel','name','code','Journal Destination', required=True, ondelete='restrict'),
        'inter_journal_dest_id': fields.many2one('account.journal','Journal Destination',required=True, ondelete='restrict'),

        }
account_fiscal_journal()

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
              'percentage':fields.char('Percentage'),
              'company_id':fields.many2one('res.company','Company Id'),
              'invoice_ids':fields.many2one('account.invoice','Account Invoice'),
              'partner_id':fields.many2one('res.partner','Partner Id')
              }
class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
              'customer_account_invoice_ids':fields.one2many('supplier.account.invoice','invoice_ids','Journal'),
              'is_intragroup_invoice_company': fields.boolean('Is an intra-group company'),
              }
    
    #########################################################################################################
    def get_fiscal_position_id(self, cr, uid, fiscal_position, account_id,company_id, context=None):
        fiscal_account_obj = self.pool.get('account.fiscal.position.account')
        
        fiscal_account_id = fiscal_account_obj.search(cr,uid,[('position_id','=',fiscal_position),('account_src_id','=',account_id),('company_id','=',company_id)])        
        if fiscal_account_id:
            return fiscal_account_obj.browse(cr, uid, fiscal_account_id).account_dest_id.id
        else:
            print "raise warning"
            return true
    def _get_invoice_lines(self, cr, uid, invoice,company_id, context=None):
        invoice_lines = []
        for line in invoice.invoice_line:
            name = line.name
            product_id = line.product_id and line.product_id.id or False
            uos_id = line.uos_id and line.uos_id.id or False
            quantity = line.quantity
            price_unit = line.price_unit
            origin = line.origin
                
#             invoice_line_vals = self.pool.get('account.invoice.line').product_id_change(cr, uid, False, product_id, uos_id,
#                 line.quantity, name, context.get('invoice_type', False), context.get('invoice_partner_id', False),
#                 context.get('invoice_fiscal_position', False), price_unit, context.get('partner_address_invoice_id', False),
#                 context.get('invoice_currency_id', False), context)['value']
            invoice_line_vals.update({
                'name': name,
                'origin': line.origin,
                'uos_id': uos_id,
                'product_id': product_id,
                'price_unit': line.price_unit,
                'quantity': quantity,
                'discount': line.discount,
                'note': line.note,
                'account_id': self.get_fiscal_position_id(cr, uid, invoice.fiscal_position, line.account_id,company_id, context),
            })
            invoice_lines.append(invoice_line_vals)
        return invoice_lines
    
    def create_inter_company_invoices(self, cr, uid, ids, context=None):
        context_copy = dict(context or {})
        if isinstance(ids, (int, long)):
            ids = [ids]
        for invoice in self.browse(cr, uid, ids, context):
            if  invoice.partner_id.partner_company_id:
                for line in invoice.customer_account_invoice_ids:
                    invoice_type = invoice.type.startswith('in_') and invoice.type.replace('in_', 'out_') or invoice.type.replace('out_', 'in_')
                    partner_id = invoice.company_id.partner_id.id
                    date_invoice = invoice.date_invoice
                    payment_term = invoice.payment_term.id
                    partner_bank_id = invoice.partner_bank_id.id
                    company_id = line.company_id.id
                    currency_id = invoice.currency_id.id
                    journal_id = line.journal_id.id
                    invoice_vals = self.onchange_partner_id(cr, uid, False, invoice_type, partner_id, date_invoice, \
                                                        payment_term, partner_bank_id, company_id)['value']
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
                        'user_id': False,
                        'invoice_line': map(lambda x: (0, 0, x), self._get_invoice_lines(cr, uid, invoice,line.company.id, context_copy)),
                        'check_total': invoice.amount_total,
                    })
                    self.create(cr, 1, invoice_vals, context) #To bypass access and record rules
        return True
    
    def action_number(self, cr, uid, ids, context=None):
        """Override this original method to create invoice for the supplier/customer company"""
        res = super(account_invoice, self).action_number(cr, uid, ids, context)
        
        self.create_inter_company_invoices(cr, uid, ids, context)
        return res
    
 #################################################################################################################
    def onchange_fiscal_position(self,cr,uid,ids,fiscal_position,partner_id,context=None):
            print'========fiscial_position======',ids,uid,fiscal_position
            res={}
            lst=[]
            info=''
            opt = [('uid', str(uid))]
            print'==pkoklkfvkmklfvmklamvkmal;mm'
            if partner_id:
                opt.insert(0, ('id', partner_id))
                p = self.pool.get('res.partner').browse(cr, uid, partner_id)
                acc_fiscal_posi=self.pool.get('account.fiscal.position')
                comp_id=self.pool.get('res.company').search(cr,uid,[('name','=',p.name)])
                customer_account_inv=self.pool.get('supplier.account.invoice')
                obj=self.browse(cr,uid,fiscal_position)
                print'=======obj=====',obj
                account_fiscal_company=acc_fiscal_posi.search(cr,uid,[('company_id','in',comp_id),('id','=',fiscal_position)])
                acc_fiscal_position=acc_fiscal_posi.search(cr,uid,[('type','=','icb'),('company_id','in',comp_id),('id','=',fiscal_position)])
                if acc_fiscal_position:
                    acc_fiscal_journal=acc_fiscal_posi.browse(cr,uid,acc_fiscal_position[0])
                    if acc_fiscal_journal.account_ids:
                       for acc in acc_fiscal_journal.account_ids:
                            if acc_fiscal_journal.journal_ids:
                                    for val in acc_fiscal_journal.journal_ids:
                                        lst.append((0,0,{'journal_id':val.inter_journal_dest_id.id,'account_id':acc.account_dest_id.id,'company_id':comp_id[0],'partner_id':partner_id})),
                    res ={
                          'customer_account_invoice_ids':lst
                        } 
                elif account_fiscal_company:
                        acc_fiscal_journal=acc_fiscal_posi.browse(cr,uid,account_fiscal_company[0])
                        if acc_fiscal_journal.account_ids:
                           for acc in acc_fiscal_journal.account_ids:
                                if acc_fiscal_journal.journal_ids:
                                        for val in acc_fiscal_journal.journal_ids:
                                            for jou in val.journal_dest_id:
                                                lst.append((0,0,{'journal_id':jou.id,'company_id':comp_id[0],'account_id':acc.account_dest_id.id})), 
                        res ={
                                'customer_account_invoice_ids':lst
                             } 
            return {'value': res}
        
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        lst=[]
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False

        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            comp_id=self.pool.get('res.company').search(cr,uid,[('name','=',p.name)])
            acc_fiscal_posi=self.pool.get('account.fiscal.position')
            if company_id:
                acc_fiscal_position=acc_fiscal_posi.search(cr,uid,[('type','=','icb'),('company_id','in',comp_id)])
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
            if acc_fiscal_position and p.is_intragroup_company:
                value1=True
            else:
                value1=False
                
        result = {'value': {
            'is_intragroup_invoice_company':value1,
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        