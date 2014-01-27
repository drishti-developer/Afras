from openerp.osv import osv,fields

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
              'from_date': fields.date('From date'),
              'to_date': fields.date('Date To'),
              'fleet_analytic_id':fields.many2one('fleet.analytic.account','Fleet Analytic Account'),
              'asset_id':fields.many2one('account.asset.asset','Asset')
             }
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


    