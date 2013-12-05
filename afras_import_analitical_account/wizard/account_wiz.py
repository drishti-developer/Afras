from osv import osv
from osv import fields
from tools.translate import _
import StringIO
import cStringIO
import base64
import xlrd
import string
import sys
class import_analytical_account(osv.osv_memory):
    _name='import.analytical.account'
    _columns={
            'file':fields.binary("File Path:"),
            'file_name':fields.char('File Name:'),
              }
    def import_account_info(self,cr,uid,ids,context=None):
        lst=[]
        list_company=[]
        cur_obj = self.browse(cr,uid,ids)[0]
        account_type_obj=self.pool.get('account.analytic.account')
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
        type='normal'
        for sh in range(0,5):
            print'======sheet_number======',sh
            sheet=wb.sheet_by_index(sh)
            company_id=lst[sh]
            parent_id=parent1=parent2=parent3=parent4=parent5=parent6=False
            for i in range(1,sheet.nrows):
                print'======loop=======',i,sh
                name1 =sheet.row_values(i,0,sheet.ncols)[0]
                print'=======parent_Account---name1--------',name1
                name2 =sheet.row_values(i,0,sheet.ncols)[1]
                print'======parent_account----name2======',name2
                cost_center_type=sheet.row_values(i,0,sheet.ncols)[2]
                print'=======sheet_value=====',cost_center_type
                cost_center_type=cost_center_type.lower()
                print'========cost_center_type====convert lowercase=====',cost_center_type
                region =sheet.row_values(i,0,sheet.ncols)[3]
                print'==========region===========',region
                city =sheet.row_values(i,0,sheet.ncols)[4]
                print'==========city===========',city
                name5 =sheet.row_values(i,0,sheet.ncols)[5]
                print'==========child name===========',name5
                reference_number =sheet.row_values(i,0,sheet.ncols)[6]
                print'======reference_number======',reference_number
                if name1:
                                    
#                                    analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                                   account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name1,'type':type,'code':reference_number,'parent_id':parent_id  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                                   print'======account_id==1==',account_id
                                   parent1=account_id
                                   print'======parent_id1====',parent1
                elif name2:
                                    print'====name2====',name2
#                                     analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
#                                     print'======analitic_parent_id2=======',analitical_parent_id
                                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name2,'type':type,'code':str(int(reference_number)),'parent_id':parent1  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                                    print'======account_id=2===',account_id
                                    parent2=account_id
                                    print'======parent_id1====',parent2
                elif cost_center_type=='region':
#                                   analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                                  region_id=self.pool.get('res.country.state').search(cr,uid,[('name','ilike',region)])
                                  print'=======region=======',region_id
                                  print'=======region name=====',region_id
                                  account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : region,'type':type,'code':str(int(reference_number)),'parent_id':parent2  or False,'company_id':company_id,'entry_type':cost_center_type or False,'region_id':region_id[0]}) 
                                  print'======account_id3====',account_id
                                  parent3=account_id
                                  print'======parent_id3===',parent3
                elif cost_center_type=='company':
#                                     analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name5,'type':type,'code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                                    print'=====account_id4====',account_id
                                    parent4=account_id
                                    print'=====parent4====',parent4 
                elif cost_center_type=='city':
#                                     analitical_parent_id=self.pool.get('account.analytic.account').search(cr,uid,[('parent_id','like',analitical_parent_code)]) 
                                    city_id=self.pool.get('res.state.city').search(cr,uid,[('name','ilike',city)])
                                    print'=======city===1111====',city_id
                                    if not city_id:
                                        account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : city ,'type':type,'code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False,'city_id':city_id}) 
                                        print'=====account_id4====',account_id
                                        parent5=account_id
                                        print'=====parent4====',parent4
                                    else:
                                        account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : city ,'type':type,'code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False,'city_id':city_id[0]}) 
                                        print'=====account_id4====',account_id
                                        parent5=account_id
                                        print'=====parent4====',parent4
                    
                elif parent5:
                                    print'=====parent5====vale-------',parent5
                                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name5,'type':type,'code':str(int(reference_number)),'parent_id':parent5  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                                    print'=====account_id4====',account_id
                else:
                                    account_id=self.pool.get('account.analytic.account').create(cr,uid,{'name' : name5,'type':type,'code':str(int(reference_number)),'parent_id':parent3  or False,'company_id':company_id,'entry_type':cost_center_type or False}) 
                                    print'=====account_id4====',account_id
        return True
