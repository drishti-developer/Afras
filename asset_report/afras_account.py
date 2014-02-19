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
              'from_date': fields.date('From date'),
              'to_date': fields.date('Date To'),
              'fleet_analytic_id':fields.many2one('fleet.analytic.account','Fleet Analytic Account'),
              'asset_id':fields.many2one('account.asset.asset','Asset')
             }
    
    def create(self, cr, uid, values, context=None):
        from_date=values.get('from_date')
        asset_ID=self.search(cr,uid,[('asset_id','=',values.get('asset_id')),('to_date','=',False)])
        self.write(cr,uid,asset_ID,{'to_date':datetime.date(int(from_date[:4]),int(from_date[5:7]),int(from_date[8:10])) - datetime.timedelta(1)})
        return super(account_asset_cost_center,self).create(cr, uid, values, context=context)
       
    def unlink(self, cr, uid, ids, context=None):
        brw_obj=self.browse(cr,uid,ids[0])
        asset_id=self.search(cr,uid,[('asset_id','=',brw_obj.asset_id.id),('to_date','=',False)])
        if brw_obj.to_date:
            raise osv.except_osv(('Warning !'),('User can not delete this record if you want to delete this record then first delete the last record then delete '))
        if asset_id:
            previousdate_asset_id=self.search(cr,uid,[('to_date','=',datetime.date(int(brw_obj.from_date[:4]),int(brw_obj.from_date[5:7]),int(brw_obj.from_date[8:10])) - datetime.timedelta(1))])
            if previousdate_asset_id:
                rec=self.browse(cr,uid,previousdate_asset_id[0])
                if rec.to_date:
                    pre_asset_id=self.search(cr,uid,[('asset_id','=',rec.asset_id.id),('id','=',previousdate_asset_id),('analytic_id','=',rec.analytic_id.id)])
                    self.write(cr,uid,pre_asset_id,{'to_date':False})
        return super(account_asset_cost_center, self).unlink(cr, uid, ids, context=context)
            
account_asset_cost_center()
    
class account_asset_category(osv.osv):
    _inherit = 'account.asset.category'
    _columns={
       'category_id':fields.many2one('account.asset.sub.category','Asset Category'),
       }
account_asset_category()    
    
class account_asset_asset(osv.osv):
    _inherit = 'account.asset.asset'
    _columns={
        'cost_center_ids':fields.one2many('account.asset.cost.center','asset_id','Cost Center'),
        'sub_category_id':fields.many2one('account.asset.sub.category','Sub Category'),
        'category_rel_id': fields.related('category_id','category_id',type='many2one',relation='account.asset.sub.category',string='Asset Category',store=True),
         'unique_id': fields.char('Unique'),
          }
account_asset_asset()




    