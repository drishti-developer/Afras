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
            currnet_cmpny=self.pool.get('res.users').browse(cr,uid,uid).company_id
            print'======current_company====',currnet_cmpny
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
            if p.is_intragroup_company ==True:
                value1=True
                
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
              'company_id1':fields.many2one('res.company','Company Id'),
              }
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        