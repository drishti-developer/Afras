from openerp.osv import osv
from openerp.osv import fields
import StringIO
import base64
import xlrd
class import_account(osv.osv_memory):
    _name='import.account'
    _columns={
            'file':fields.binary("File Path:"),
            'file_name':fields.char('File Name:'),
              }
    def import_account_info(self,cr,uid,ids,context=None):
        lst=[]
        list_company=[]
        cur_obj = self.browse(cr,uid,ids)[0]
        account_type_obj=self.pool.get('account.account.type')
        company_obj=self.pool.get('res.company')
        company_id=company_obj.search(cr,uid,[('name','ilike','Facility Management')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','O&M Public Sector')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Construction')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Waste Management')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Shared Services')])
        if company_id:
            lst.append(company_id[0])
        company_id=company_obj.search(cr,uid,[('name','ilike','Syaj')])
        if company_id:
            lst.append(company_id[0])
        company_id1=company_obj.search(cr,uid,[('name','ilike','Afras Trading and Contracting')])
        if company_id1:
            lst.append(company_id1[0])
        file_data=cur_obj.file
        val=base64.decodestring(file_data)
        fp = StringIO.StringIO()
        fp.write(val)     
        wb = xlrd.open_workbook(file_contents=fp.getvalue())
        for sh in range(0,7):
            sheet=wb.sheet_by_index(sh)
            company_id=lst[sh]
            parent_id=parent1=parent2=parent3=parent4=parent5=parent6=False
            for i in range(1,sheet.nrows):
                account_code =sheet.row_values(i,0,sheet.ncols)[0]
                acc_type=account_type_obj.search(cr, uid, [('name','ilike','Bank')], context=context)
                user_type=acc_type[0]
                type='other'
                map_company_name=sheet
                name1 =sheet.row_values(i,0,sheet.ncols)[1]
                name2 =sheet.row_values(i,0,sheet.ncols)[2]
                name3 =sheet.row_values(i,0,sheet.ncols)[3]
                name4 =sheet.row_values(i,0,sheet.ncols)[4]
                name5 =sheet.row_values(i,0,sheet.ncols)[5]
                name6 =sheet.row_values(i,0,sheet.ncols)[6]
                name7 =sheet.row_values(i,0,sheet.ncols)[7]
                if sh==6:
                    list_company=[]
                    type='consolidation'
                    map_code1=sheet.row_values(i,0,sheet.ncols)[8]
                    map_code2=sheet.row_values(i,0,sheet.ncols)[9]
                    map_code3=sheet.row_values(i,0,sheet.ncols)[10]
                    map_code4=sheet.row_values(i,0,sheet.ncols)[11]
                    map_code5=sheet.row_values(i,0,sheet.ncols)[12]
                    map_account_id1=self.pool.get('account.account').search(cr,uid,[('code','=',map_code1),('company_id','=',lst[0])])
                    if map_account_id1:
                        list_company.append(map_account_id1[0])
                    map_account_id2=self.pool.get('account.account').search(cr,uid,[('code','=',map_code2),('company_id','=',lst[1])])
                    if map_account_id2:
                        list_company.append(map_account_id2[0])
                    map_account_id3=self.pool.get('account.account').search(cr,uid,[('code','=',map_code3),('company_id','=',lst[2])])
                    if map_account_id3:
                        list_company.append(map_account_id3[0])
                    map_account_id4=self.pool.get('account.account').search(cr,uid,[('code','=',map_code4),('company_id','=',lst[3])])
                    if map_account_id4:
                        list_company.append(map_account_id4[0])
                    map_account_id5=self.pool.get('account.account').search(cr,uid,[('code','=',map_code5),('company_id','=',lst[4])])
                    if map_account_id5:
                        list_company.append(map_account_id5[0])
                    
                if account_code:
                            if name1:
        #                          account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
        #                          if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name1,'type':type,'user_type':user_type,'parent_id':parent_id  or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent1=account_id
    #                             else:
    #                                 self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name1,'type':type,'user_type':user_type,'parent_id':parent_id  or False})    
    
                            elif name2:
    #                             account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
    #                             if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name2,'type':type,'user_type':user_type,'parent_id':parent1 or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent2=account_id
    #                             else:
    #                                 self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name2,'type':type,'user_type':user_type,'parent_id':parent1  or False})    
                            elif name3:
    #                             account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
    #                             if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name3,'type':type,'user_type':user_type,'parent_id':parent2 or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent3=account_id
    #                             else:
    #                                 self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name3,'type':type,'user_type':user_type,'parent_id':parent2  or False})    
                            elif name4:
    #                              account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
    #                              if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name4,'type':type,'user_type':user_type,'parent_id':parent3 or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent4=account_id
    #                              else:
    #                                 self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name4,'type':type,'user_type':user_type,'parent_id':parent3  or False})    
                            elif name5:
    #                              account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
    #                              if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name5,'type':type,'user_type':user_type,'parent_id':parent4 or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent5=account_id
    #                              else:
    #                                 self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name5,'type':type,'user_type':user_type,'parent_id':parent4  or False})    
                            elif name6:
    #                              account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
    #                              if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name6,'type':type,'user_type':user_type,'parent_id':parent5 or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent6=account_id
    #                              else:
#                                         self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name6,'type':type,'user_type':user_type,'parent_id':parent5  or False})    
                            elif name7:
    #                              account_search_id=self.pool.get('account.account').search(cr,uid,[('code','=',account_code)])
    #                              if not account_search_id:
                                account_id=self.pool.get('account.account').create(cr,uid,{'code' : account_code,'name' : name7,'type':type,'user_type':user_type,'parent_id':parent6 or False,'company_id':company_id,'child_consol_ids':[[6,0,list_company]]}) 
                                parent7=account_id
    #                              else:
#                                         self.pool.get('account.account').write(cr,uid,account_search_id[0],{'code':account_code,'name' : name6,'type':type,'user_type':user_type,'parent_id':parent5  or False})    

        
        
        
        
        
        return True
