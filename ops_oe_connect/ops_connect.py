from openerp.osv import fields, osv


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
                'ITEMSTATUS':'active',
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

PURCHASE_ORDER_DIC={
           'PURCHASEORDERNO':'ops_order_id',  #ops_id
           'PURCHASEDATE':'date_order',
           'PURCHASEMETHOD':'invoice_method',
           'VENDORNO':'partner_id',
           
           'PROJECTCODE':'PROJECTCODE',
           'PURCHASETYPE':'purchase_type',
           'LOCATIONSERIALCOUNTER':'location_serialcounter',
           
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
                'ops_code':fields.integer('OPS Code'),
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
                category_id = [self.create(cr,uid,dic)]
            return category_id[0]
        else:
            return False

product_category()


class product_product(osv.osv):
    
    _inherit="product.product"
    
    _columns={
            'ops_code':fields.integer('OPS Code'),
            'name_arabic':fields.char('Arbic Name',size=64),
            
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
                                 if product_id else self.create(cr,uid,dic)
                return product_id
            return False  
        else:    
            return False
    
product_product()


class res_bank(osv.osv):
    
    _inherit="res.bank"
    
    _columns={
            'ops_id':fields.char('OPS Bank ID',size=64),     
          }

    
class res_partner(osv.osv):
    _inherit='res.partner'
    _columns={
              'ops_code':fields.integer('OPS Code'),
              'phone_ext':fields.char('Phone Ext',size=64),
              'crno':fields.char('Company Registration Number',size=64),
              'fax_ext':fields.char('Fax Ext',size=64),
             }
    
    def CreateRecord(self, cr, uid, vals, context=None):
        dic = {}
        
        partner_obj=self.pool.get('res.partner')
        country_obj=self.pool.get('res.country')
        state_obj=self.pool.get('res.country.state')
        bank_obj=self.pool.get('res.bank')
        partner_bank_obj=self.pool.get('res.partner.bank')
        
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
                             if partner_id else self.create(cr,uid,dic)                  
            
            # if contact name then one record will create for contact and map to vendor
            if dic.get('contact_name',False): 
                domain = [('parent_id','=',partner_id),('name','=',dic['contact_name'])]
                contact_id = partner_obj.search(cr, uid, domain)
                  
                contact_dic = { 'name': dic['contact_name'],'parent_id':partner_id ,
                                'phone': dic.get('contact_phone',False),
                                'phone_ext': dic.get('contact_phone_ext',False), }
                contact_id = self.write(cr,uid,contact_id[0],contact_dic) and contact_id[0] \
                                 if contact_id else self.create(cr,uid,contact_dic)
                
            # if owner name then one record will create for owner and map to vendor   
            if dic.get('owner_name',False):  
                domain = [('parent_id','=',partner_id),('name','=',dic['owner_name'])]
                owner_id = partner_obj.search(cr, uid, domain)
                owner_dic ={ 'name': dic['owner_name'],'parent_id':partner_id,
                             'phone': dic.get('owner_phone',False),
                             'email': dic.get('owner_email',False),}
                owner_id = self.write(cr,uid,owner_id[0],owner_dic) and owner_id[0] \
                                 if owner_id else self.create(cr,uid,owner_dic)
             
            # if ceo name then one record will create for CEO and map to vendor
            if dic.get('ceo_name',False): 
                domain = [('parent_id','=',partner_id),('name','=',dic['ceo_name'])]
                ceo_id = partner_obj.search(cr, uid, domain) 
                ceo_dic ={ 'name': dic['ceo_name'],
                           'parent_id':partner_id }   
                ceo_id = self.write(cr,uid,ceo_id[0],ceo_dic) and ceo_id[0] \
                                 if ceo_id else self.create(cr,uid,ceo_dic)
                                 
            # if BankID(ops_id) then create bank in OpenERP res.bank     
            # OPS Need to send Bank Name Also     
            if dic.get('ops_id',False):  
                domain = [('ops_id','=',dic['ops_id'])]
                bank_id = bank_obj.search(cr, uid, domain)
                bank_dic ={ 'name': dic['ops_id'],'country': dic['country_id'],
                            'ops_id':  dic.get('ops_id',False),
                            'bic': dic.get('bank_bic',False),}
                bank_id = bank_id[0] if bank_id else bank_obj.create(cr,uid,bank_dic)  
                     
                # if Bank Holder name then one record will create for BankHolderName and map to vendor   
                if dic.get('bank_holder_name',False): 
                    domain =  [('parent_id','=',partner_id),('name','=',dic['bank_holder_name'])]
                    bank_holder_id = partner_obj.search(cr, uid, domain)
                    bank_holder_dic ={ 'name': dic['bank_holder_name'],
                                       'parent_id':partner_id }
                    bank_holder_id = bank_holder_id[0] if bank_holder_id else self.create(cr,uid,bank_holder_dic)
                      
                    # Create vendor Bank account in OpenERP res.partner.bank 
                    #Assuming country of Bank is same as vendor country
                    if  dic.get('acc_number',False):   
                        partner_bank_dic = { 'acc_number': dic['acc_number'],'state' : 'bank',
                                             'bank_name' : dic.get('bank_name',False),  
                                             'bank_bic' : dic.get('bank_bic',False),
                                             'owner_name': dic.get('bank_holder_name',False),
                                             'bank': bank_id,
                                             'partner_id' : partner_id,'country_id':dic['country_id'],}
                    # According to me if bank account type is IBAN then we need to create another bank record
                    # WE Must need bank identifier code or swift code for IBAN Account Bank
                    # Assuming IBAN and Normal both belong to same bank as we are getting only one bankid
#                         if dic.get('bank_bic',False):
#                             partner_bank_dic['state'] = 'iban'
                        domain = [('partner_id','=',bank_holder_id),('bank','=',bank_id),('acc_number','=',dic['acc_number'])]
                        partner_bank_id = partner_bank_obj.search(cr, uid, domain)    
                        if not partner_bank_id:
                            partner_bank_id = partner_bank_id[0] if partner_bank_id \
                                      else partner_bank_obj.create(cr, uid,partner_bank_dic)
                        
                                                
        return partner_id  
        
        return True
    
res_partner()

MATERIAL_DIC = {
            'REQUESTNO':'ops_id',
            'REQUESTDATE':'date_start',
            'REQUESTSTATUS':'state',
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
            'RQSTDETAILSTATUS':'state',
            'REQUESTDETAILID':'ops_id',
            }



class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"
    
    _columns={
              'analytic_id':fields.many2one('account.analytic.account','Cost Center'),
              'ops_id':fields.integer('OPS Request No'),
              'rmrnumber':fields.char('Revenue ref Number',size=64),
              
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
        if dic['project_code'] :
            if dic['location_serial_counter'] :
                ref = str(dic['project_code']) + '0'*(3-len(str(dic['location_serial_counter']))) + str(dic['location_serial_counter'])
            else:
                ref =  str(dic['project_code'])
            # Assuming Project already available in analytic account otherwise we will not create and pass as False    
            dic['analytic_id'] = analytic_obj.search(cr, uid, [('code','=',ref)]) and analytic_obj.search(cr, uid, [('code','=',ref)])[0] or False
                      
        requisition_id = self.search(cr, uid, [('ops_id','=',dic['ops_id'])])
        requisition_id = self.write(cr,uid,requisition_id[0],dic) and requisition_id[0] \
                                 if requisition_id else self.create(cr,uid,dic)
        
        return requisition_id  
         
    
purchase_requisition()

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    
    _columns={
              'description' : fields.char('Description',size=64),
              'ops_id':fields.integer('OPS Request Detail ID'),
              }
    
    
    def CreateRecord(self, cr, uid, vals, context=None):
        dic = {  }
        requisition_obj=self.pool.get('purchase.requisition')
        product_obj=self.pool.get('product.product')
        
        for key,value in vals.iteritems():
            dic[MATERIAL_LINE_DIC.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
        requisition_id = requisition_obj.search(cr, uid, [('ops_id','=',dic['requisition_id'])])
        product_id = product_obj.search(cr, uid, [('ops_code','=',dic['product_id'])])
        if requisition_id and product_id:
            dic['requisition_id'] = requisition_id[0]
            dic['product_id'] = product_id[0]
            requisition_line_id = self.search(cr, uid, [('ops_id','=',dic['ops_id'])])
            requisition_line_id = self.write(cr,uid,requisition_line_id[0],dic) and requisition_line_id[0] \
                                 if requisition_line_id else self.create(cr,uid,dic)
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
              'ops_id':fields.integer('OPS Country ID',readonly=True),
              
              } 
    def ViewRecord(self,cr,uid):
        res=[]
        dict={}
        country_obj=self.pool.get('res.country')
        country_ids=country_obj.search(cr,uid,[])
        for val in country_obj.browse(cr,uid,country_ids):
            #dict={}
            #for key,value in COUNTRY_LIST_DIC.iteritems():
                #print val
                #print "key valu=================",key,getattr(val,value)
                #if isinstance(value, (object,record)):
                 #   value=value.id
                #dict.update({key:getattr(val,value)})
                #dic[COUNTRY_LIST_DIC.get(key)] = value.encode('utf-8') if isinstance(value, (str, unicode)) else value
            
            dict={
                  'ERPID':val.id,
                  'NAME':val.name,
                  'NAMEARABIC':(val.arabic_name.encode('utf-8')),
                  'CODE':val.code,
                  'CALLINGCODE':val.calling_code,
                  'CURRENCYCODE':val.currency_id.id,
                  }
            res.append(dict)
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
               'ops_id':fields.integer('OPS Region ID',readonly=True),
               
               }
    def ViewRecord(self,cr,uid):
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
    
class res_state_city(osv.osv):
    _inherit='res.state.city'
    _columns={
              'ops_id':fields.integer('OPS City ID',readonly=True),
              }
    
    def ViewRecord(self,cr,uid):
        res=[]
        dict={}
        region_obj=self.pool.get('res.state.city')
        for val in region_obj.browse(cr,uid,region_obj.search(cr,uid,[])):
#assuming country ops code and region ops code is updated in ERP
            if val.country_id.ops_id >0 and val.state_id.ops_id > 0:
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
    def CreateRecord(self, cr, uid, vals, context=None):
        dic = {  }
        
        if vals.get('COUNTRYERPID',False) and vals.get('REGIONERPID',False) and vals.get('CITYNAME',False):
            city_id=self.search(cr,uid,[('name','=',vals['CITYNAME']),('country_id','=',vals['COUNTRYERPID']),('region_id','=',vals['REGIONERPID'])])
            if vals.get('CITYNAMEARABIC',False) and vals.get('CITYCODE',False) and not city_id:
                self.create(cr,uid,ids,vals)
            
            
        return True
            
            
            
            
            
            
        return True