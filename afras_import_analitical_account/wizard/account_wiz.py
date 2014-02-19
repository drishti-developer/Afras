from openerp.osv import osv
from openerp.osv import fields
import StringIO
import base64
import xlrd
class import_analytical_account(osv.osv_memory):
    _name='import.analytical.account'
    _columns={
            'file':fields.binary("File Path:"),
            'file_name':fields.char('File Name:'),
              }
    def import_account_info(self,cr,uid,ids,context=None):
        lst=[]
        cur_obj = self.browse(cr,uid,ids)[0]
        company_obj=self.pool.get('res.company')
        company_id=company_obj.search(cr,uid,[('name','ilike','Facility Management')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Waste Management')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Construction')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','O&M Public Sector')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Syaj')])
        if company_id:
            lst.append(company_id[0])
        file_data=cur_obj.file
        val=base64.decodestring(file_data)
        fp = StringIO.StringIO()
        fp.write(val)     
        wb = xlrd.open_workbook(file_contents=fp.getvalue())
        for sh in range(0,5):
            sheet=wb.sheet_by_index(sh)
            company_id=lst[sh]
            parent_id=parent1=parent2=parent3=parent5=False
            for i in range(1,sheet.nrows):
                name1 =sheet.row_values(i,0,sheet.ncols)[0]
                name2 =sheet.row_values(i,0,sheet.ncols)[1]
                cost_center_type=sheet.row_values(i,0,sheet.ncols)[2]
                cost_center_type=cost_center_type.lower()
                region =sheet.row_values(i,0,sheet.ncols)[3]
                city =sheet.row_values(i,0,sheet.ncols)[4]
                name5 =sheet.row_values(i,0,sheet.ncols)[5]
                reference_number =sheet.row_values(i,0,sheet.ncols)[6]
                if name1:
                                        
#                   analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name1,'type':'normal','code':reference_number,'parent_id':parent_id  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                    parent1=account_id
                elif name2:
#                   analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name2,'type':'normal','code':str(int(reference_number)),'parent_id':parent1  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                    parent2=account_id
                elif cost_center_type=='region':
#                   analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                    region_id=self.pool.get('res.country.state').search(cr,uid,[('name','ilike',region)])
                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : region,'type':'normal','code':str(int(reference_number)),'parent_id':parent2  or False,'company_id':company_id,'entry_type':cost_center_type or False,'region_id':region_id[0]}) 
                    parent3=account_id
                elif cost_center_type=='company':
#                   analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name5,'type':'normal','code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                elif cost_center_type=='city':
#                   analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                    city_id=self.pool.get('res.state.city').search(cr,uid,[('name','ilike',city)])
                    if not city_id:
                        account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : city ,'type':'normal','code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False,'city_id':city_id}) 
                        parent5=account_id
                    else:
                        account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : city ,'type':'normal','code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False,'city_id':city_id[0]}) 
                        parent5=account_id
                    
                elif parent5:
                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name5,'type':'normal','code':str(int(reference_number)),'parent_id':parent5  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                else:
                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name5,'type':'normal','code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
        return True
