from openerp.osv import fields, osv


class account_asset_asset_wiz(osv.osv_memory):
    _name='account.asset.asset.wiz'
    
    def get_company_id(self,cr,uid,ids,context=None):
        curr_company = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        return curr_company
    
    _columns={
    'asset_id':fields.many2one('account.asset.asset','Asset'),
    'asset_cat_id':fields.many2one('account.asset.category','Asset category'),
    'status':fields.selection([('act','Active'),('inact','Inactive'),('rs','Ready to sell'),('sld','Sold')],'Status'),
    'cost_center_id':fields.many2one('account.analytic.account','Cost Center'),
    'start_date':fields.date('As on Date',required=True),  
    'company_id':fields.many2one('res.company','Company'),
              }
    _defaults = {
        'start_date': fields.date.context_today,
        'status':'act',
        'company_id':get_company_id,
                 }
    
    def print_report(self,cr,uid,ids,context=None):
        data={}
        domain=[]
        obj=self.browse(cr,uid,ids[0])
        asset_obj=self.pool.get('account.asset.asset')
        cost_center_obj=self.pool.get('account.asset.cost.center')
        account_analytic_account_obj=self.pool.get('account.analytic.account')
        if obj.asset_cat_id:
            domain.append(('category_id','=',obj.asset_cat_id.id))
        if obj.status:
            domain.append(('is_status','=',obj.status)) 
        if obj.asset_id:
            domain.append(('id','=',obj.asset_id.id))
        asset_ids=asset_obj.search(cr,uid,domain)
        if obj.cost_center_id:
            cost_center_ids=account_analytic_account_obj._get_children(cr,uid,[obj.cost_center_id.id],context=None)
            to_date=cost_center_obj.search(cr,uid,[('analytic_id','in',cost_center_ids),('asset_id','in',asset_ids),('from_date','<=',obj.start_date),('to_date','>=',obj.start_date)])
            if to_date:
                asset_cost_center_ids=cost_center_obj.search(cr,uid,[('analytic_id','in',cost_center_ids),('asset_id','in',asset_ids),('from_date','<=',obj.start_date),('to_date','>=',obj.start_date)])
            else:
                asset_cost_center_ids=cost_center_obj.search(cr,uid,[('analytic_id','in',cost_center_ids),('asset_id','in',asset_ids),('from_date','<=',obj.start_date)])
            asset_ids = []
            for cost_center_brw in cost_center_obj.browse(cr, uid, asset_cost_center_ids):
                asset_ids.append(cost_center_brw.asset_id.id)
        if asset_ids:
            data=self.read(cr, uid, ids,[])[0]
            data['asset_ids']=asset_ids
            return {
                'type':'ir.actions.report.xml',
                'report_name':'account_asset_asset_report',
                'datas':data,
                  }
        else:
            raise osv.except_osv(('Warning !'),('No record exists for the options selected by the user'))
            return True
    
account_asset_asset_wiz()