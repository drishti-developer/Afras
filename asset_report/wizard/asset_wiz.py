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
    
    def print_report(self,cr,uid,ids,data,context=None):
        data.update(self.read(cr, uid, ids, ['start_date','asset_cat_id'])[0])
        print'=====datatattatat====',data
#         datas = {
#              'ids': ids,
#              'model': 'account.asset.asset.wiz',
#              'form': []
#                  }
        return {
                'type':'ir.actions.report.xml',
                'report_name':'account_asset_asset_report',
                'datas':data,
              }
account_asset_asset_wiz()