from openerp.osv import fields, osv
from datetime import datetime,timedelta
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp


class account_asset_category(osv.osv):
    _inherit = "account.asset.category"
    
    _columns = {
                'non_depreciation_value': fields.integer('Non depreciation Time'),
                'non_depreciation_period' : fields.selection([('days','Days'),('months','Months')],'Non Depreciation Period'),
                'depreciation_period' : fields.selection([('days','Days'),('months','Months')],'Depreciation Period',required=True),
                'method_period': fields.integer('Period Length', help="State here the time between 2 depreciations, in months or days", required=True),
                }
    _defaults = {
                 'non_depreciation_period': 'months',
                 'depreciation_period' : 'months'
                 }

        
class account_asset_depreciation_line(osv.osv):
    _inherit = 'account.asset.depreciation.line'
    
    _columns = {
                 'amount': fields.float('Monthly Depreciation', digits_compute=dp.get_precision('Account'), required=True),
                 'remaining_value': fields.float('Book Value', digits_compute=dp.get_precision('Account'),required=True),
                 'depreciated_value': fields.float('Accumulated Depreciated', required=True),
                 
                 
                }
    _order = 'depreciated_value'
              
            
    def create_move(self, cr, uid, ids, context=None):
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
            ids = self.search(cr,uid,[('depreciation_date' ,'<=', datetime.today()),('move_check','=',False),('parent_state','=','open')])
           
        for line in self.browse(cr, uid, ids, context=context):
            #depreciation_date = context.get('depreciation_date') or time.strftime('%Y-%m-%d')
            depreciation_date = line.depreciation_date
            depreciation_date1 = datetime.strptime(depreciation_date,"%Y-%m-%d")     
            if line.asset_id.depreciation_period =='months':
                from_date = depreciation_date1 - relativedelta(months=line.asset_id.method_period) + timedelta(days=1)
            else:
                from_date = depreciation_date1 - relativedelta(days=line.asset_id.method_period) + timedelta(days=1) 
            
            ctx = dict(context, account_period_prefer_normal=True)
            period_ids = period_obj.find(cr, uid, depreciation_date, context=ctx)
            company_currency = line.asset_id.company_id.currency_id.id
            current_currency = line.asset_id.currency_id.id
            context.update({'date': depreciation_date})
            amount = currency_obj.compute(cr, uid, current_currency, company_currency, line.amount, context=context)
            sign = (line.asset_id.category_id.journal_id.type == 'purchase' and 1) or -1
            asset_name = line.asset_id.name
            reference = line.name
            
            vehicle_id = line.asset_id.vehicle_id and line.asset_id.vehicle_id.id or False
            cost_analytic_id = False
            if vehicle_id: 
                fleet_analytic_account_obj = self.pool.get('fleet.analytic.account')
                fleet_analytic = fleet_analytic_account_obj.search(cr, uid, [('date_from','<=',depreciation_date),('date_to', '=', False),('vehicle_id','=',vehicle_id)]) or fleet_analytic_account_obj.search(cr, uid, [('date_from','<=',depreciation_date),('date_to', '!=', False),('date_to','>=',depreciation_date),('vehicle_id','=',vehicle_id)])
                cost_analytic_id = False
                if fleet_analytic:
                    fleet_obj = fleet_analytic_account_obj.browse(cr ,uid,fleet_analytic[0] )
                    cost_analytic_id = fleet_obj.branch_id and fleet_obj.branch_id.project_id and fleet_obj.branch_id.project_id.id    
            else:
                asset_cost_center_obj = self.pool.get('account.asset.cost.center')
                analytic_account = asset_cost_center_obj.search(cr, uid, [('from_date','<=',depreciation_date),('to_date', '=', False),('asset_id','=',line.asset_id.id)]) or asset_cost_center_obj.search(cr, uid, [('from_date','<=',depreciation_date),('to_date', '!=', False),('to_date','>=',depreciation_date),('asset_id','=',line.asset_id.id)])
                cost_analytic_id = False
                if analytic_account:
                    analytic_obj = asset_cost_center_obj.browse(cr ,uid,analytic_account[0] )
                    cost_analytic_id = analytic_obj.analytic_id.id
                else:
                    cost_analytic_id = line.cost_analytic_id and line.cost_analytic_id.id or False
                cost_analytic_id = line.cost_analytic_id and line.cost_analytic_id.id or False
            move_vals = {
                'name': asset_name,
                'date': depreciation_date,
                'ref': reference,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': line.asset_id.category_id.journal_id.id,
                 'cost_analytic_id': cost_analytic_id
                }
            move_id = move_obj.create(cr, uid, move_vals, context=context)
            journal_id = line.asset_id.category_id.journal_id.id
            partner_id = line.asset_id.partner_id.id
            
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_depreciation_id.id,
                'debit': 0.0,
                'credit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and - sign * line.amount or 0.0,
                'date': depreciation_date,
                'cost_analytic_id': cost_analytic_id,
                
            })
            
            move_line_obj.create(cr, uid, {
                'name': asset_name,
                'ref': reference,
                'move_id': move_id,
                'account_id': line.asset_id.category_id.account_expense_depreciation_id.id,
                'credit': 0.0,
                'debit': amount,
                'period_id': period_ids and period_ids[0] or False,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and  current_currency or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': (line.asset_id.analytic_id and line.asset_id.analytic_id.id) or (line.asset_id.category_id and line.asset_id.category_id.account_analytic_id.id) or False,
                'date': depreciation_date,
                'asset_id': line.asset_id.id,
                'from_date': from_date,
                'to_date' : depreciation_date,
                 'cost_analytic_id': line.asset_id.cost_analytic_id and line.asset_id.cost_analytic_id.id or False,
            })
            
            self.write(cr, uid, line.id, {'move_id': move_id}, context=context)
            created_move_ids.append(move_id)
            asset_ids.append(line.asset_id.id)
        # we re-evaluate the assets to determine whether we can close them
        for asset in asset_obj.browse(cr, uid, list(set(asset_ids)), context=context):
            if currency_obj.is_zero(cr, uid, asset.currency_id, asset.value_residual):
                asset.write({'state': 'close'})
        return created_move_ids

class account_asset_asset(osv.osv):
    _inherit = "account.asset.asset"
    
    def _amount_residual(self, cr, uid, ids, name, args, context=None):
        cr.execute("""SELECT
                l.asset_id as id, SUM(abs(l.debit-l.credit)) AS amount
            FROM
                account_move_line l
            WHERE
                l.asset_id IN %s GROUP BY l.asset_id """, (tuple(ids),))
        res=dict(cr.fetchall())
        for asset in self.browse(cr, uid, ids, context):
            res[asset.id] = asset.purchase_value - res.get(asset.id, 0.0) - asset.salvage_value -asset.already_depreciated_amt
        for id in ids:
            res.setdefault(id, 0.0)
        return res
    
    
    def get_serial_no(self, cr, uid, ids, name, arg, context={}):
        res = {}
        count=1
        for each in self.browse(cr, uid, ids):
            res[each.id]=count
            count+=1
        return res

     
    _columns = {
                'already_depreciated_amt' : fields.float('Exa Depreciated Amount'),
                 'dept_arrear' : fields.float('Arrear Amount'),
                'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle'),
                'analytic_id' : fields.many2one('account.analytic.account','Cost Center'),
                'depreciation_period' : fields.selection([('days','Days'),('months','Months')],'Depreciation Period',required=True),
                'depreciation_start_date':fields.date('Depreciation Start Date',required=True),
                'non_depreciation_value': fields.integer('Non depreciation Time'),
                'method_period': fields.integer('Number of Months/Days in a Period', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The amount of time between two depreciations, in months/Days"),
                'non_depreciation_period' : fields.selection([('days','Days'),('months','Months')],'Non Depreciation Period'),
                'cost_analytic_id': fields.many2one('account.analytic.account','Invoice Cost Center', required=True),
                 'value_residual': fields.function(_amount_residual, method=True, digits_compute=dp.get_precision('Account'), string='Residual Value'),
               'is_status':fields.selection([('act','Active'),('inact','Inactive'),('rs','Ready to sell'),('sold','Sold')],'Status'),
                'unique_id' : fields.function(get_serial_no,type='integer',string='Unique ID'),
                }  
    
    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id):
        res = {'value':{}}
        vehicle_obj = self.pool.get('fleet.vehicle')
        if not vehicle_id:
            return res
        vehicle = vehicle_obj.browse(cr,uid,vehicle_id)
        res['value'] = { 'analytic_id': vehicle.analytic_id and vehicle.analytic_id.id or False }
        return res
                    
    def onchange_category_id(self, cr, uid, ids, category_id, purchase_date=False,context=None):
        res = {'value':{}}
        asset_categ_obj = self.pool.get('account.asset.category')
        if category_id:
            category_obj = asset_categ_obj.browse(cr, uid, category_id, context=context)
            res['value'] = {
                            'method': category_obj.method,
                            'method_number': category_obj.method_number,
                            'method_time': category_obj.method_time,
                            'method_period': category_obj.method_period,
                            'method_progress_factor': category_obj.method_progress_factor,
                            'method_end': category_obj.method_end,
                            'prorata': category_obj.prorata,
                            'depreciation_period': category_obj.depreciation_period,
                            'non_depreciation_value':category_obj.non_depreciation_value,
                            'non_depreciation_period':category_obj.non_depreciation_period,
                           
                         }
            if category_obj.non_depreciation_value and  category_obj.non_depreciation_period and purchase_date:
                if category_obj.non_depreciation_period == 'months':
                    res['value']['depreciation_start_date'] = (datetime.strptime(purchase_date, '%Y-%m-%d') + relativedelta(months=+category_obj.non_depreciation_value)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                else:
                    res['value']['depreciation_start_date'] = (datetime.strptime(purchase_date, '%Y-%m-%d') + relativedelta(days=+category_obj.non_depreciation_value)).strftime(DEFAULT_SERVER_DATETIME_FORMAT) or False
            else:
                res['value']['depreciation_start_date'] =   purchase_date         
        return res



    def _get_last_depreciation_date(self, cr, uid, ids, context=None):
        """
        @param id: ids of a account.asset.asset objects
        @return: Returns a dictionary of the effective dates of the last depreciation entry made for given asset ids. If there isn't any, return the purchase date of this asset
        """
        cr.execute("""
            SELECT a.id as id, COALESCE(MAX(l.date),a.depreciation_start_date) AS date
            FROM account_asset_asset a
            LEFT JOIN account_move_line l ON (l.asset_id = a.id)
            WHERE a.id IN %s
            GROUP BY a.id, a.depreciation_start_date """, (tuple(ids),))
        return dict(cr.fetchall())

    def compute_depreciation_board(self, cr, uid, ids, context=None):
        depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
        currency_obj = self.pool.get('res.currency')
        
        for asset in self.browse(cr, uid, ids, context=context):
            depreciation_start_date = asset.depreciation_start_date or asset.purchase_date
            
            
            if asset.value_residual == 0.0:
                continue
            posted_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_check', '=', True)],order='depreciation_date desc')
            old_depreciation_line_ids = depreciation_lin_obj.search(cr, uid, [('asset_id', '=', asset.id), ('move_id', '=', False)])
            if old_depreciation_line_ids:
                depreciation_lin_obj.unlink(cr, uid, old_depreciation_line_ids, context=context)

            amount_to_depr = residual_amount = asset.value_residual
            if asset.prorata:
                depreciation_date = datetime.strptime(self._get_last_depreciation_date(cr, uid, [asset.id], context)[asset.id], '%Y-%m-%d')
                depreciation_date = datetime.strptime(depreciation_start_date, '%Y-%m-%d') - relativedelta(days=+1)
            else:
                # depreciation_date = 1st January of purchase year
                
                purchase_date = datetime.strptime(depreciation_start_date, '%Y-%m-%d')
                #if we already have some previous validated entries, starting date isn't 1st January but last entry + method period
                if (len(posted_depreciation_line_ids)>0):
                    last_depreciation_date = datetime.strptime(depreciation_lin_obj.browse(cr,uid,posted_depreciation_line_ids[0],context=context).depreciation_date, '%Y-%m-%d')
                    if asset.depreciation_period =='months': 
                        depreciation_date = (last_depreciation_date+relativedelta(months=+asset.method_period))
                    else:
                        depreciation_date = (last_depreciation_date+relativedelta(days=+asset.method_period) ) 
                else:
                    depreciation_date = datetime(purchase_date.year, 1, 1)
            day = day1 =depreciation_date.day
            month = month1 = depreciation_date.month
            year = year1 = depreciation_date.year
            total_days = (year % 4) and 365 or 366
            

            undone_dotation_number = self._compute_board_undone_dotation_nb(cr, uid, asset, depreciation_date, total_days, context=context)
            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                i = x + 1
                amount = self._compute_board_amount(cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=context)
                company_currency = asset.company_id.currency_id.id
                current_currency = asset.currency_id.id
                # compute amount into company currency
                amount = currency_obj.compute(cr, uid, current_currency, company_currency, amount, context=context)
                residual_amount -= amount
                
                vals = {
                     'amount': amount,
                     'asset_id': asset.id,
                     'sequence': i,
                     'name': str(asset.id) +'/' + str(i),
                     'remaining_value': residual_amount +(asset.dept_arrear or 0),
                     'depreciated_value': (asset.purchase_value - asset.salvage_value) - (residual_amount + amount) -(asset.dept_arrear or 0) ,
                     'depreciation_date': depreciation_date.strftime('%Y-%m-%d'),
                }
                if amount!=0:
                    depreciation_lin_obj.create(cr, uid, vals, context=context)
                # Considering Depr. Period as months
                if asset.depreciation_period =='months':
                    depreciation_date = (datetime(year1, month1, day1) + relativedelta(months=+(asset.method_period*i)))
                else:
                    depreciation_date = (datetime(year, month, day) + relativedelta(days=+asset.method_period))
                day = depreciation_date.day
                month = depreciation_date.month
                year = depreciation_date.year
        return True


    def _compute_board_amount(self, cr, uid, asset, i, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date, context=None):
        #by default amount = 0
        amount = 0
        if i == undone_dotation_number:
            amount = residual_amount
        else:
            if asset.method == 'linear':
                amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
                if asset.prorata:
                    amount = amount_to_depr / asset.method_number
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        
#                         purchase_date = datetime.datetime.strptime(asset.purchase_date, '%Y-%m-%d')
#                         if not asset.method_period % 12:
#                             for period in  range(asset.method_period / 12):
#                                 if period == 0:
#                                     continue
#                                 next_year_date = (purchase_date + relativedelta(years=period))
#                                 next_year_days = calendar.isleap(next_year_date.year) and 366 or 365
#                                 days += next_year_days
#                                 total_days += next_year_days
#                         else:
#                             total_days = calendar.monthrange(purchase_date.year, purchase_date.month)[1]
#                             days = (total_days - purchase_date.day)
#                             for period in range(asset.method_period):
#                                 if period == 0:
#                                     continue
#                                 next_depreciation_date = (purchase_date + relativedelta(months=period))
#                                 next_month_days = calendar.monthrange(next_depreciation_date.year, next_depreciation_date.month)[1]
#                                 days += next_month_days
#                                 total_days += next_month_days
#                         amount = (amount_to_depr / asset.method_number) / total_days * days
#                                  
                        amount = 0 #(amount_to_depr / asset.method_number) / total_days * days
#                     elif i == undone_dotation_number:
#                         amount = (amount_to_depr / asset.method_number) / total_days * (total_days - days)
            elif asset.method == 'degressive':
                amount = residual_amount * asset.method_progress_factor
                if asset.prorata:
                    days = total_days - float(depreciation_date.strftime('%j'))
                    if i == 1:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * days
                    elif i == undone_dotation_number:
                        amount = (residual_amount * asset.method_progress_factor) / total_days * (total_days - days)
        return amount
