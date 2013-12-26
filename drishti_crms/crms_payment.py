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


class crms_payment(osv.osv):
    _name = 'crms.payment'
    
    _columns = {
                   'name':fields.char('Name',size=64),
                   'crms_id':fields.integer('Crms Payment Id'),
                   'partner_id':fields.many2one('res.partner','Customer Name'),
                   'vehicle_id':fields.many2one('fleet.vehicle','Vehicle'),
                   'car_type_id':fields.many2one('fleet.type','Car Type'),
                   'model_id':fields.many2one('fleet.vehicle.model','Vehicle Model'),
                   'crms_booking_id':fields.integer('Crms Booking Id'),
                   'rental_from_date':fields.datetime('Rental From Date'),
                   'rental_to_date':fields.datetime('Rental To Date'),
                   'no_of_days':fields.integer('No Of Days'),
                   'pickup_branch_id':fields.many2one('sale.shop','Pickup Branch'),
                   'drop_branch_id':fields.many2one('sale.shop','Drop Branch'),
                   'booking_branch_id':fields.many2one('sale.shop','Booking Branch'),
                   'amount_paid':fields.float('Amount Paid by Customer'),
                   'amount_receive_date':fields.datetime('Amount Receive Date'),
                   'rental_amount':fields.float('Rental Amount'),
                   'holding_amount':fields.float('Holding Amount'),
                   'advance_amount':fields.float('Advanced Amount'),
                   'balance_due_amount':fields.float('Balance Due Amount'),
                   'payment_type':fields.selection([('Cash','Cash'),('Card','Card')],'Payment Type'),
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
                    string="bank Journal",
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
                }
    
    
    def create_account_voucher_enries(self, cr, uid, ids, context=None):
        
        # CRMS Payment
        crms_payment_obj = self.pool.get('crms.payment')
        period_obj = self.pool.get('account.period')
        voucher_obj = self.pool.get('account.voucher')
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        
        voucher_line_obj = self.pool.get('account.voucher.line')
        if not ids:
            ids = crms_payment_obj.search(cr, uid, [('status','<>','close')])
        
        for crms_payment_brw in crms_payment_obj.browse(cr ,uid, ids):
              ctx = {}
              
              voucher_dic = {
                             'partner_id': crms_payment_brw.partner_id.id,
                             'journal_id': crms_payment_brw.property_cash_journal.id,
                             'type' : 'receipt',
                             'cost_analytic_id' : crms_payment_brw.pickup_branch_id.analytic_id.id,
                             'company_id' : crms_payment_brw.pickup_branch_id.company_id.id,
                             'account_id' : crms_payment_brw.property_cash_journal.default_credit_account_id,
                             'date': crms_payment_brw.amount_receive_date,
                             'period_id': False
                             
                             }
              ctx.update(company_id=crms_payment_brw.pickup_branch_id.company_id.id,account_period_prefer_normal=True)
              period_ids = period_obj.find(cr, uid, crms_payment_brw.amount_receive_date, context=ctx)
              voucher_dic['period_id'] = period_ids and period_ids[0] or False
              
              voucher_id = voucher_obj.create(cr, uid, voucher_dic)
              
              voucher_line_dic = {
                                  'account_id': crms_payment_brw.property_advance_account.id,
                                  'amount': crms_payment_brw.advance_amount,
                                  'type': 'cr',
                                  'voucher_id': voucher_id,
                                  }
              voucher_line_obj.create(cr, uid, voucher_line_dic)
              
              
              
              
              # Create Journal Entries for revenue
              date = datetime.datetime.today()
              move_dic = {
                          'journal_id': crms_payment_brw.property_sale_journal.id,
                          'date' : date,
                          'period_id': False,
                          'cost_analytic_id': crms_payment_brw.pickup_branch_id.analytic_id.id,
                          'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                          
                          
                          }
              period_ids1 = period_obj.find(cr, uid,crms_payment_brw.property_sale_journal.company_id.id, context=ctx)
              move_dic['period_id'] = period_ids1 and period_ids1[0] or False
              move_id = move_obj.create(cr,uid, move_dic)
              remaining_amount =0
              per_day_amt =100
              move_line_dic = {
                          'journal_id': crms_payment_brw.property_sale_journal.id,
                          'date' : date,
                          'period_id': period_ids1 and period_ids1[0] or False,
                          'partner_id':crms_payment_brw.partner_id.id,
                          'cost_analytic_id': crms_payment_brw.pickup_branch_id.analytic_id.id,
                          'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                          'name': 'Car rent',
                          'debit': per_day_amt,
                          'account_id': crms_payment_brw.advance_amount,
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
                          'cost_analytic_id': crms_payment_brw.pickup_branch_id.analytic_id.id,
                          'company_id':crms_payment_brw.property_sale_journal.company_id.id,
                          'name': 'Car rent',
                          'credit': 0,
                          'account_id': crms_payment_brw.property_revenue_account.id,
                          'move_id' : move_id,
                          }
              move_line_obj.create(cr, uid, move_line_dic1)
              
        
        return True
        