from openerp.osv import osv,fields
import datetime

class account_asset_sub_category(osv.osv):
    _name='account.asset.sub.category'
    _columns={
              'name':fields.char('Name',size=64,required=True),
              'parent_id': fields.many2one('account.asset.sub.category', 'Parent category'),
              'child_ids': fields.one2many('account.asset.sub.category', 'parent_id', 'Child category'),
              }
account_asset_sub_category()


class res_company(osv.osv):
    _inherit="res.company"
    _columns={
    'company_ids': fields.many2many('res.company', 'company_rel', 'company_id', 'rel_id', 'Allow Shared Company'),
            }

class account_asset_cost_center(osv.osv):
    _name='account.asset.cost.center'
    _columns={
              'analytic_id':fields.many2one('account.analytic.account','Analytical Account'),
              'from_date': fields.date('From date',required=True),
              'to_date': fields.date('Date To'),
              'fleet_analytic_id':fields.many2one('fleet.analytic.account','Fleet Analytic Account'),
              'asset_id':fields.many2one('account.asset.asset','Asset')
             }
#     def create(self, cr, uid, values, context=None):
#         from_date=values.get('from_date')
#         date_from_year = int(from_date[:4])
#         date_from_month = int(from_date[5:7])
#         date_from_date = int(from_date[8:10])
#         previous_todate = datetime.date(date_from_year,date_from_month,date_from_date) - datetime.timedelta(1)
#         cr.execute('select id from account_asset_cost_center where asset_id=%s and to_date IS NULL',[values.get('asset_id')])
#         record_id=cr.fetchone()[0]
#         cr.execute('update account_asset_cost_center set to_date=%s where id=%s', [previous_todate,record_id])
#         res = super(account_asset_cost_center,self).create(cr, uid, values, context=context)
#         return res
#       
#     def unlink(self, cr, uid, ids, context=None):
#         brw_obj=self.browse(cr,uid,ids[0])
#         if brw_obj.to_date:
#             raise osv.except_osv(('Warning !'),('User can not delete this record if you want to delete this record then first delete the last record then delete '))
#         current_asset_ids=brw_obj.asset_id.id
#         date_from_year = int(brw_obj.from_date[:4])
#         date_from_month = int(brw_obj.from_date[5:7])
#         date_from_date = int(brw_obj.from_date[8:10])
#         cr.execute('select id from account_asset_cost_center where asset_id=%s and to_date IS NULL',[current_asset_ids])
#         record_id=cr.fetchone()[0]
#         if record_id:
#             previous_todate = datetime.date(date_from_year,date_from_month,date_from_date) - datetime.timedelta(1)
#             cr.execute('select id from account_asset_cost_center where to_date=%s',[previous_todate])
#             record_id=cr.fetchone()[0]
#             rec=self.browse(cr,uid,record_id)
#             analytic_id=rec.analytic_id.id
#             asset_id=rec.asset_id.id
#             if rec.to_date:
#                 cr.execute('update account_asset_cost_center set to_date=NULL where id=%s and analytic_id=%s and asset_id=%s',[record_id,analytic_id,asset_id]) 
#                 return super(account_asset_cost_center, self).unlink(cr, uid, ids, context=context)
#          
            
account_asset_cost_center()
    
class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'
    _columns={
       'category_id':fields.many2one('account.asset.sub.category','Category Type'),
       }
account_asset_category()    
    
class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _columns={
        'cost_center_ids':fields.one2many('account.asset.cost.center','asset_id','Cost Center'),
        'sub_category_id':fields.many2one('account.asset.sub.category','Sub Category'),
        'category_rel_id': fields.related('category_id','category_id',type='many2one',relation='account.asset.sub.category',string='Category Type'),
         }
    
    
account_asset_asset()


    