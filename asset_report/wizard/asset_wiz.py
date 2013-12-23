from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_asset_asset_wiz(osv.osv_memory):
    _name='account.asset.asset.wiz'
    _columns={
    'asset_id':fields.many2one('account.asset.asset','Asset'),
    'asset_cat_id':fields.many2one('account.asset.category','Asset category'),
    'status':fields.selection([('act','Active'),('inact','Inactive'),('rs','Ready to sell'),('sld','Sold')],'Status'),
    'asset_location':fields.many2one('stock.location','Asset Location'),
    'start_date':fields.date('As on Date',required=True),  
              }
    _defaults = {
        'start_date': fields.date.context_today,
        'status':'act',
                 }
    
    def print_report(self,cr,uid,ids,context=None):
        data={}
        domain=[]
        obj=self.browse(cr,uid,ids[0])
        asset_obj=self.pool.get('account.asset.asset')
        if obj.asset_cat_id:
            domain.append(('category_id','=',obj.asset_cat_id.id))
        if obj.status:
            domain.append(('is_status','=',obj.status)) 
        if obj.asset_id:
            domain.append(('id','=',obj.asset_id.id))
        asset_ids=asset_obj.search(cr,uid,domain)
        if asset_ids:
            data=self.read(cr, uid, ids,[])[0]
            data['asset_ids']=asset_ids
            return {
                'type':'ir.actions.report.xml',
                'report_name':'account_asset_asset_report',
                'datas':data,
                }
        else:
            return True
account_asset_asset_wiz()