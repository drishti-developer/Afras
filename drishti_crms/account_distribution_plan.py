from openerp.osv import fields, osv, orm
import time
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
import datetime
#from datetime import datetime
from dateutil import relativedelta
import calendar
from openerp.tools import float_compare
from openerp import netsvc
import openerp.addons.decimal_precision as dp


class account_afras_cost_distribution(osv.osv):
    _name = 'account.afras.cost.distribution'
    _columns = {
                'name' : fields.char('Plan'),
                'related_analytic': fields.many2one('account.analytic.account','Related Analytic Account', required=True),
                'related_period': fields.many2one('account.period','Related Period', required=True),
                'comment': fields.char('Reference'),
                'journal_id': fields.many2one('account.analytic.journal', 'Analytic Journal' ),
                'distribution_lines':fields.one2many('account.afras.cost.distribution.lines','name','Distribution Lines'),
        }
    def get_balance(self,cr,uid,general_account_ids,account,date_to,from_date,context):
        total=0.0
        
        line_obj=self.pool.get('account.analytic.line')
        line_ids=line_obj.search(cr,uid,[('date', '>=', from_date),('date', '<=', date_to),('general_account_id', 'in', general_account_ids),
                                         ('account_id', '=', account.id),('company_id', '=', account.company_id.id)])
        for val in line_obj.browse(cr,uid,line_ids):
        #if account.date >= date_from and account.date <= date_to and account.general_account_id==general_account_id.id:
            total+=val.amount
        return total  
      
    def create_plan_scheduler(self, cr, uid,vals, context=None):
        analytic_account_obj = self.pool.get('account.analytic.account')
        period_obj = self.pool.get('account.period')
        #Get Parent Analytic Accounts
        parent_analytic_ids = analytic_account_obj.search(cr, uid, [('use_distribution_plan','=',True)], context=context)
        parent_analytic_objs = analytic_account_obj.browse(cr,uid,parent_analytic_ids,context=context)
        related_period = 0 #Take today's date and search for the previous period
        #analytic_journal = 0 # Get the related analytic journal
        dist_plan_line_obj = self.pool.get('account.afras.cost.distribution.lines')
        date_today=datetime.date.today()
        month=int(date_today.month)-1
        year=int(date_today.year)
        from_date= str(year)+'-'+str(month)+'-01'
        date = datetime.datetime.strptime(from_date , '%Y-%m-%d').date()
        date_to = str(date + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
        for parent in parent_analytic_objs:
            general_account_id = parent.company_id.revenue_account
            
            
            
            analytic_account_obj = self.pool.get('account.analytic.account')
            child_ids = self.pool.get('account.account').search(cr, uid, [('parent_id','=',general_account_id.id)], context=context)
            child_ids.append(general_account_id.id)
            
            child_ids1 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids)], context=context)
            child_ids2 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids1)], context=context)
            child_ids3 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids2)], context=context)
            child_ids4 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids3)], context=context)
            child_ids5 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids4)], context=context)
            child_ids6 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids5)], context=context)
            child_ids7 = self.pool.get('account.account').search(cr, uid, [('parent_id','in',child_ids6)], context=context)
            child_ids=set(child_ids+child_ids1+child_ids2+child_ids3+child_ids4+child_ids5+child_ids6+child_ids7)
            child_ids=list(child_ids)
            
#             ctx.update(company_id=company_id,account_period_prefer_normal=True)
#             period_ids = period_obj.find(cr, uid, to_date, context=ctx)
#             period_id = period_ids and period_ids[0] or False
            related_period = period_obj.search(cr,uid, [('company_id','=',parent.company_id.id),('date_start','=',from_date)]) 
            plan_id=self.search(cr,uid,[('name','=',parent.name),('related_analytic','=',parent.id),('related_period','=',related_period[0])])
            if not plan_id:
                plan_vals = {
                             'name': parent.name,
                             'related_analytic': parent.id,
                             'related_period': related_period[0],
             #                'journal_id': analytic_journal,
                             
                             }
                plan_id = self.create(cr,uid,plan_vals,context=context)
                print plan_id
                child_analytic_ids = analytic_account_obj._get_children(cr,uid,[parent.id],context=None) # Get all the child Analytic Accounts that are 'not' 'use_distribution_plan'
                child_analytic_ids1=analytic_account_obj.search(cr, uid, [('id', 'in', child_analytic_ids),('use_distribution_plan', '=', False)], context=context)
                child_analytic_objs = analytic_account_obj.browse(cr,uid,child_analytic_ids1,context=context)
                total_rev = 0
                child_accounts_dict = {}
                for account in child_analytic_objs:
                    balance_amt=self.get_balance(cr,uid,child_ids,account,date_to,from_date,context) # We need the Balance for the child "account" for the entire period: period.start_date -> period.end_date for the entries where there general_account_id = general_account_id
                    if balance_amt == 0:
                        continue
                    else:
                        total_rev += balance_amt
                        child_accounts_dict.update({account : balance_amt})
                for key in child_accounts_dict:
                    vals = {
                                'name': int(plan_id),
                                'analytic_account_id': int(key),
                                'rate': child_accounts_dict[key]/total_rev
                                }
                    dist_plan_line_obj.create(cr, uid, vals, context=context)
                
        
    
    

class account_afras_cost_distribution_lines(osv.osv):
    _name = 'account.afras.cost.distribution.lines'
    _columns = {
                'name': fields.many2one('account.afras.cost.distribution','Related Plan'),
                'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account', required=True, domain=[('type','<>','view')]),
                'rate': fields.float('Percentage')
                }