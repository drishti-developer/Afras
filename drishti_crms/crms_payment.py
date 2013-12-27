from openerp.osv import fields, osv
#from openerp.tools.translate import _
import datetime
from openerp import netsvc

class crms_payment(osv.osv):
    _name = 'crms.payment'
    _columns = {
   'name':fields.char('Name',size=64),
   'crms_id':fields.integer('Crms Payment Id'),
   'partner_id':fields.many2one('res.partner','Customer Name',required=True),
   'vehicle_id':fields.many2one('fleet.vehicle','Vehicle'),
   'car_type_id':fields.many2one('fleet.type','Car Type'),
   'model_id':fields.many2one('fleet.vehicle.model','Vehicle Model'),
   'crms_booking_id':fields.integer('Crms Booking Id'),
   'rental_from_date':fields.datetime('Rental From Date'),
   'rental_to_date':fields.datetime('Rental To Date'),
   'no_of_days':fields.integer('No Of Days'),
   'no_of_hours':fields.integer('No Of Hours'),
   'pickup_branch_id':fields.many2one('sale.shop','Pickup Branch'),
   'drop_branch_id':fields.many2one('sale.shop','Drop Branch'),
   'booking_branch_id':fields.many2one('sale.shop','Booking Branch'),
   'amount_paid':fields.float('Amount Paid by Customer'),
   'amount_receive_date':fields.datetime('Amount Receive Date'),
   'rental_amount':fields.float('Rental Amount'),
   'amount_returned':fields.float('Amount returned to the Customer'),
   'amount_returned_date':fields.datetime('Amount returned date to customer'),
   'holding_amount':fields.float('Holding Amount'),
   'advance_amount':fields.float('Advanced Amount'),
   'balance_due_amount':fields.float('Balance Due Amount'),
   'admin_expenses':fields.float('Admin Expenses'),
   'damage_charges':fields.float('Car Damage Charges'),
   'traffic_violation_charges':fields.float('Traffic Violation charges'),
   'other_charges':fields.float('Other charges'),
   'extra_hour_charges':fields.float('Extra Hour charges'),
   'extra_km_charges':fields.float('Extra Kilometer charges'),
   'additional_day_charges':fields.float('Additional Day charges'),
   'payment_type':fields.selection([('Cash','Cash'),('Card','Card'),('Span','Span')],'Payment Type'),
   'remaining_amount':fields.float('Remaining Amount'),
   'per_day_amount':fields.float('Per Day Amount'),
   'status':fields.selection([('Active','Active'),('Awaiting Payment','Awaiting Payment'),('Closed','Closed')],'Status'),
   'property_cash_journal': fields.property(
        'account.journal',
        type='many2one',
        relation='account.journal',
        string="Cash Journal",
        view_load=True,
        help="Cash Journal",
        ),
   'property_bank_journal': fields.property(
        'account.journal',
        type='many2one',
        relation='account.journal',
        string="Bank Journal",
        view_load=True,
        help="Bank Journal",
        ),
   'property_sale_journal': fields.property(
        'account.journal',
        type='many2one',
        relation='account.journal',
        string="Sale Journal",
        view_load=True,
        help="Sale Journal",
        ),
   'property_advance_account': fields.property(
        'account.account',
        type='many2one',
        relation='account.account',
        string="Advance Account",
        view_load=True,
        help=" Advance Account",
        ),
   'property_retail_account': fields.property(
        'account.account',
        type='many2one',
        relation='account.account',
        string="Retail Account",
        view_load=True,
        help=" Retail Account",
        ),
   'property_revenue_account': fields.property(
        'account.account',
        type='many2one',
        relation='account.account',
        string="Revenue Account",
        view_load=True,
        help=" Revenue Account",
        ),
   'property_account_payable': fields.property(
        'account.account',
        type='many2one',
        relation='account.account',
        string="Account Payable",
        view_load=True,
        domain="[('type', '=', 'payable')]",
        help="This account will be used instead of the default one as the payable account for the current partner",
        required=True),
    'line_ids': fields.one2many('account.move.line','crms_payment_id',string="Lines"),
    }
    
    def create(self, cr, uid, data, context=None):
        
        if context is None:
            context = {}
            
        payment_id = super(crms_payment, self).create(cr, uid, data, context=context)
        crms_payment_brw = self.browse(cr, uid, payment_id)
        if crms_payment_brw.amount_paid > 0:
            period_obj = self.pool.get('account.period')
            voucher_obj = self.pool.get('account.voucher')
            
            ctx = context.copy()
            ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
            period_ids = period_obj.find(cr, uid, crms_payment_brw.amount_receive_date, context=ctx)
            
            if crms_payment_brw.payment_type == 'Cash':
                journal_id = crms_payment_brw.property_cash_journal.id
                account_id = crms_payment_brw.property_cash_journal.default_credit_account_id.id
            elif crms_payment_brw.payment_type == 'Card':
                journal_id = crms_payment_brw.property_bank_journal.id
                account_id = crms_payment_brw.property_bank_journal.default_credit_account_id.id
            
            voucher_id = voucher_obj.create(cr, uid, {
             'partner_id': crms_payment_brw.partner_id.id,
             'journal_id': journal_id,
             'type' : 'receipt',
             'cost_analytic_id' : crms_payment_brw.pickup_branch_id.project_id.id,
             'company_id' : crms_payment_brw.pickup_branch_id.company_id.id,
             'account_id' : account_id,
             'date': crms_payment_brw.amount_receive_date,
             'period_id': period_ids and period_ids[0] or False,
             'amount':crms_payment_brw.amount_paid,
             'line_ids': [(0,0,{'account_id': crms_payment_brw.property_advance_account.id,'amount': crms_payment_brw.amount_paid,'type': 'cr',})]
             })
            
            netsvc.LocalService("workflow").trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
        
        return payment_id
    
    def write(self, cr, uid, ids, vals, context=None):
        super(crms_payment, self).write(cr, uid, ids, vals, context=context)
        
        return True
    
    def create_account_voucher_enries(self, cr, uid, ids, context=None):
        
        # CRMS Payment
        if context is None:
            context = {}
            
        crms_payment_obj = self.pool.get('crms.payment')
        period_obj = self.pool.get('account.period')
        voucher_obj = self.pool.get('account.voucher')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        voucher_line_obj = self.pool.get('account.voucher.line')
        
        if not ids:
            ids = crms_payment_obj.search(cr, uid, [('status','=','Active')])
        
        for crms_payment_brw in crms_payment_obj.browse(cr ,uid, ids):
            date = datetime.datetime.today()
            ctx = context.copy()
            ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
            period_ids1 = period_obj.find(cr, uid, date, context=ctx)
            # Create Journal Entries for revenue
            
            
            move_dic = {
            'journal_id': crms_payment_brw.property_sale_journal.id,
            'date' : date,
            'period_id': False,
            'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
            'company_id':crms_payment_brw.property_sale_journal.company_id.id,
            'period_id':period_ids1 and period_ids1[0] or False,
            'crms_payment_id':crms_payment_brw.id,
            }
            
            move_id = move_obj.create(cr,uid, move_dic)
            remaining_amount =crms_payment_brw.remaining_amount
            per_day_amt =crms_payment_brw.per_day_amount
            move_line_dic = {
            'journal_id': crms_payment_brw.property_sale_journal.id,
            'date' : date,
            'period_id': period_ids1 and period_ids1[0] or False,
            'partner_id':crms_payment_brw.partner_id.id,
            'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
            'company_id':crms_payment_brw.property_sale_journal.company_id.id,
            'name': 'Car rent',
            'debit': per_day_amt,
            'account_id': crms_payment_brw.property_advance_account.id,
            'move_id':move_id,
            }
            if remaining_amount < per_day_amt:
                if remaining_amount >0:
                    move_line_dic['debit']= remaining_amount
                    move_line_obj.create(cr, uid, move_line_dic)
                    move_line_dic['debit'] = per_day_amt- remaining_amount 
                    move_line_dic['account_id'] = crms_payment_brw.partner_id.property_account_receivable.id,
                    move_line_obj.create(cr, uid, move_line_dic) 
                    remaining_amount =0
                else:
                    move_line_dic['debit'] = per_day_amt 
                    move_line_dic['account_id'] = crms_payment_brw.partner_id.property_account_receivable.id,
                    move_line_obj.create(cr, uid, move_line_dic) 
            else:           
                move_line_obj.create(cr, uid, move_line_dic)
                
            move_line_dic1 = {
            'journal_id': crms_payment_brw.property_sale_journal.id,
            'date' : date,
            'partner_id':crms_payment_brw.partner_id.id,
            'period_id': period_ids1 and period_ids1[0] or False,
            'analytic_account_id':crms_payment_brw.vehicle_id.analytic_id.id,
            'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
            'company_id':crms_payment_brw.property_sale_journal.company_id.id,
            'name': 'Car rent',
            'credit': per_day_amt,
            'account_id': crms_payment_brw.property_revenue_account.id,
            'move_id' : move_id,
            }
            move_line_obj.create(cr, uid, move_line_dic1)
            
        
        return True

crms_payment()
        