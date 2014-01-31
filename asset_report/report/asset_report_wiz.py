from openerp.report import report_sxw
import time
from openerp.osv import osv,fields
import datetime

class account_asset_asset_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_asset_asset_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
                              'get_category':self.get_category,
                              'get_total':self.get_total,
                              'get_headtable':self.get_headtable,
                              'time':time,
                                  })
    def get_total(self,data):
        dic={}
        total_purchase=0.00
        current_book_total=0.00
        depricaited_total_amount=0.00
        status=data['status']
        start_date=data['start_date']
        asset_cat_id=data['asset_cat_id']
        asset_ids=data['asset_ids']
        asset_obj=self.pool.get('account.asset.asset')
        if asset_ids:
            for line in asset_obj.browse(self.cr,self.uid,asset_ids):
                depr_line_id= self.pool.get('account.asset.depreciation.line').search(self.cr,self.uid,[('depreciation_date','=',start_date),('asset_id','=',line.id)])
                total_purchase=total_purchase+line.purchase_value
                if depr_line_id:
                    depr_line_obj = self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, depr_line_id[0])
                    depricaited_total_amount=depricaited_total_amount+depr_line_obj.depreciated_value
                    current_book_total=current_book_total+depr_line_obj.remaining_value
            dic['total_purchase']=total_purchase
            dic['depricaited_total_amount']=depricaited_total_amount
            dic['current_book_total']=current_book_total
        if dic:
            return dic
        else:
            return True
    
    def get_category(self,data):
        status=''
        analytic_account=data['analytic_account']
        print'======analytic_acount======',data['analytic_account']
        asset_ids=data['asset_ids']
        start_date=data['start_date']
        asset_cat_id=data['asset_cat_id']
        status=data['status']
        asset_id=data['asset_id']
        asset_obj=self.pool.get('account.asset.asset')
        dic1={}
        result=[]
        if asset_ids:
                for line in asset_obj.browse(self.cr,self.uid,asset_ids):
                    depr_line_id= self.pool.get('account.asset.depreciation.line').search(self.cr,self.uid,[('depreciation_date','<=',start_date),('asset_id','=',line.id)])
                    print'===depr_line_id=============',depr_line_id
                    get_depr_id=depr_line_id.sort()
                    search_id=self.pool.get('account.asset.cost.center').search(self.cr,self.uid,[('asset_id','=',line.id),('from_date','<=',start_date),'|',('to_date','=',False),('to_date','>=',start_date)])
                    if asset_cat_id == 0.00:
                        asset_cat_id=''
                    if data['status'] == 'act':
                        status='Active'
                        if not search_id:
                            analytic_account=''
                        else:
                            brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
                            analytic_account=brw_id.analytic_id.name
                            print'=====analytic_account======',analytic_account
                    if data['status'] == 'inact':
                        status='Inactive'
                        if not search_id:
                            analytic_account=''
                        else:
                            brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
                            analytic_account=brw_id.analytic_id.name
                            print'=====analytic_account======',analytic_account
                    if data['status'] == 'rs':
                        status='Ready to sell'
                        if not search_id:
                            analytic_account=''
                        else:
                            brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
                            analytic_account=brw_id.analytic_id.name
                            print'=====analytic_account======',analytic_account
                    if data['status'] == 'sold':
                        status='Sold'
                        print'=======gggggggggggggggg'
                        analytic_account=''
                    elif data['status'] == False:
                        print'======status===11111==',data['status']
                        status=line.is_status
                        if status == 'act':
                            status='Active'
                            if not search_id:
                                analytic_account=''
                            else:
                                brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
                                analytic_account=brw_id.analytic_id.name
                                print'=====analytic_account======',analytic_account
                        elif status == 'inact':
                            status='Inactive'
                            if not search_id:
                                analytic_account=''
                            else:
                                brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
                                analytic_account=brw_id.analytic_id.name
                                print'=====analytic_account======',analytic_account
                        elif status == 'rs':
                            status='Ready to sell'
                            if not search_id:
                                analytic_account=''
                            else:
                                brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
                                analytic_account=brw_id.analytic_id.name
                                print'=====analytic_account======',analytic_account
                        elif status == 'sold':
                            status='Sold'
                            analytic_account=''
#                     else:
#                         search_id=self.pool.get('account.asset.cost.center').search(self.cr,self.uid,[('asset_id','=',line.id),('from_date','<=',start_date),'|',('to_date','=',False),('to_date','>=',start_date)])
#                         print'===search_id======',search_id
#                         brw_id=self.pool.get('account.asset.cost.center').browse(self.cr,self.uid,search_id[0])
#                         analytic_account=brw_id.analytic_id.name
#                         print'=====analytic_account======',analytic_account
    # #                     self.cr.execute('select max(depreciation_date) from account_asset_depreciation_line where asset_id=%s', [line.id])
    #                     date=self.cr.fetchall()[0]
                    dic1 = {
                                        'start_date':data['start_date'],
                                        'is_status':status,
                                        'name' :line.name,
                                        'amount': 0,
                                        'depreciated_value': 0,
                                        'remaining_value' :0,
                                        'purchase_value':line.purchase_value,
                                        'purchase_date':line.purchase_date,
                        #               'last_period':date[0],
                                        'analytic_id':analytic_account,
                                        }
                    if depr_line_id:
                        depr_line_obj = self.pool.get('account.asset.depreciation.line').browse(self.cr, self.uid, depr_line_id[0])
                        dic1['amount'] = depr_line_obj.amount
                        dic1['depreciated_value'] = depr_line_obj.depreciated_value
                        dic1['remaining_value'] = depr_line_obj.remaining_value
                    result.append(dic1) 
                if result:
                    return result
                else:
                    return True
        
        
    def get_headtable(self, data):
            dic={}
            state=''
            status=data['status']
            print'======status====',status
            asset_cat_id=data['asset_cat_id']
            if data.get('start_date'):
                dic.update({'start_date':data['start_date']})
            if data.get('asset_cat_id'):
                dic.update({'asset_cat_id':data['asset_cat_id'][1]})
            else:
                dic.update({'asset_cat_id':''})
            if data.get('status') == 'act':
                    state='Active'
                    dic.update({'status':state})
            if data.get('status') == 'inact':
                    state='Inactive'
                    dic.update({'status':state})
            if data.get('status') == 'rs':
                    state='Ready to sell'
                    dic.update({'status':state})
            if data.get('status') == 'sold':
                    state='Sold'
                    dic.update({'status':state})
                 
            return  dic
            
            
        

report_sxw.report_sxw('report.account_asset_asset_report', 'account.asset.asset.wiz','asset_report/report/asset.rml',parser=account_asset_asset_report,header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: