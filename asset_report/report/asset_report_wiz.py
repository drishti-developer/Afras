from openerp.report import report_sxw
from openerp.tools.translate import _
import time
from datetime import datetime

class account_asset_asset_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(account_asset_asset_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
                              'get_category':self.get_category,
                              'get_total':self.get_total,
                                  })
    def get_total(self,data):
        dic={}
        start_date=data['start_date']
        asset_cat_id=data['asset_cat_id']
        asset_obj=self.pool.get('account.asset.asset')
        category_ids=asset_obj.search(self.cr,self.uid,[('category_id','=',asset_cat_id[0])])
        dic1={}
        result=[]
        depricaited_total_amount=0.0
        current_book_total=0.0
        total_purchase=0.0
        dic={}
        for line in asset_obj.browse(self.cr,self.uid,category_ids):
            depr_line_id= self.pool.get('account.asset.depreciation.line').search(self.cr,self.uid,[('depreciation_date','=',start_date),('asset_id','=',line.id)])
            total_purchase=total_purchase+line.purchase_value
            if depr_line_id:
                 depr_line_obj = self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, depr_line_id[0])
                 depricaited_total_amount=depricaited_total_amount+depr_line_obj.depreciated_value
                 current_book_total=current_book_total+depr_line_obj.remaining_value
        dic['total_purchase']=total_purchase
        dic['depricaited_total_amount']=depricaited_total_amount
        dic['current_book_total']=current_book_total
        return dic
    

 #Add this line in self.localcontext.update dictionary

    def get_category(self, data):
        dic={}
        start_date=data['start_date']
        asset_cat_id=data['asset_cat_id']
        asset_obj=self.pool.get('account.asset.asset')
        category_ids=asset_obj.search(self.cr,self.uid,[('category_id','=',asset_cat_id[0])])
        dic1={}
        result=[]
        depricaited_total_amount=0.0
        current_book_total=0.0
        total_purchase=0.0
        for line in asset_obj.browse(self.cr,self.uid,category_ids):
            depr_line_id= self.pool.get('account.asset.depreciation.line').search(self.cr,self.uid,[('depreciation_date','=',start_date),('asset_id','=',line.id)])
            print "depr_line_id",depr_line_id
            print "line id==============================",line.id
            self.cr.execute('select max(depreciation_date) from account_asset_depreciation_line where asset_id=%s', [line.id])
            date=self.cr.fetchall()[0]
            print'=========exeeee======',date[0]
            dic1 = {
                    'start_date':data['start_date'],
                    'name' :line.name,
                    'amount': 0,
                    'depreciated_value': 0,
                    'remaining_value' :0,
                    'purchase_value':line.purchase_value,
                    'purchase_date':line.purchase_date,
                    'last_period':date[0]
                    }
            if depr_line_id:
                 depr_line_obj = self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, depr_line_id[0])
                 dic1['amount'] = depr_line_obj.amount
                 dic1['depreciated_value'] = depr_line_obj.depreciated_value
                 dic1['remaining_value'] = depr_line_obj.remaining_value
            result.append(dic1)     
        return result

report_sxw.report_sxw('report.account_asset_asset_report', 'account.asset.asset.wiz','asset_report/report/asset.rml', parser=account_asset_asset_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: