from openerp.osv import fields, osv
#from openerp.tools.translate import _
import datetime
from dateutil.relativedelta import relativedelta
from openerp import netsvc

class crms_payment(osv.osv):
    _name = 'crms.payment'
    _rec_name = 'crms_id'
    
    def _get_intermediate_payment_id(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        
        for record in ids:
            value_id = False
            cr.execute('select crms_id from crms_payment_intermediatepayment_history where booking_id=%s order by id DESC',(record,))
            intermediate_id = cr.fetchone()
            if intermediate_id:
                value_id = intermediate_id
                    
            res[record.id] = value_id
        return res
    
    _columns = {
    'name':fields.char('Name',size=64),
    'crms_id':fields.integer('CRMS Booking ID', required=True, readonly=True),
    'partner_id':fields.many2one('res.partner','Customer Name', required=True),
    'vehicle_id':fields.many2one('fleet.vehicle','Vehicle', required=True),
    'car_type_id':fields.many2one('fleet.type','Car Type'),
    'model_id':fields.many2one('fleet.vehicle.model','Vehicle Model'),
    'crms_payment_id':fields.integer('CRMS Payment ID'),
    'rental_from_date':fields.datetime('Rental From', required=True),
    'rental_to_date':fields.datetime('Rental To', required=True),
    'no_of_days':fields.integer('No Of Days'),
    'no_of_hours':fields.integer('No Of Hours'),
    'pickup_branch_id':fields.many2one('sale.shop','Pickup Branch', required=True),
    'drop_branch_id':fields.many2one('sale.shop','Drop Branch'),
    'booking_branch_id':fields.many2one('sale.shop','Booking Branch'),
    'amount_paid':fields.float('Amount Paid', required=True),
    'amount_receive_date':fields.datetime('Amount Receive Date', required=True),
    'rental_amount':fields.float('Rental Amount'),
    'amount_returned':fields.float('Amount Returned'),
    'amount_returned_date':fields.datetime('Amount Returned Date'),
    'holding_amount':fields.float('Holding Amount'),
    'advance_amount':fields.float('Advanced Amount'),
    'balance_due_amount':fields.float('Balance Due Amount'),
    'admin_expenses':fields.float('Admin Expenses'),
    'damage_charges':fields.float('Car Damage Charges'),
    'traffic_violation_charges':fields.float('Traffic Violation charges'),
    'other_charges':fields.float('Other charges'),
    'extra_hour_charges':fields.float('Extra Hour charges'),
    'extra_km_charges':fields.float('Extra Kilometer charges'),
    'additional_driver_charges':fields.float('Additional Driver charges'),
    'payment_type':fields.selection([('Cash','Cash'),('Card','Card'),('Span','Span')],'Payment Type', required=True),
    'remaining_amount':fields.float('Remaining Amount'),
    'per_day_amount':fields.float('Per Day Amount', required=True),
    'state':fields.selection([('Active','Active'),('Awaiting for outgoing check','Awaiting for outgoing check'),('Payment Processing','Payment Processing'),('Replaced','Replaced'),('Changed','Changed'),('Closed','Closed')], string='State'),
    'discount':fields.float(string="Discount(%)"),
    'rental_extension':fields.selection([('Yes','Yes'),('No','No')],string="Rental Extension",readonly=True),
    'property_cash_journal': fields.property('account.journal', type='many2one', relation='account.journal', string="Cash Journal", view_load=True, help="Cash Journal",),
    'property_bank_journal': fields.property('account.journal', type='many2one', relation='account.journal', string="Bank Journal", view_load=True, help="Bank Journal",),
    'property_sale_journal': fields.property('account.journal', type='many2one', relation='account.journal', string="Sale Journal", view_load=True, help="Sale Journal",),
    'property_advance_account': fields.property('account.account', type='many2one', relation='account.account', string="Advance Account", view_load=True, help=" Advance Account",),
    'property_retail_account': fields.property('account.account', type='many2one', relation='account.account', string="Retail Account", view_load=True, help=" Retail Account",),
    'property_revenue_account': fields.property('account.account', type='many2one', relation='account.account', string="Revenue Account", view_load=True, help=" Revenue Account",),
    'property_account_payable': fields.property('account.account', type='many2one', relation='account.account', string="Account Payable", view_load=True, domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current Customer", required=True),
    'property_discount_account': fields.property('account.account', type='many2one', relation='account.account', string="Discount Account", view_load=True, help=" Discount Account",),
    'property_extra_hours_account': fields.property('account.account', type='many2one', relation='account.account', string="Extra Hours Account", view_load=True, help="Extra Hours Account",),
    'property_extra_kms_account': fields.property('account.account', type='many2one', relation='account.account', string="Extra KMs Account", view_load=True, help="Extra KMs Account",),
    'property_other_charges_account': fields.property('account.account', type='many2one', relation='account.account', string="Other Charges Account", view_load=True, help="Other Charges Account",),
    'property_car_damages_account': fields.property('account.account', type='many2one', relation='account.account', string="Car Damages Account", view_load=True, help=" Car Damages Account",),
    'property_admin_charges_account': fields.property('account.account', type='many2one', relation='account.account', string="Admin Expense Account", view_load=True, help="Admin Expense Account",),
    'property_traffic_violation_charges_account': fields.property('account.account', type='many2one', relation='account.account', string="Traffic Violation Account", view_load=True, help="Traffic Violation Account",),
    'property_driver_charges_account': fields.property('account.account', type='many2one', relation='account.account', string="Extra Driver Charges Account", view_load=True, help=" Extra Driver Charges Account",),
    'last_expense_date':fields.datetime(string="Last Expense Date"),
    'line_ids': fields.one2many('account.move.line','crms_payment_id',string="Lines"),
    'amount_history_ids': fields.one2many('crms.payment.intermediatepayment.history','booking_id',string="Amount Paid History"),
    'discount_history_ids': fields.one2many('crms.payment.discount.history','booking_id',string="Discount History"),
    'payment_id':fields.function(_get_intermediate_payment_id, type="many2one", relation="crms.payment.intermediatepayment.history", string='Latest Payment ID'),
    'total_amount_paid':fields.float('Total Amount Paid'),
    'revenue_days':fields.integer('Revenue Days'),
    'daily_revenue_ids': fields.one2many('crms.daily.revenue','booking_id',string="Amount Paid History"),
    }
    
    _sql_constraints = [
        ('crms_booking_id_uniq', 'unique(crms_id)', 'CRMS Booking Id already exist!'),
    ]
    
    _defaults = {
    'state':'Active',
    'revenue_days':0,
                 }
    
    def create(self, cr, uid, data, context=None):
        
        if context is None:
            context = {}
            
        data['last_expense_date'] = data.get('rental_from_date')
        data['amount_history_ids'] = [(0,0,{'date':data.get('amount_receive_date'),'amount':data.get('amount_paid'),'payment_type':data.get('payment_type'),'crms_id':data.get('crms_payment_id'),'voucher_amount':data.get('amount_paid')})]
        data['total_amount_paid'] = data.get('amount_paid')   
        if data.get('admin_expenses',False):context['admin_expenses'] = data.get('admin_expenses')
            
        return super(crms_payment, self).create(cr, uid, data, context=context)
    
    def write(self, cr, uid, ids, vals, context={}):
        #print vals,context
        #date = datetime.datetime.today()
        crms_payment_brw = self.browse(cr, uid, ids[0])
        intermediate_pool = self.pool.get('crms.payment.intermediatepayment.history')
        
        if crms_payment_brw.state == 'Closed' : return True
        
        period_pool = self.pool.get('account.period')
        voucher_pool = self.pool.get('account.voucher')
        voucher_amount = False
        #Check whether is a new discount is applied or not.
        if vals.get('discount',False) and vals.get('discount_date',False):
            self.pool.get('crms.payment.discount.history').create(cr, uid, {'date':vals.get('discount_date'), 'booking_id':ids[0], 'discount':vals.get('discount')},context)
        
        if vals.get('state') and (vals.get('state') == 'Closed' or vals.get('state') == 'Payment Processing') and crms_payment_brw.state in ['Active']:
            
            context['no_of_days'] = vals.get('no_of_days',0)
            #self.create_account_voucher_entries(cr, uid, ids, context)
            crms_payment_brw = self.browse(cr, uid, ids[0])
            
            if vals.get('rental_to_date',False):
                rental_to_date = vals.get('rental_to_date')
            else:
                rental_to_date = crms_payment_brw.rental_to_date
            
            rental_to_date = rental_to_date[:10]
            ctx = context.copy()
            ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
            period_ids = period_pool.find(cr, uid, rental_to_date, context=ctx)
            remaining_amount = crms_payment_brw.remaining_amount
            paid_amount = 0.0
            account_id = False
            
            if vals.get('payment_type',False) and vals.get('payment_type') == 'Cash':
                journal_id = crms_payment_brw.property_cash_journal.id
                account_id = crms_payment_brw.property_cash_journal.default_credit_account_id.id
            elif vals.get('payment_type',False) and vals.get('payment_type') in ['Span','Card']:
                journal_id = crms_payment_brw.property_bank_journal.id
                account_id = crms_payment_brw.property_bank_journal.default_credit_account_id.id
            else:
                account_id = crms_payment_brw.property_retail_account.id
            
            if vals.get('amount_returned',False) and float(vals.get('amount_returned',0.0)) > 0:
                intermediate_pool.create(cr, uid, {'date': datetime.datetime.today(), 
                                                   'amount': vals.get('amount_returned',0.0), 
                                                   'payment_type':'Cash',
                                                   'booking_id':ids[0], 
                                                   'crms_id':False,
                                                   'voucher_amount':float(vals.get('amount_returned',0.0))*-1}) 
                
                remaining_amount = remaining_amount - float(vals.get('amount_returned'))
                
            elif vals.get('amount_paid',False):
                
                paid_amount = float(vals.get('amount_paid')) - float(vals.get('admin_expenses',0.0))
                
                
#             if float(vals.get('admin_expenses',0.0)) > 0:
#                 remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Admin Expenses Charges',crms_payment_brw, float(vals.get('admin_expenses')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_admin_charges_account.id, rental_to_date, account_id)
            
            if float(vals.get('extra_hour_charges',0.0)) > 0:
                remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Extra Hours Charges', crms_payment_brw, float(vals.get('extra_hour_charges')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_extra_hours_account.id, rental_to_date, account_id)
                
            if float(vals.get('extra_km_charges',0.0)) > 0:
                remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Extra KM Charges', crms_payment_brw, float(vals.get('extra_km_charges')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_extra_kms_account.id, rental_to_date, account_id)
                
            if float(vals.get('other_charges',0.0)) > 0:
                remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Other Charges', crms_payment_brw, float(vals.get('other_charges')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_other_charges_account.id, rental_to_date, account_id)
                
            if float(vals.get('damage_charges',0.0)) > 0:
                remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Damage Charges', crms_payment_brw, float(vals.get('damage_charges')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_car_damages_account.id, rental_to_date, account_id)
                
            if float(vals.get('traffic_violation_charges',0.0)) > 0:
                remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Traffic Violation Charges', crms_payment_brw, float(vals.get('traffic_violation_charges')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_traffic_violation_charges_account.id, rental_to_date, account_id)
            
            if float(vals.get('additional_driver_charges',0.0)) > 0:
                remaining_amount, paid_amount = self.create_closed_entries(cr, uid, 'Additional Driver Charges', crms_payment_brw, float(vals.get('additional_driver_charges')), remaining_amount, paid_amount, period_ids, crms_payment_brw.property_driver_charges_account.id, rental_to_date, account_id)
                
            
            voucher_amount = paid_amount + float(vals.get('admin_expenses',0.0))
            
            cr.execute('update crms_payment set remaining_amount=%s where id=%s',(paid_amount + remaining_amount,ids[0]))
            
        #Check whether Amount is paid by Customer or not.
        if vals.get('amount_paid') and float(vals.get('amount_paid',0.0)) > 0.0 and vals.get('crms_payment_id',False) and vals.get('payment_type',False) and vals.get('amount_receive_date',False):
            
            intermediate_ids = intermediate_pool.search(cr, uid, [('crms_id','=',vals.get('crms_payment_id'))])
            if not intermediate_ids:
                vals['total_amount_paid'] = crms_payment_brw.total_amount_paid + float(vals.get('amount_paid'))
                if not voucher_amount:
                    voucher_amount = float(vals.get('amount_paid',0.0))
                if vals.get('admin_expenses',False) : context['admin_expenses'] = vals.get('admin_expenses')
                intermediate_pool.create(cr, uid, {'date':vals.get('amount_receive_date'), 'amount': vals.get('amount_paid'), 'payment_type':vals.get('payment_type'), 'booking_id':ids[0], 'crms_id':vals.get('crms_payment_id'),'admin_expenses':vals.get('admin_expenses',0.0),'voucher_amount':voucher_amount})
#             else:
#                 vals.pop('amount_paid')
#                 vals.pop('payment_type')
#                 vals.pop('amount_receive_date')   
            
        
        return super(crms_payment, self).write(cr, uid, ids, vals, context=context)
    
    def create_closed_entries(self, cr, uid, charge_name, crms_payment_brw, other_amount, remaining_amount, paid_amount, period_ids, other_amount_account_id, rental_to_date, other_account_id):
        
        # Credit Move Line        
        lines = [(0,0,{
        'journal_id': crms_payment_brw.property_sale_journal.id,
        'date' : rental_to_date,
        'partner_id':crms_payment_brw.partner_id.id,
        'period_id': period_ids and period_ids[0] or False,
        'analytic_account_id':crms_payment_brw.vehicle_id.analytic_id.id,
        'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
        'company_id':crms_payment_brw.property_sale_journal.company_id.id,
        'name': charge_name,
        'credit': other_amount,
        'account_id': other_amount_account_id,
        })]
        
        # Debit Move Line
        move_line_2 = {
        'journal_id': crms_payment_brw.property_sale_journal.id,
        'date' : rental_to_date,
        'partner_id':crms_payment_brw.partner_id.id,
        'period_id': period_ids and period_ids[0] or False,
        'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
        'company_id':crms_payment_brw.property_sale_journal.company_id.id,
        'name': charge_name,
        }
        
        if remaining_amount > 0:
            if remaining_amount >= other_amount:
                move_line_2['debit'] = other_amount
                move_line_2['account_id'] = crms_payment_brw.property_advance_account.id
                lines.append((0,0,move_line_2))
                remaining_amount = remaining_amount - other_amount
                
            elif paid_amount > 0 and (paid_amount+remaining_amount) > other_amount:
                move_line_3 = move_line_2.copy()
                move_line_2['debit'] = remaining_amount
                move_line_2['account_id'] = crms_payment_brw.property_advance_account.id
                lines.append((0,0,move_line_2))
                move_line_3['debit'] = other_amount - remaining_amount
                move_line_3['account_id'] = other_account_id
                lines.append((0,0,move_line_3))
                paid_amount = paid_amount + remaining_amount - other_amount
                remaining_amount = 0
                
            elif paid_amount > 0 :
                move_line_3 = move_line_2.copy()
                move_line_4 = move_line_2.copy()
                move_line_2['debit'] = remaining_amount
                move_line_2['account_id'] = crms_payment_brw.property_advance_account.id
                lines.append((0,0,move_line_2))
                move_line_3['debit'] = paid_amount
                move_line_3['account_id'] = other_account_id
                lines.append((0,0,move_line_3))
                move_line_4['debit'] = other_amount - remaining_amount - paid_amount
                move_line_4['account_id'] = crms_payment_brw.property_retail_account.id                
                lines.append((0,0,move_line_4))
                remaining_amount = -(other_amount - remaining_amount - paid_amount)
                paid_amount = 0
                
            else:
                move_line_3 = move_line_2.copy()
                move_line_2['debit'] = remaining_amount
                move_line_2['account_id'] = crms_payment_brw.property_advance_account.id
                lines.append((0,0,move_line_2))
                move_line_3['debit'] = other_amount - remaining_amount
                move_line_3['account_id'] = crms_payment_brw.property_retail_account.id
                lines.append((0,0,move_line_3))
                remaining_amount = -(other_amount - remaining_amount)
            
        else:
            if paid_amount > 0 and paid_amount > other_amount:
                move_line_2['debit'] = other_amount
                move_line_2['account_id'] = other_account_id
                lines.append((0,0,move_line_2))
                paid_amount = paid_amount - other_amount
                
            elif paid_amount > 0 :
                move_line_3 = move_line_2.copy()
                move_line_2['debit'] = paid_amount
                move_line_2['account_id'] = other_account_id
                lines.append((0,0,move_line_2))
                move_line_3['debit'] = other_amount - paid_amount
                move_line_3['account_id'] = crms_payment_brw.property_retail_account.id
                lines.append((0,0,move_line_3))
                paid_amount = 0
                remaining_amount = other_amount - paid_amount
                
            else:
                move_line_2['debit'] = other_amount
                move_line_2['account_id'] = crms_payment_brw.property_retail_account.id
                lines.append((0,0,move_line_2))
                paid_amount = 0
                remaining_amount = -(other_amount - paid_amount)
        
        self.pool.get('account.move').create(cr,uid, {
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : rental_to_date,
                'period_id': period_ids and period_ids[0] or False,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'period_id':period_ids and period_ids[0] or False,
                'crms_payment_id':crms_payment_brw.id,
                'line_id': lines,
                })
        
        return remaining_amount,paid_amount
    
    # CRMS Payment
    def create_account_voucher_entries(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
            
        period_obj = self.pool.get('account.period')
        move_obj = self.pool.get('account.move')
        
        for crms_payment_brw in self.browse(cr ,uid, ids):
            remaining_amount =crms_payment_brw.remaining_amount
            per_day_amt = crms_payment_brw.per_day_amount
            discount_amt = crms_payment_brw.per_day_amount * (crms_payment_brw.discount/100) if crms_payment_brw.discount else 0.0
            per_day_amt_disc = per_day_amt - discount_amt
            #today_date = datetime.datetime.today() - relativedelta(days=1)
            today_date = datetime.datetime.today()
            expense_date = crms_payment_brw.last_expense_date
            rental_from = crms_payment_brw.rental_from_date
            revenue_days = crms_payment_brw.revenue_days or 0
            
            rental_to_date = datetime.datetime.strptime(crms_payment_brw.rental_to_date[:10],'%Y-%m-%d')
            if rental_to_date < today_date:
                today_date = rental_to_date
            
            if expense_date:
                expense_date = datetime.datetime.strptime(expense_date[:10],'%Y-%m-%d')
            elif rental_from:
                expense_date = datetime.datetime.strptime(rental_from[:10],'%Y-%m-%d')
            else:
                expense_date = today_date
                
            if context.get('no_of_days',False):
                remaining_days = int(context.get('no_of_days')) - revenue_days
            else:
                remaining_days = (today_date - expense_date).days + 1
                
            #while remaining_days >= today_date:
            while remaining_days > 0:
                
                ctx = context.copy()
                ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
                period_ids = period_obj.find(cr, uid, expense_date, context=ctx)
                
                move_lines = [(0,0,{
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : expense_date,
                'partner_id':crms_payment_brw.partner_id.id,
                'period_id': period_ids and period_ids[0] or False,
                'analytic_account_id':crms_payment_brw.vehicle_id.analytic_id.id,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'name': 'Car rent',
                'credit': per_day_amt,
                'account_id': crms_payment_brw.property_revenue_account.id,
                })]
                
                move_line_dict = {
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : expense_date,
                'period_id': period_ids and period_ids[0] or False,
                'partner_id':crms_payment_brw.partner_id.id,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'name': 'Car rent',
                'debit': per_day_amt_disc,
                'account_id': crms_payment_brw.property_advance_account.id,
                }
                
                if remaining_amount < per_day_amt_disc:
                    if remaining_amount > 0:
                        move_line_1 = move_line_dict.copy()
                        move_line_1['debit'] = remaining_amount
                        move_lines.append((0,0,move_line_1))
                        move_line_2 = move_line_dict.copy()
                        move_line_2['debit'] = per_day_amt_disc - remaining_amount
                        move_line_2['account_id'] = crms_payment_brw.property_retail_account.id
                        move_lines.append((0,0,move_line_2))
                    else:
                        move_line_1 = move_line_dict.copy()
                        move_line_1['account_id'] = crms_payment_brw.property_retail_account.id
                        move_lines.append((0,0,move_line_1))
                else:
                    move_lines.append((0,0,move_line_dict))
                    
                if discount_amt :
                    move_line_disc = move_line_dict.copy()
                    move_line_disc['debit'] = discount_amt
                    move_line_disc['account_id'] = crms_payment_brw.property_discount_account.id
                    move_line_disc['analytic_account_id'] = crms_payment_brw.vehicle_id.analytic_id.id
                    move_lines.append((0,0,move_line_disc))
                    
                move_obj.create(cr,uid, {
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : expense_date,
                'period_id': False,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'period_id':period_ids and period_ids[0] or False,
                'crms_payment_id':crms_payment_brw.id,
                'line_id':move_lines,
                })
                
                remaining_amount -= per_day_amt_disc
                remaining_days = remaining_days - 1
                revenue_days += 1
                #expense_date = expense_date + relativedelta(days=1)
                
            self.write(cr, uid, [crms_payment_brw.id], {'last_expense_date':expense_date,'remaining_amount':remaining_amount,'revenue_days':revenue_days}, context)
            
        return True
    
    #Cron Job function
    def cron_create_payment_voucher_entries(self, cr, uid, context=None):
        
#         payment_ids = self.search(cr, uid, [('state','=','Active')])
#         
#         if payment_ids :
#             self.create_account_voucher_entries(cr, uid, payment_ids, context)
        return True

crms_payment()

# Intermediate Payment History Class for keeping track of payment(s) done by Customer.
class crms_payment_intermediatepayment_history(osv.osv):
    _name = "crms.payment.intermediatepayment.history"
    _rec_name = "amount"
    _columns ={
    'date':fields.date(string="Date", required=True),
    'booking_id':fields.many2one('crms.payment',"CRMS Booking ID", required=True),
    'amount':fields.float(string="Actual Amount", required=True),
    'voucher_amount':fields.float(string="Voucher Amount"),
    'payment_type':fields.selection([('Cash','Cash'),('Card','Card'),('Span','Span')],'Payment Type', required=True),
    'voucher_id':fields.many2one('account.voucher',string="Journal Voucher"),
    'crms_id':fields.integer('CRMS Payment ID', readonly=True),
    'admin_expenses':fields.float('Admin Expenses'),
    }
    
    def create(self, cr, uid, data, context=None):
         
        if context is None:context = {}
        
        payment_obj = self.pool.get('crms.payment')
        crms_payment_brw = payment_obj.browse(cr, uid, int(data['booking_id']))
        remaining_amount = crms_payment_brw.remaining_amount
         
        ctx = context.copy()
        ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
        period_ids = self.pool.get('account.period').find(cr, uid, data['date'], context=ctx)
         
        if data.get('payment_type') == 'Cash':
            journal_id = crms_payment_brw.property_cash_journal.id
            account_id = crms_payment_brw.property_cash_journal.default_credit_account_id.id
        else:
            journal_id = crms_payment_brw.property_bank_journal.id
            account_id = crms_payment_brw.property_bank_journal.default_credit_account_id.id
        
        paid_amount = float(data.get('voucher_amount')) - float(data.get('admin_expenses',0.0))
        if crms_payment_brw.remaining_amount and crms_payment_brw.remaining_amount < 0:
            if crms_payment_brw.remaining_amount*-1 < paid_amount:                
                lines = [(0,0,{'account_id': crms_payment_brw.property_retail_account.id, 'amount': crms_payment_brw.remaining_amount*-1, 'type': 'cr',}),
                (0,0,{'account_id': crms_payment_brw.property_advance_account.id, 'amount': paid_amount + crms_payment_brw.remaining_amount, 'type': 'cr',})]
                
            else:
                lines = [(0,0,{'account_id': crms_payment_brw.property_retail_account.id, 'amount': paid_amount, 'type': 'cr',})]
        else:
            if paid_amount > 0:
                lines = [(0,0,{'account_id': crms_payment_brw.property_advance_account.id, 'amount': paid_amount, 'type': 'cr',})]
            else:
                lines = [(0,0,{'account_id': crms_payment_brw.property_advance_account.id, 'amount': paid_amount*-1, 'type': 'dr',})]
        if float(data.get('admin_expenses',0.0)) > 0:
            lines.append((0,0,{'account_id': crms_payment_brw.property_admin_charges_account.id, 'amount': float(data.get('admin_expenses',0.0)), 'type': 'cr',}))
                
        voucher_id = self.pool.get('account.voucher').create(cr, uid, {
        'partner_id': crms_payment_brw.partner_id.id,
        'journal_id': journal_id,
        'type' : 'receipt' if paid_amount > 0 else 'payment',  ###
        'cost_analytic_id' : crms_payment_brw.pickup_branch_id.project_id.id,
        'company_id' : crms_payment_brw.pickup_branch_id.company_id.id,
        'account_id' : account_id,
        'date': data['date'],
        'period_id': period_ids and period_ids[0] or False,
        'amount':float(data['voucher_amount']) if float(data['voucher_amount']) > 0 else float(data['voucher_amount'])*-1,
        'crms_payment_id':data['booking_id'],
        'line_ids': lines
        })
         
        netsvc.LocalService("workflow").trg_validate(uid, 'account.voucher', voucher_id, 'proforma_voucher', cr)
        data['voucher_id'] = voucher_id
        
        remaining_amount = remaining_amount + float(data['amount']) - float(context.get('admin_expenses',0.0))
        cr.execute('update crms_payment set remaining_amount=%s where id=%s',(remaining_amount,data['booking_id']))
         
        return super(crms_payment_intermediatepayment_history, self).create(cr, uid, data, context=context)
    
crms_payment_intermediatepayment_history()

# Discount History Class for keeping Track of Discount given to Customer.
class crms_payment_discount_history(osv.osv):
    _name = "crms.payment.discount.history"
    _rec_name = "discount"
    _columns ={
    'date':fields.date(string="Date", required=True),
    'booking_id':fields.many2one('crms.payment',"CRMS Booking ID", required=True),
    'discount':fields.float(string="Discount(%)", required=True),
    }
    
    def create(self, cr, uid, data, context=None):
        
        if context is None:
            context = {}
            
        crms_payment_brw = self.pool.get('crms.payment').browse(cr ,uid, data['booking_id'])
        discount = float(data['discount']) - (crms_payment_brw.discount or 0.0)
        remaining_amount = crms_payment_brw.remaining_amount
        discount_amt = crms_payment_brw.per_day_amount * (discount/100)
        if discount_amt > 0:
            period_pool = self.pool.get('account.period')
            move_pool = self.pool.get('account.move')
            today_date = datetime.datetime.today()
            rental_to_date = datetime.datetime.strptime(crms_payment_brw.rental_to_date[:10],'%Y-%m-%d')
            
            if rental_to_date < today_date:
                today_date = rental_to_date
                
            if crms_payment_brw.rental_from_date:
                iter_date = datetime.datetime.strptime(crms_payment_brw.rental_from_date[:10],'%Y-%m-%d')
            else:
                iter_date = today_date
                
            while iter_date < today_date:
                
                ctx = context.copy()
                ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
                period_ids = period_pool.find(cr, uid, iter_date, context=ctx)
                move_lines = []
                
                move_line_1 = {
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : iter_date,
                'partner_id':crms_payment_brw.partner_id.id,
                'period_id': period_ids and period_ids[0] or False,
                'analytic_account_id':crms_payment_brw.vehicle_id.analytic_id.id,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'name': 'Discount',
                'account_id': crms_payment_brw.property_discount_account.id,
                'debit':discount_amt
                }
                move_lines.append((0,0,move_line_1))
                
                move_line_2 = {
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : iter_date,
                'partner_id':crms_payment_brw.partner_id.id,
                'period_id': period_ids and period_ids[0] or False,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'name': 'Discount',
                'credit': discount_amt,
                'account_id': crms_payment_brw.property_advance_account.id
                }
                
                if remaining_amount < 0:
                    if  (remaining_amount * -1) >= discount_amt:
                        move_line_2['account_id'] = crms_payment_brw.property_retail_account.id
                        move_lines.append((0,0,move_line_2))
                    else:
                        move_line_3 = move_line_2.copy()
                        move_line_2['account_id'] = crms_payment_brw.property_retail_account.id
                        move_line_2['credit'] = remaining_amount*-1
                        move_lines.append((0,0,move_line_2))
                        move_line_3['credit'] = discount_amt+ remaining_amount
                        move_lines.append((0,0,move_line_3))
                else:
                    move_lines.append((0,0,move_line_2))
                        
                move_pool.create(cr,uid, {
                'journal_id': crms_payment_brw.property_sale_journal.id,
                'date' : iter_date,
                'period_id': False,
                'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
                'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                'period_id':period_ids and period_ids[0] or False,
                'crms_payment_id':crms_payment_brw.id,
                'line_id':move_lines,
                })
                
                remaining_amount += discount_amt
                iter_date = iter_date + relativedelta(days=1)
            
            cr.execute('update crms_payment set remaining_amount=%s where id=%s',(remaining_amount,data['booking_id']))
            
        return super(crms_payment_discount_history, self).create(cr, uid, data, context=context)
    
crms_payment_discount_history()

class crms_daily_revenue(osv.osv):
    _name='crms.daily.revenue'
    _columns={
    'open_balance':fields.float('Open Balance'),
    'booking_id':fields.many2one('crms.payment','Booking Id'),
    'date':fields.date('Date'),
    'revenue':fields.float('Revenue'),
    'discount':fields.float('Discount'),
    'discount_amt':fields.float('Discount amount'),
    'changed_discount':fields.float('Changed Discount Amount'),
    'amount_paid':fields.float('Amount Paid'),
    'amount_returned':fields.float('Amount Return'),
    'admin_expenses':fields.float('Discount'),
    'traffic_violation_charges':fields.float('Amount Paid'),
    'extra_hours_charges':fields.float('Extra Hours Charges'),
    'additional_driver_charges':fields.float('Additional Driver Charges'),
    'damage_charges':fields.float('Car Damage Charges'),
    'other_charges':fields.float('Other Charges'),
    'extra_km_charges':fields.float('Extra Km Charges'),
    }
    
    def create(self, cr, uid, data, context=None):
        
        ctx = context.copy()
        period_pool = self.pool.get('account.period')
        move_pool = self.pool.get('account.move')
        booking_id = int(data.get('booking_id'))
        crms_payment_brw = self.pool.get('crms.payment').browse(cr,uid,booking_id)
        expense_date = data['date']
        remaining_amount = crms_payment_brw.remaining_amount
        per_day_amt = float(data['revenue'])
        discount_amt = float(data.get('discount_amt',0.0))
        per_day_amt_disc = per_day_amt - discount_amt
        
        ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
        period_ids = period_pool.find(cr, uid, expense_date, context=ctx)
        
        move_lines = [(0,0,{
        'journal_id': crms_payment_brw.property_sale_journal.id,
        'date' : expense_date,
        'partner_id':crms_payment_brw.partner_id.id,
        'period_id': period_ids and period_ids[0] or False,
        'analytic_account_id':crms_payment_brw.vehicle_id.analytic_id.id,
        'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
        'company_id':crms_payment_brw.property_sale_journal.company_id.id,
        'name': 'Car Rent Daily Revenue',
        'credit': per_day_amt,
        'account_id': crms_payment_brw.property_revenue_account.id,
        })]
        
        move_line_dict = {
        'journal_id': crms_payment_brw.property_sale_journal.id,
        'date' : expense_date,
        'period_id': period_ids and period_ids[0] or False,
        'partner_id':crms_payment_brw.partner_id.id,
        'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
        'company_id':crms_payment_brw.property_sale_journal.company_id.id,
        'name': 'Car Rent Daily Revenue',
        'debit': per_day_amt_disc,
        'account_id': crms_payment_brw.property_advance_account.id,
        }
        
        if remaining_amount < per_day_amt_disc:
            if remaining_amount > 0:
                move_line_1 = move_line_dict.copy()
                move_line_1['debit'] = remaining_amount
                move_lines.append((0,0,move_line_1))
                move_line_2 = move_line_dict.copy()
                move_line_2['debit'] = per_day_amt_disc - remaining_amount
                move_line_2['account_id'] = crms_payment_brw.property_retail_account.id
                move_lines.append((0,0,move_line_2))
            else:
                move_line_1 = move_line_dict.copy()
                move_line_1['account_id'] = crms_payment_brw.property_retail_account.id
                move_lines.append((0,0,move_line_1))
        else:
            move_lines.append((0,0,move_line_dict))
            
        if discount_amt :
            move_line_disc = move_line_dict.copy()
            move_line_disc['debit'] = discount_amt
            move_line_disc['account_id'] = crms_payment_brw.property_discount_account.id
            move_line_disc['analytic_account_id'] = crms_payment_brw.vehicle_id.analytic_id.id
            move_lines.append((0,0,move_line_disc))
            
        move_pool.create(cr,uid, {
        'journal_id': crms_payment_brw.property_sale_journal.id,
        'date' : expense_date,
        'cost_analytic_id': crms_payment_brw.pickup_branch_id.project_id.id,
        'company_id':crms_payment_brw.property_sale_journal.company_id.id,
        'period_id':period_ids and period_ids[0] or False,
        'crms_payment_id':crms_payment_brw.id,
        'line_id':move_lines,
        })
        
        cr.execute('update crms_payment set remaining_amount=%s where id=%s',(remaining_amount-per_day_amt_disc,data['booking_id']))
        return super(crms_daily_revenue, self).create(cr, uid, data, context=context)
   
crms_daily_revenue()