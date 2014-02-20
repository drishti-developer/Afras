from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
from openerp import netsvc



class location_setting(osv.osv):
    _name='location.setting'
    _columns={
              'name':fields.char('Location Name'),
              'location_id':fields.many2one('stock.location','Location'),
              }

PRODUCT_CATEGORY_DIC = {
                'CATEGORYCODE':'ops_code',
                'DESCRIPTIONE':'name',
                'DESCRIPTIONA':'name_arabic',
                'CATEGORYSTATUS': 'active',
               
                }

PRODUCT_LIST = {
                'ITEMNUMBER':'ops_code',
                'ITEMNAMEA':'name_arabic',
                'ITEMNAMEE':'name',
                'ITEMSTATUS':'status',
                'CATEGORYCODE':'categ_id',
                'DESC2':'description',
                 }

SUPPLIER_LIST = {
            'VNO':'ops_code',
            'VNAMEA':'arabic_name',
            'FAX':'fax',
            'COUNTRY':'country_id',
            'CITY':'city',
            'ADDRESS1':'street',
            'ADDRESS2':'street2',
            'REGION':'state_id',
            'EMAIL':'email',
            'WEBSITE':'website',
            'TELEPHONE':'phone',
            'ETELEPHONE':'phone_ext',
            'ETAX':'fax_ext',
            'VNAMEE':'name',
            'STATUS':'active',
            'MAXCREDITLIMIT':'credit_limit',
            'CRNO':'crno',
            'DESC1':'comment',
            'CONTACTNO':'contact_phone',
            'CONTACTNAME':'contact_name',
            'ECONTACTNO':'contact_phone_ext',
            'OWNERNAME':'owner_name',
            'OWNEREMAIL':'owner_email',
            'OWNERNUM':'owner_phone',
            'CEONAME':'ceo_name',
            'BANKID':'ops_id',
            'BENEFICIARYNAME':'bank_holder_name',
            'ACCOUNTNO':'acc_number',
            'BRANCH':'bank_name',
            'IBAN':'bank_bic',
            'AGTREEMENTPATH':'',
            'REGDOCPATH':'',
             'BANKDOCPATH':'',
            }
ACCOUNT_DETAILS={
                'ACCOUNTANTID':'ops_accountant',
                'EMPLOYEECODE':'employee_code',
                'PROJECTCODE':'project_code',
                'LOCATIONSERIALNUMBER':'location_serial_counter',
                }
PURCHASE_ORDER_DIC={
           'PURCHASEORDERNO':'ops_order_id',  #ops_id
           'PURCHASEDATE':'date_order',
           'PURCHASEMETHOD':'invoice_method',
           'VENDORNO':'partner_id',
           
           'PROJECTCODE':'PROJECTCODE',
           'PURCHASETYPE':'purchase_type',
           'LOCATIONSERIALCOUNTER':'location_serial_counter',
           
           'QUOTATIONNUMBER':'partner_ref',
           'RECORDSTATUS':'state',
           


           'PAYMENTSTATUS':'',
           'TOTALAMOUNT':'po_amount',
           'DISCOUNTACT':'discount_type',
           'SERVICEACT':'service_type',
           'DEDUCTIONACT':'deduction_type',
           'DISCOUNTAMOUNT':'discount_amt',
           'DEDUCTIONAMOUNT':'deduction_amt',
           'SERVICEAMOUNT':'service_amt',
           'NETAMOUNT':'amount_total',
           'EXPENSETYPE':'revenue_type',
           'REIMBURSESTATUS':'reimurses_status',
           'REIMBURSECOMMAMOUNT':'reimurses_com_amt',
           'REIMBURSABLEAMOUNT':'reimurses_total_amt',
          
           'INVOICENUMBER':'origin',
           'INSTALLMENTS':'',
           'SQLREFERENCENO':'',
           'VENDORSTATUS':'',
           'REPORTCOUNT':'',
           'VENDORUPDATEDDATE':'',
           'ISMANUALPURCHASE':'',
            'DESC3':'',
           'DESC2':'',
           'DESC1':'',
           'PRricelist_id':'pricelist_id',
           'product_id':'product_id',
           'order_line':'order_line'
   }

           
PURCHASE_ORDER_LINE_DICT = {
                            'PURCHASEORDERNO': '' ,
                            'PURCHASEDETAILID': '',
                            'QUOTATIONNUMBER': '' ,
                            'RECORDSTATUS': '',
                            'REQUESTNO' : '',
                            'REQUESTDETAILID' : '',
                            'ITEMPRICE' : '',
                             'ITEMTOTAL' : '',
                             'UNITDISCOUNT' : '',
                             'VENDORSTATUS' :'',
                             'ADDITIONAL_CHARGE' : '',
                             'QUANTITY' : '',
                             'QDETNO' : '',
                            }   
        
class product_category(osv.osv):
    _inherit = "product.category"
    _columns={
                'ops_code':fields.char('OPS Code'),
                'name_arabic':fields.char('Arabic Name',size=64),       
             }
    
    def CreateRecord(self, cr, uid, vals, context=None):
        dic = {}
        
        for key,value in vals.iteritems():
            dic[PRODUCT_CATEGORY_DIC.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
        
        if dic.get('ops_code',False):   
            category_id = self.search(cr, uid, [('ops_code','=',dic['ops_code'])])
            if category_id:
                self.write(cr,uid,category_id[0],dic)
            else:
                category_id = [self.create(cr,uid,dic,context={})]
            return category_id[0]
        else:
            return False

product_category()


class product_product(osv.osv):
    _inherit="product.product"
    
    _columns={
            'ops_code':fields.char('OPS Code'),
            'name_arabic':fields.char('Arbic Name',size=64),
            'status':fields.char('Item Status',readonly=True),
            
            }
    _defaults={
               'active':True,
               }
                
    def CreateRecord(self, cr, uid, vals, context=None):
        
        dic={
            'sale_ok':'True',
            'purchase_ok':'True',
            'procure_method':'make_to_stock',
            'supply_method':'buy',
            'type':'consu',
             }
        categ_obj=self.pool.get('product.category')
        
        for key,value in vals.iteritems():
            dic[PRODUCT_LIST.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
        if dic.get('ops_code',False) and dic.get('categ_id',False):
            category_id = categ_obj.search(cr, uid, [('ops_code','=',dic['categ_id'])])
            if category_id:
                dic['categ_id'] = category_id[0]
                product_id = self.search(cr, uid,[('ops_code','=',dic['ops_code'])] )
                product_id = self.write(cr,uid,product_id[0],dic) and product_id[0] \
                                 if product_id else self.create(cr,uid,dic,context={})
                return product_id
            return False  
        else:    
            return False
    
product_product()


    
class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
              'ops_code':fields.char('OPS Code'),
              'phone_ext':fields.char('Phone Ext',size=64),
              'crno':fields.char('Company Registration Number',size=64),
              'fax_ext':fields.char('Fax Ext',size=64),
              'name':fields.char('Name',size=64),
              'ops_accountant':fields.integer('Ops Accountant'),
              'project_code':fields.char('Project Code',size=64),
              'employee_code':fields.char('Employee Code',size=64),
              'location_serial_counter':fields.integer('Location Serial Counter'),
             }
    
    #request for multiple record is to be done
    def CreateRecord(self, cr, uid, vals):
        dic = {}
        partner_obj=self.pool.get('res.partner')
        country_obj=self.pool.get('res.country')
        state_obj=self.pool.get('res.country.state')
        bank_obj=self.pool.get('res.bank')
        partner_bank_obj=self.pool.get('res.partner.bank')
        if vals.get('ACCOUNTANTID') and vals.get('EMPLOYEECODE') and vals.get('PROJECTCODE'):
            name = 'Accountant' + '-' + vals['EMPLOYEECODE'] + '-' + vals['ACCOUNTANTID']
            partner_id = partner_obj.search(cr,uid,[('ops_accountant','=',vals['ACCOUNTANTID'])])
            partner_id = self.write(cr,uid,partner_id[0],vals) and partner_id[0] \
                            if partner_id else self.create(cr,uid,{'name':name,'ops_accountant':vals['ACCOUNTANTID'],'project_code':vals['PROJECTCODE'],
                                                                            'employee_code':vals['EMPLOYEECODE'],'location_serial_counter':vals['LOCATIONSERIALNUMBER']},context={})
            
            return partner_id
        
        else:
            for key,value in vals.iteritems():
                dic[SUPPLIER_LIST.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
    
            if dic.get('ops_code',False):
                partner_id = partner_obj.search(cr, uid, [('ops_code','=',dic['ops_code'])])
                
                
                #Assuming country is created in OpenERP and same name is available in OPS. OPS Should use either name(English) or code of the country
                # Country OPS ID
                # Please confirm whether Region will pass as Arabic or English or both
                # Region OPS ID
                # Need to confirm from OPS whether we need to create Region in OpenERP or not if state not available
                #  
                # If we need to create then we must need state code also because code is a required field
                
                if dic.get('country_id',False):
                    name_domain = [('name','=',dic['country_id'])]
                    code_domain = [('code','=',dic['country_id'])]
                    country_id = country_obj.search(cr, uid, name_domain) or \
                                     country_obj.search(cr, uid, code_domain)
                    dic['country_id'] = country_id and country_id[0] or False
                    if dic.get('state_id',False):
                        name_domain = [('name','=',dic['state_id']),('country_id','=',dic['country_id'])]
                        code_domain = [('code','=',dic['state_id']),('country_id','=',dic['country_id'])]
                        state_id = state_obj.search(cr, uid, name_domain) or \
                                       state_obj.search(cr, uid, code_domain)
                        dic['state_id'] = state_id and state_id[0] or False
                dic['active'] = True if dic['active'] == 'A' else False  
                
                #Vendor is a company and supplier
                dic['is_company'] =True
                dic['supplier'] =True
                partner_id = self.write(cr,uid,partner_id[0],dic) and partner_id[0] \
                                 if partner_id else self.create(cr,uid,dic,context={})                  
                
                # if contact name then one record will create for contact and map to vendor
                if dic.get('contact_name',False): 
                    domain = [('parent_id','=',partner_id),('name','=',dic['contact_name'])]
                    partner_id = partner_obj.search(cr, uid, domain)
                      
                    contact_dic = { 'name': dic['contact_name'],'parent_id':partner_id ,
                                    'phone': dic.get('contact_phone',False),
                                    'phone_ext': dic.get('contact_phone_ext',False), }
                    partner_id = self.write(cr,uid,partner_id[0],contact_dic) and partner_id[0] \
                                     if partner_id else self.create(cr,uid,contact_dic,context={})
                    
                # if owner name then one record will create for owner and map to vendor   
                if dic.get('owner_name',False):  
                    domain = [('parent_id','=',partner_id),('name','=',dic['owner_name'])]
                    partner_id = partner_obj.search(cr, uid, domain)
                    owner_dic ={ 'name': dic['owner_name'],'parent_id':partner_id,
                                 'phone': dic.get('owner_phone',False),
                                 'email': dic.get('owner_email',False),}
                    partner_id = self.write(cr,uid,partner_id[0],owner_dic) and partner_id[0] \
                                     if partner_id else self.create(cr,uid,owner_dic,context={})
                 
                # if ceo name then one record will create for CEO and map to vendor
                if dic.get('ceo_name',False): 
                    domain = [('parent_id','=',partner_id),('name','=',dic['ceo_name'])]
                    partner_id = partner_obj.search(cr, uid, domain) 
                    ceo_dic ={ 'name': dic['ceo_name'],
                               'parent_id':partner_id }   
                    partner_id = self.write(cr,uid,partner_id[0],ceo_dic) and partner_id[0] \
                                     if partner_id else self.create(cr,uid,ceo_dic,context={})
                                     
                # if BankID(ops_id) then create bank in OpenERP res.bank     
                # OPS Need to send Bank Name Also     
                if dic.get('ops_id',False):  
                    domain = [('ops_id','=',dic['ops_id'])]
                    bank_id = bank_obj.search(cr, uid, domain)
                    bank_dic ={ 'name': dic['ops_id'],'country': dic['country_id'],
                                'ops_id':  dic.get('ops_id',False),
                                'bic': dic.get('bank_bic',False),}
                    bank_id = bank_id[0] if bank_id else bank_obj.create(cr,uid,bank_dic,context={})  
                         
                    # if Bank Holder name then one record will create for BankHolderName and map to vendor   
                    if dic.get('bank_holder_name',False): 
                        domain =  [('parent_id','=',partner_id),('name','=',dic['bank_holder_name'])]
                        bank_holder_id = partner_obj.search(cr, uid, domain)
                        bank_holder_dic ={ 'name': dic['bank_holder_name'],
                                           'parent_id':partner_id }
                        bank_holder_id = bank_holder_id[0] if bank_holder_id else self.create(cr,uid,bank_holder_dic,context={})
                          
                        # Create vendor Bank account in OpenERP res.partner.bank 
                        #Assuming country of Bank is same as vendor country
                        if  dic.get('acc_number',False):   
                            partner_bank_dic = { 'acc_number': dic['acc_number'],'state' : 'bank',
                                                 #'partner_id':partner_id and partner_id[0] or False,
                                                 'bank_name' : dic.get('bank_name',False),  
                                                 'bank_bic' : dic.get('bank_bic',False),
                                                 'owner_name': dic.get('bank_holder_name',False),
                                                 'bank': bank_id,
                                                 'partner_id' : partner_id,
                                                 'country_id':dic['country_id'],}
                        # According to me if bank account type is IBAN then we need to create another bank record
                        # WE Must need bank identifier code or swift code for IBAN Account Bank
                        # Assuming IBAN and Normal both belong to same bank as we are getting only one bankid
    #                         if dic.get('bank_bic',False):
    #                             partner_bank_dic['state'] = 'iban'
                            domain = [('partner_id','=',bank_holder_id),('bank','=',bank_id),('acc_number','=',dic['acc_number'])]
                            partner_bank_id = partner_bank_obj.search(cr, uid, domain)    
                            if not partner_bank_id:
                                partner_bank_id = partner_bank_id[0] if partner_bank_id \
                                          else partner_bank_obj.create(cr, uid,partner_bank_dic,context={})
                            
                                                    
                return partner_id  
        
res_partner()

MATERIAL_DIC = {
            'REQUESTNO':'ops_id',
            'REQUESTDATE':'date_start',
            'REQUESTSTATUS':'status',
            'PROJECTCODE':'project_code',
            'LOCATIONSERIALCOUNTER':'location_serial_counter',
            'PURPOSE':'description',
            'RMRNUMBER':'rmrnumber',
            'ISBUDGET':'is_budget',
            }

MATERIAL_LINE_DIC = {
            'REQUESTNO':'requisition_id',
            'ITEMNUMBER':'product_id',
            'QUANTITY':'product_qty',
            'UNITTYPE':'product_uom_id',
            'PURPOSE':'description',
            'RQSTDETAILSTATUS':'status',
            'REQUESTDETAILID':'ops_id',
            }



class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    
    _columns={
              'analytic_id':fields.many2one('account.analytic.account','Cost Center'),
              'ops_id':fields.integer('OPS Request No'),
              'rmrnumber':fields.char('Revenue ref Number',size=64),
              'status':fields.char('Request Status'),
              
              'location_serial_counter':fields.char('Location Serial Counter'),
              'project_code':fields.char('Project Code'),
              'is_budget':fields.boolean('Is Budget')
              }
    
    def CreateRecord(self, cr, uid, vals, context=None):
        dic = { 'exclusive' : 'exclusive',
               }
        
        analytic_obj=self.pool.get('account.analytic.account')
        for key,value in vals.iteritems():
            dic[MATERIAL_DIC.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
        dic['name'] = dic['ops_id']
        if dic.get('is_budget'):
            if dic['is_budget'].lower() == 'true':
                budget=True
            else:
                budget=False
        else:
            budget=False
        if dic['project_code'] :
            if dic['location_serial_counter'] :
                ref = str(dic['project_code']) + '0'*(3-len(str(dic['location_serial_counter']))) + str(dic['location_serial_counter'])
            else:
                ref =  str(dic['project_code'])
            # Assuming Project already available in analytic account otherwise we will not create and pass as False    
            dic['analytic_id'] = analytic_obj.search(cr, uid, [('code','=',ref)]) and analytic_obj.search(cr, uid, [('code','=',ref)])[0] or False
        dic['is_budget']=budget              
        requisition_id = self.search(cr, uid, [('ops_id','=',dic['ops_id'])])
        requisition_id = self.write(cr,uid,requisition_id[0],dic) and requisition_id[0] \
                                 if requisition_id else self.create(cr,uid,dic,context={})
        return requisition_id  
         
    
purchase_requisition()

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    
    _columns={
              'description' : fields.char('Description',size=64),
              'ops_id':fields.integer('OPS Request Detail ID'),
              'status':fields.char('Request Line Status'),
              }
    
    
    def CreateRecord(self, cr, uid, vals, context=None):
        dic = {  }
        #print "create=======",vals
        requisition_obj=self.pool.get('purchase.requisition')
        product_obj=self.pool.get('product.product')
        
        for key,value in vals.iteritems():
            dic[MATERIAL_LINE_DIC.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
        requisition_id = requisition_obj.search(cr, uid, [('ops_id','=',dic['requisition_id'])])
#        print 'requisition_id======',requisition_id
        product_id = product_obj.search(cr, uid, [('ops_code','=',dic['product_id'])])
        print "product id",product_id
        if requisition_id and product_id:
            dic['requisition_id'] = requisition_id[0]
            dic['product_id'] = product_id[0]
            requisition_line_id = self.search(cr, uid, [('ops_id','=',dic['ops_id'])])
            print 'requisition_line_id======',requisition_line_id
            requisition_line_id = self.write(cr,uid,requisition_line_id[0],dic) and requisition_line_id[0] \
                                 if requisition_line_id else self.create(cr,uid,dic,context={})
            return requisition_line_id                     
        else:
            return False
        

#COUNTRY_LIST_DIC = {
#            'ERPID':'id',
#            'NAME':'name',
#            'NAMEARABIC':'arabic_name',
#            'CODE':'code',
#            'CALLINGCODE':'calling_code',
#            'CURRENCYCODE':'currency_id',
#            }

COUNTRY_DIC={
            'ERPID':'1',
            'OPSID':'5',
            }
class res_country(osv.osv):
    _inherit='res.country'
    _columns={
              'ops_id':fields.char('OPS Country ID',readonly=True),
              
              } 
    def ListRecord(self,cr,uid):
        res=[]
        dic={}
        country_obj=self.pool.get('res.country')
        country_ids=country_obj.search(cr,uid,[])
        for val in country_obj.browse(cr,uid,country_ids):
            dic={
                  'ERPID':val.id,
                  'NAME':val.name,
                  'NAMEARABIC':(val.arabic_name.encode('utf-8')),
                  'CODE':val.code,
                  'CALLINGCODE':val.calling_code,
                  'CURRENCYCODE':val.currency_id.id,
                  }
            res.append(dic)
        return res
    
    def UpdateRecord(self,cr,uid,vals):
        if isinstance(vals,(list,tuple)):
            for dict in vals:
                if dict.get('ERPID',False) and dict.get('OPSID',False):
                    self.pool.get('res.country').write(cr,uid,[dict['ERPID']],{'ops_id':dict['OPSID']})
        else:
            if vals.get('ERPID',False) and vals.get('OPSID',False):
                    self.pool.get('res.country').write(cr,uid,[vals['ERPID']],{'ops_id':vals['OPSID']})
        return True

class res_country_state(osv.osv):
    _inherit='res.country.state'
    _columns={
               'ops_id':fields.char('OPS Region ID',readonly=True),
               
               }
    def ListRecord(self,cr,uid):
        res=[]
        dict={}
        region_obj=self.pool.get('res.country.state')
        for val in region_obj.browse(cr,uid,region_obj.search(cr,uid,[])):
#assuming country ops code is updated in ERP
            if val.country_id.ops_id >0:
                dict={
                      'ERPID':val.id,
                      'REGIONNAME':val.name,
                      'REGIONCODE':val.code,
                      'COUNTRYOPSID':val.country_id.ops_id,
                      'COUNTRYERPID':val.country_id.id,
                      }
                res.append(dict)
        return res
    
    def UpdateRecord(self,cr,uid,vals):
        if isinstance(vals,(list,tuple)):
            for dict in vals:
                if dict.get('ERPID',False) and dict.get('OPSID',False):
                    self.pool.get('res.country.state').write(cr,uid,[dict['ERPID']],{'ops_id':dict['OPSID']})
        else:
            if vals.get('ERPID',False) and vals.get('OPSID',False):
                    self.pool.get('res.country.state').write(cr,uid,[vals['ERPID']],{'ops_id':vals['OPSID']})
        return True
    
city_dict={
            'CITYNAME':'name',
            'CITYNAMEARABIC':'arabic_name',
            'CITYCODE':'code',
            'CITYOPSID':'ops_id',
            'COUNTRYERPID':'country_id',
            'REGIONERPID':'state_id',
           
           }
class res_state_city(osv.osv):
    _inherit='res.state.city'
    _columns={
              'ops_id':fields.char('OPS City ID',readonly=True),
              }
    
    def ListRecord(self,cr,uid):
        res=[]
        dict={}
        region_obj=self.pool.get('res.state.city')
        for val in region_obj.browse(cr,uid,region_obj.search(cr,uid,[])):
#assuming country ops code and region ops code is updated in ERP
            if val.country_id.ops_id > 0 and val.state_id.ops_id > 0:
                dict={
                      'ERPID':val.id,
                      'CITYNAME':val.name,
                      'CITYNAMEARABIC':val.arabic_name,
                      'CITYCODE':val.code,
                      'COUNTRYOPSID':val.country_id.ops_id,
                      'COUNTRYERPID':val.country_id.id,
                      'REGIONOPSID':val.state_id.ops_id,
                      'REGIONERPID':val.state_id.id,
                      }
                res.append(dict)
        return res
    
    def UpdateRecord(self,cr,uid,vals):
        if isinstance(vals,(list,tuple)):
            for dict in vals:
                if dict.get('ERPID',False) and dict.get('OPSID',False):
                    self.pool.get('res.state.city').write(cr,uid,[dict['ERPID']],{'ops_id':dict['OPSID']})
        else:
            if vals.get('ERPID',False) and vals.get('OPSID',False):
                    self.pool.get('res.state.city').write(cr,uid,[vals['ERPID']],{'ops_id':vals['OPSID']})
        return True
    
    def CreateRecord(self,cr,uid,vals):
        if vals.get('CITYCODE',False) and vals.get('CITYNAME',False):
            city_id=self.search(cr,uid,[('name','=',vals['CITYNAME']),('code','=',vals['CITYCODE'])])
            if not city_id:
                city_id=self.pool.get('res.state.city').create(cr,uid,{'name':vals['CITYNAME'],'code':vals['CITYCODE'],'arabic_name':vals['CITYNAMEARABIC'],'ops_id':vals['OPSID'],'country_id':vals['COUNTRYERPID'],'state_id':vals['REGIONERPID']},context={})
        return city_id

class res_bank(osv.osv):
    _inherit='res.bank'
    _columns={
              'ops_id':fields.char('Bank OPS ID'),
              }
    def ListRecord(self,cr,uid):
        res=[]
        dict={}
        region_obj=self.pool.get('res.bank')
        for val in region_obj.browse(cr,uid,region_obj.search(cr,uid,[])):
#assuming country ops code and region ops code is updated in ERP
                dict={
                      'ERPID':val.id,
                      'BANKNAME':val.name,
                      'BANKBIC':val.bic,
                      }
                res.append(dict)
        return res
    
    def UpdateRecord(self,cr,uid,vals):
        if isinstance(vals,(list,tuple)):
            for dict in vals:
                if dict.get('ERPID',False) and dict.get('OPSID',False):
                    self.pool.get('res.bank').write(cr,uid,[dict['ERPID']],{'ops_id':dict['OPSID']})
        else:
            if vals.get('ERPID',False) and vals.get('OPSID',False):
                    self.pool.get('res.bank').write(cr,uid,[vals['ERPID']],{'ops_id':vals['OPSID']})
        return True
    
    
    def CreateRecord(self,cr,uid,vals):
        if vals.get('IDENTIFIERCODE',False) and vals.get('BANKNAME',False):
            bank_id=self.search(cr,uid,[('name','=',vals['BANKNAME']),('bic','=',vals['IDENTIFIERCODE'])])
            if not bank_id:
                bank_id=self.pool.get('res.bank').create(cr,uid,{'name':vals['BANKNAME'],'bic':vals['IDENTIFIERCODE'],'ops_id':vals['OPSID'],'country_id':vals.get('COUNTRYERPID',False)},context={})
        return bank_id

PURCHASE_ORDER_DIC={
           'PURCHASEORDERNO':'ops_order_id',  
           'PURCHASEDATE':'date_order',
           'PURCHASEMETHOD':'invoice_method',
           'VENDORNO':'partner_id',
           'PROJECTCODE':'project_code',
           'PURCHASETYPE':'purchase_type',
           'LOCATIONSERIALCOUNTER':'location_serial_counter',
           
           'QUOTATIONNUMBER':'partner_ref',
           'RECORDSTATUS':'status',
          # 'PAYMENTSTATUS':'',
           'TOTALAMOUNT':'po_amount',
          # 'DISCOUNTACT':'discount_type',
         #  'SERVICEACT':'service_type',
          # 'DEDUCTIONACT':'deduction_type',
           'DISCOUNTAMOUNT':'discount_value',
           'DEDUCTIONAMOUNT':'deduction_value',
           'SERVICEAMOUNT':'service_amt',
           'NETAMOUNT':'amount_total',
          # 'EXPENSETYPE':'revenue_type',
           'REIMBURSESTATUS':'reimurses_status',
           'REIMBURSECOMMAMOUNT':'reimurses_com_amt',
           'REIMBURSABLEAMOUNT':'reimurses_total_amt',
          
#           'INVOICENUMBER':'origin',
#           'INSTALLMENTS':'',
#           'SQLREFERENCENO':'',
#           'VENDORSTATUS':'',
#           'REPORTCOUNT':'',
#           'VENDORUPDATEDDATE':'',
#           'ISMANUALPURCHASE':'',
#            'DESC3':'',
#           'DESC2':'',
#           'DESC1':'',
#           'PRricelist_id':'pricelist_id',
#           'product_id':'product_id',
#           'order_line':'order_line'
   }

class purchase_order(osv.osv):
    _inherit='purchase.order'
    
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'deduction_amt':0.0,
                'service_amt':0.0,
                'discount_amt':0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['deduction_amt']=order.deduction_amt
            res[order.id]['service_amt']=order.service_amt
            res[order.id]['discount_amt']=order.discount_amt
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] + res[order.id]['deduction_amt'] + res[order.id]['service_amt'] -res[order.id]['discount_amt']
        return res
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    def check_material(self,cr,uid,vals):
        print "check material =========",vals,type(vals)
        for val in vals:
            if isinstance(val,dict):
                print val,"check request=============="
                if val.get('REQUESTNO',False) and val.get('REQUESTDETAILID',False):
                    return True
                else:
                    if not val.get('REQUESTNO',False):
                        error="Please send 'REQUESTNO' "
                    elif not val.get('REQUESTDETAILID',False):
                        error="Please send 'REQUESTDETAILID' "
                    else:
                        error='Please Create Material Request First'
                    return error
            
    _columns={
              'ops_order_id':fields.char('OPS ID'),
              'purchse_type':fields.char('Purchase Type'),
              'project_code':fields.char('Project Code'),
              'purchase_type':fields.char('Purchase Type'),
              'analytic_id':fields.many2one('account.analytic.account','Cost Center'),
              'location_serial_counter':fields.integer('Location Serial Number'),
              'po_amount':fields.float('PO Amount'),
              'discount_type':fields.selection([('value','Value'),('percentage','Percentage')],'Discount Type'),
              'discount_amt':fields.float('Discount'),
              'discount_value':fields.integer('Discount Value'),
              'service_type':fields.char('Service Type'),
              'deduction_type':fields.selection([('value','Value'),('percentage','Percentage')],'Deduction Type'),
              'deduction_value':fields.integer('Deduction Value'),
              'deduction_amt':fields.float('Deduction'),
              'service_amt':fields.float('Service Amount'),
              'revenue_type':fields.char('Revenue Type'),
              'status':fields.char('Record Status'),
              'reimurses_status':fields.char('Reimburse Status'),
              'reimurses_com_amt':fields.integer('Reimburse Commission'),
              'reimurses_total_amt':fields.float('Reimburse Total'),
              'amount_untaxed': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Untaxed Amount',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The amount without tax", track_visibility='always'),
        'amount_tax': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Taxes',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums", help="The tax amount"),
        'amount_total': fields.function(_amount_all, digits_compute= dp.get_precision('Account'), string='Total',
            store={
                'purchase.order.line': (_get_order, None, 10),
            }, multi="sums",help="The total amount"),
              
              
              }

#    def onchange_discount(self,cr,uid,ids,discount_type,discount_value,total,context=None):
#        result=0.0
#        res={}
#        if discount_type:
#            if discount_type == 'percentage':
#                result= (total*discount_value)/100
#            elif discount_type == 'value':
#                result=discount_value
#        #print "result=====================",result
#        res.update({'discount_amt': result})
#        #print "===================onchange======================",res,result
#        return {'value':res }
    
#    def onchange_deduction(self,cr,uid,ids,discount_type,discount_value,total,context=None):
#        result=0.0
#        if discount_type:
#            if discount_type == 'percentage':
#                result= (total*discount_value)/100
#            elif discount_type == 'value':
#                result=discount_value
#        return {'value': {'deduction_amt': result}}
    _defaults={
              'pricelist_id': lambda self, cr, uid, context: context.get('partner_id', False) and self.pool.get('res.partner').browse(cr, uid, context['partner_id']).property_product_pricelist_purchase.id,
               
               }
    def CreateRecord(self,cr,uid,vals):
        print "==============purchase order==========================",vals
        dic={}
        ids=[]
        value={}
        val1=vals['DetailData']
        del vals['DetailData']
        response=self.check_material(cr,uid,val1)
        if response == True:
            analytic_obj=self.pool.get('account.analytic.account')
            for key,value in vals.iteritems():
                dic[PURCHASE_ORDER_DIC.get(key)] =  value 
            #location_id=self.pool.get('location.setting').search(cr,uid,[])[0]
            dic.update({'name':dic['ops_order_id'],'invoice_method':'manual'})
            partner_id=self.pool.get('res.partner').search(cr,uid,[('ops_code','=',dic['partner_id'])])
            partner_id = partner_id and partner_id[0] if isinstance (partner_id,(list,tuple)) else partner_id
            
            pricelist_id=self.pool.get('res.partner').browse(cr, uid, partner_id).property_product_pricelist_purchase.id
            self.onchange_pricelist(cr, uid, ids, pricelist_id, context=None)
            #self.onchange_warehouse_id(cr, uid, ids, warehouse_id)
            self.onchange_partner_id(cr, uid, ids, partner_id)
            dic['partner_id']=partner_id or False
            dic ['pricelist_id']=pricelist_id or False
            dic['location_id']=16
            dic.update({'name':dic['ops_order_id'],'invoice_method':'picking'})
            if dic['project_code'] :
                if dic['location_serial_counter'] :
                    ref = str(dic['project_code']) + '0'*(3-len(str(dic['location_serial_counter']))) + str(dic['location_serial_counter'])
                else:
                    ref =  str(dic['project_code'])
                # Assuming Project already available in analytic account otherwise we will not create and pass as False    
                dic['analytic_id'] = analytic_obj.search(cr, uid, [('code','=',ref)]) and analytic_obj.search(cr, uid, [('code','=',ref)])[0] or False
                #print "dic['analytic_id']=============================",dic['analytic_id']
                
                #discount=self.onchange_discount(cr,uid,ids,dic['discount_type'],dic['discount_value'],dic['po_amount'])
                #dic['discount_amt']=discount['value']['discount_amt']
                #deduction=self.onchange_deduction(cr,uid,ids,dic['deduction_type'],dic['deduction_value'],dic['po_amount'])
                #dic['deduction_amt']=deduction['value']['deduction_amt']
                purchase_id=self.search(cr, uid, [('ops_order_id','=',dic['ops_order_id'])])
                purchase_id = self.write(cr,uid,purchase_id[0],dic) and purchase_id[0] \
                                     if purchase_id else self.create(cr,uid,dic,context={})
            #print "purchase id==================================",purchase_id
            order_line=self.pool.get('purchase.order.line').CreateRecord(cr,uid,val1)
            netsvc.LocalService("workflow").trg_validate(uid, 'purchase.order', purchase_id, 'purchase_confirm', cr)
            invoice=self.action_invoice_create(cr, uid, [purchase_id], context={})
            #print "ops     invoice==============",invoice
            context=self.view_invoice(cr, uid, [purchase_id], context={})
            #print "invoice id=======================================",context
            if context.get('res_id',False):
                self.pool.get('account.invoice').write(cr,uid,context['res_id'],{'cost_analytic_id':8260})
            netsvc.LocalService("workflow").trg_validate(uid, 'account.invoice', context['res_id'], 'invoice_open', cr)
           #value['PurchaseERPID'] = purchase_id
            return purchase_id
        else:
            return response
    
PURCHASE_ORDER_LINE_DIC = {
                            'PURCHASEORDERNO': 'order_id' ,
                            'PURCHASEDETAILID': 'ops_id',
                            'QUOTATIONNUMBER': 'quotation_number' ,
                            #'RECORDSTATUS': 'status',
                            'REQUESTNO' : 'requisition_id',
                            'REQUESTDETAILID' : 'requisition_line_id',
                            'ITEMPRICE' : 'price_unit',
                             'ITEMTOTAL' : 'price_subtotal',
                             'UNITDISCOUNT' : 'unit_discount',
                             'VENDORSTATUS' :'vendor_status',
                             'ADDITIONAL_CHARGE' : 'additional_charge_per_qty',
                             'QUANTITY' : 'product_qty',
                             'QDETNO' : 'quotation_detail_number',
                            } 
  
class purchase_order_line(osv.osv):
    _inherit='purchase.order.line'
    
    def _amount_line(self, cr, uid, ids, prop, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for line in self.browse(cr, uid, ids, context=context):
            taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total']) - (line.product_qty)*line.additional_charge_per_qty
        return res
    _columns={
              'requisition_id':fields.many2one('purchase.requisition','Requisition'),
              'requisition_line_id':fields.many2one('purchase.requisition.line','Requisition Line'),
              'ops_id':fields.char('Line OPS ID'),
              'additional_charge_per_qty':fields.float('Additional Charge / Unit'),
              'quotation_detail_number':fields.char('Quotation Detail Number'),
              'quotation_number':fields.char('Quotation Number'),
              'vendor_status':fields.char('Vendor Status'),
              'status':fields.char('Status'),
              'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
              }
    
    
   
    def CreateRecord(self,cr,uid,vals):
        dic={}
        line={}
        purchase_obj=self.pool.get('purchase.order')
        requisition_obj=self.pool.get('purchase.requisition')
        requisition_line_obj=self.pool.get('purchase.requisition.line')
#        analytic_obj=self.pool.get('account.analytic.account')
        for val in vals:
            for key,value in val.iteritems():
                dic[PURCHASE_ORDER_LINE_DIC.get(key)] =  value
            requisition_id=requisition_obj.search(cr,uid,[('ops_id','=',dic['requisition_id'])])
            requisition_line_id=requisition_line_obj.search(cr,uid,[('ops_id','=',dic['requisition_line_id'])])
            order_id=purchase_obj.search(cr,uid,[('ops_order_id','=',dic['order_id'])])
            #print requisition_line_id,"11111111111"
            line_obj=requisition_line_obj.browse(cr,uid,requisition_line_id[0])
            if order_id:
                dic.update({'order_id':order_id[0],'requisition_id':requisition_id[0],'requisition_line_id':requisition_line_id[0],'product_id':line_obj.product_id.id,'name':line_obj.product_id.name,
                            'date_planned':str(datetime.datetime.today())})
               
            purchase_line_id=self.search(cr, uid, [('ops_id','=',dic['ops_id'])])
            purchase_line_id = self.write(cr,uid,purchase_line_id[0],dic) and purchase_line_id[0] \
                                     if purchase_line_id else self.create(cr,uid,dic,context={})
            line['DetailERPID'] = purchase_line_id
        return line




    
#    def write(self, cr, uid, ids, vals, context={}):
#        print vals
#        error
#        return True

payment_term_dic={
                  'PURCHASEORDERNO':'purchase',
                  'PAYMENTID':'pos_payment_id',
                  'PAYABLEAMOUNT':'payable_amt',
                  'PLUSDAYS':'plus_days',
                  'DUEDATE':'due_date',
                  'PAYMENTREMARKS':'payment_remarks',
                  'REFERENCENO':'ref_number',
                  'INSTALLMENTNO':'installment_no',
                  'PAYMENTTYPE':'payment_type',
                  'APPROVALSTATUS':'approval_status',
                  'BANKSTATUS':'bank_status',
                  'CHEQUENO':'cheque_no',
                  'BANKACCOUNTNO':'bank_account_no',
                  }


class account_invoice_payment(osv.osv):
    _name='account.invoice.payment'
    #_rec_name ='purchase'
    _columns={
              'invoice_id':fields.many2one('account.invoice','Invoice'),
             # 'invoice_id_new':fields.many2one('account.invoice','Invoice'),
              'purchase':fields.char('Purchase'),
              'pos_payment_id':fields.char('OPS Code'),
              'payable_amt':fields.float('Payable Amount'),
              'plus_days':fields.char('Plus Days'),
              'due_date':fields.date('Due Date'),
              #'active':fields.char('Payment Status'),
              'payment_remarks':fields.char('Payment Remarks'),
              'ref_number':fields.char('Reference Number'),
              'installment_no':fields.char('Installment'),
              'payment_type':fields.selection([('bank','Bank'),('cash','Cash')],'Payment Type'),
              'approval_status':fields.char('Approval Status'),
              'bank_status':fields.char('Bank Status'),
              'cheque_no':fields.char('Check No'),
              'bank_account_no':fields.char('Bank Account No'),
              }
    
    
    def CreateRecord(self,cr,uid,vals):
        dic={}
        account_obj=self.pool.get('account.invoice')
        for val in vals:
            for key,value in val.iteritems():
                dic[payment_term_dic.get(key)] =  value
            invoice_id=account_obj.search(cr,uid,[('origin','=',dic['purchase'])])
            if invoice_id:
                dic['invoice_id']=invoice_id[0]
            payment_id=self.search(cr, uid, [('pos_payment_id','=',dic['pos_payment_id'])])
            payment_id = self.write(cr,uid,payment_id[0],dic) and payment_id[0] \
                                     if payment_id else self.create(cr,uid,dic,context={})
        return payment_id
    
    


#class res_partner(osv.osv):
#    _inherit='res.partner'
#    _columns={
#              
#              }
#    def Create_Record(self,cr,uid,vals):  
#        dic={}  
#        for key,value in vals.iteritems():
#            dic[ACCOUNT_DETAILS.get(key)] =  value 
#        if dic('ops_code',False):
#            partner_id=self.search(cr,uid,[('ops_code','=',dic['ops_code'])])
#            partner_id = self.write(cr,uid,partner_id,dic) if partner_id else False
#            
#        return partner_id

INVOICE_DATA_DIC = {
                'LOANCODE':'ops_loan_id',
                'ACCOUNTANTID':'partner_id',
                #'LOANSTATUS':'',
               # 'ROLLBACKSTATUS':'',
                #'ROLLBACKREMARK':'',
                'AMOUNT':'amount_total',
                'RMRGRANDTOTAL':'rmr_grant_total',
                'RMRAMOUNT':'rmr_total',
                'ISBUDGET':'is_budget',
                'CREATEDDATE':'date_invoice',
                #'LOAN_DATAIL_DATA':'LOAN_DATAIL_DATA_LIST',
                #'LOAN_REQUEST_DETAIL':'LOAN_REQUEST_DETAIL_LIST',
                }


class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
          'ops_loan_id':fields.float('Ops Loan Id'),
          'rmr_total':fields.float('Rmr Total'),
          'rmr_grant_total':fields.integer('Rmr Grant Total'),
          'is_budget':fields.boolean('Is Budget'),
          'details_line':fields.one2many('account.invoice.details','detail_id','Account Invoiced Details'),
          'payment_terms':fields.one2many('account.invoice.payment','invoice_id','Payment Terms'),
          'ops_details_request_id':fields.integer('Ops details request id'),
          'invoice_details_id':fields.many2one('account.invoice.details','Invoice Details Id'),
          'unit_discount':fields.float('Unit Discount'),
          'service_charge':fields.float('Service Charge'),
          }
    
    def CreateRecord(self,cr,uid,vals):
        dic={}
        ids=[]
        invoice_line=self.pool.get('account.invoice.line')
        detail_line=self.pool.get('account.invoice.details')
        analytic_obj=self.pool.get('account.analytic.account')
        partner=self.pool.get('res.partner')
        invoice_line_list=vals['LOAN_DATAIL_DATA']
        detail_line_list=vals['LOAN_REQUEST_DEATIL']
        del vals['LOAN_DATAIL_DATA']
        del vals['LOAN_REQUEST_DEATIL']
        for key,value in vals.iteritems():
            dic[INVOICE_DATA_DIC.get(key)] =  value 
        if dic('partner_id',False):
            partner_id=partner.search(cr,uid,[('ops_accountant','=',dic['partner_id'])])
            if partner_id:
                dic['partner_id'] = partner_id[0]
                partner_obj = partner.browse(cr,uid,partner_id[0])
                
                
                if partner_obj.location_serial_counter :
                    ref = str(partner_obj.project_code) + '0'*(3-len(str(partner_obj.location_serial_counter))) + str(partner_obj.location_serial_counter)
                else:
                    ref =  str(partner_obj.project_code)
            # Assuming Project already available in analytic account otherwise we will not create and pass as False    
                dic['cost_analytic_id'] = analytic_obj.search(cr, uid, [('code','=',ref)]) and analytic_obj.search(cr, uid, [('code','=',ref)])[0] or False
                dic['account_id']=partner_obj.property_account_payable.id
            # Assuming Project already available in analytic account otherwise we will not create and pass as False    
                #dic['analytic_id'] = analytic_obj.search(cr, uid, [('code','=',obj.project_code)]) and analytic_obj.search(cr, uid, [('code','=',obj.project_code)])[0] or False
            #dic['partner_id'] = partner_id[0] if partner_id else False
            ops_loan_id=self.search(cr,uid,[('ops_loan_id','=',dic['ops_loan_id'])])
            ops_loan_id = self.write(cr,uid,ops_loan_id,dic) if ops_loan_id else self.create(cr,uid,dic,context=None)
        detail_line.CreateRecord(cr,uid,detail_line_list)
        invoice_line.CreateRecord(cr,uid,invoice_line_list)
        
        return ops_loan_id


INVOICE_DEATIL_LINE_DATA={
                    'LOANCODE':'detail_id',
                    'LOANDETAILID':'ops_details_id',
                    'INVOICEVENDOR':'invoice_vendor',
                    'INVOICENUMBER':'ops_invoice_number',
                    'INVOICEDATE':'invoice_date',
                    'INVOICEAMOUNT':'invoice_amt',
                    #'BUDGETENTITYID':'',
                    #'BUDGETDETAILID':'',
                    'DISCOUNT':'discount',
                    'RMRNUMBER':'rmr_number',
                    'RMRAMOUNT':'rmr_amount',
                    #'INVOICETYPE':'',
                    #'TRANSACTIONTYPE':'',
                    #'RECORDSTATUS':'',
                    }



class account_invoice_details(osv.osv):
    _name='account.invoice.details'
    _columns={
              'detail_id':fields.many2one('account.invoice','Account Invoice'),
              'invoice_id':fields.float('invoice id'),
              'ops_details_id':fields.integer('Ops Details ID'),
              'invoice_vendor':fields.char('Invoice Vendor',size=64),
              'ops_invoice_number':fields.char('Ops Invoice Number',size=64),
              'invoice_date':fields.date('Invoice Date'),
              'invoice_amt':fields.float('Invoice Amount'),
              'discount':fields.float('Discount Amount'),
              'rmr_number':fields.char('RMR Number'),
              'rmr_amount':fields.char('RMR Amount'),
              }
    
    def CreateRecord(self,cr,uid,list):
        dic={}
        invoice=self.pool.get('account.invoice')
#        invoice_detail=self.pool.get('account.invoice.details')
        for vals in list:
            for key,value in vals.iteritems():
                dic[INVOICE_DEATIL_LINE_DATA.get(key)] =  value
            if dic('detail_id',False):
                invoice_id=invoice.search(cr,uid,[('ops_loan_id','=',dic['detail_id'])])
                if invoice_id:
                    dic['invoice_id']=invoice_id[0]
                    ops_details_id=self.search(cr,uid,[('ops_details_id','=',dic['ops_details_id'])])
                    ops_details_id = self.write(cr,uid,ops_details_id[0],dic) and ops_details_id[0] \
                                 if ops_details_id else self.create(cr,uid,dic,context={})
        return ops_details_id

INVOICE_LINE_DATA=   {
                    'LOANREQUESTDETAILID':'ops_details_request_id',
                    'LOANREQUESTNO':'ops_invoice_id',
                    'LOANDETAILID':'invoice_details_id',
                    #'EMPLOYEECODE':'',
                    'ITEMNUMBER':'product_id',
                    'QUANTITY':'quantity',
                    'ITEMDESC':'name',
                    'UNITPRICE':'price_unit',
                    'UNITDISCOUNT':'unit_discount',
                    'SERVICECHARGE':'service_charge',
                    #'UNITTYPE':'',
                    #'RQSTDETAILSTATUS':'',
                    #'BUDGETDETAILID':'',
                    #'BUDGETENTITYID':'',
                    'LOANCODE':'invoice_id',
                    }   

 
class account_invoice_line(osv.osv):
    _inherit='account.invoice.line'
    _columns={
              'ops_details_request_id':fields.integer('Ops details request id'),
              'ops_invoice_id':fields.integer('OPS Invoice ID',readonly=True),
              'invoice_details_id':fields.many2one('account.invoice.details','Invoice Details Id'),
              'unit_discount':fields.float('Unit Discount'),
              'service_charge':fields.float('Service Charge'),
              }
    
    def CreateRecord(self,cr,uid,list):
        dic={}
        product=self.pool.get('product.product')
        invoice=self.pool.get('account.invoice')
        invoice_detail=self.pool.get('account.invoice.details')
        for vals in list:
            for key,value in vals.iteritems():
                dic[INVOICE_LINE_DATA.get(key)] =  value
            if dic('invoice_id',False):
                invoice_id=invoice.search(cr,uid,[('ops_loan_id','=',dic['invoice_id'])])
                product_id=product.search(cr,uid,[('ops_code','=',dic['product_id'])])
                if invoice_id:
                    dic['invoice_id']=invoice_id[0]
                    invoice_details_id=invoice_detail.search(cr,uid,[('ops_detail_id','=',dic['invoice_details_id'])])
                    dic['invoice_details_id']= invoice_details_id[0] if invoice_details_id else False
                    dic['account_id']=self._default_account_id(self, cr, uid, context=None)
                    dic['product_id']= product_id[0] if product_id else False
                    ops_details_request_id=self.search(cr,uid,[('ops_details_request_id','=',dic['ops_details_request_id'])])
                    ops_details_request_id = self.write(cr,uid,ops_details_request_id[0],dic) and ops_details_request_id[0] \
                                 if ops_details_request_id else self.create(cr,uid,dic,context={})
        return ops_details_request_id
    

      



    
#
#    def CreateRecord(self,cr,uid,list):
#        for val in list:
#            val
#            
#        return detail_id

