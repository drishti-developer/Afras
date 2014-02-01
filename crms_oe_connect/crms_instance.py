from openerp.osv import fields, osv
import datetime
#from xml.dom.minidom import parse, parseString
from crms_osv import Call
import crms_osv

class crms_instance(osv.osv):
    _name = "crms.instance"
    _columns = {
        'name' : fields.char(string='Server API URL',size=256,required=True),
        'username' : fields.char(string='Username',size=256,required=True),
        'password' : fields.char(string='password',size=256,required=True),
        'erp_ip' : fields.char(string='ERP IP Address',size=256,required=True),
        'active':fields.boolean(string='Active'),
        'environment':fields.selection([('test', 'Test'), ('production', 'Production'),], 'Environment',required=True),
        'last_currency_exported_date': fields.datetime('Last Updated/Created Currency Date'),
        'last_country_exported_date': fields.datetime('Last Updated/Created Country Date'),
        'last_region_exported_date': fields.datetime('Last Updated/Created Region Date'),
        'last_city_exported_date': fields.datetime('Last Updated/Created City Date'),
        'last_area_exported_date': fields.datetime('Last Updated/Created Area Date'),
        'last_branch_exported_date': fields.datetime('Last Updated/Created Branch Date'),
        'last_manufacturer_exported_date': fields.datetime('Last Updated/Created Manufacturer Date'),
        'last_cartype_exported_date': fields.datetime('Last Updated/Created CarType Date'),
        'last_model_exported_date': fields.datetime('Last Updated/Created Model Date'),
        'last_car_exported_date': fields.datetime('Last Updated/Created Car Date'),
        'last_customer_exported_date': fields.datetime('Last Updated/Created Customer Date'),
        }
    
    def onchange_environment(self, cr, uid, ids, environment, context=None):
        value = {}
        if environment:
            if environment=='test':
                value = {'name': "http://117.218.242.69/NLCO/admin/updateCRMS"}
            else:
                value = {'name': "http://172.16.1.50/NLCO/admin/updateCRMS"}
                
        return {'value': value}
    
    #1. CURRRENCY CREATE / UPDATE CODE.
    def add_update_currency(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        currency_obj = self.pool.get('res.currency')#Currency instance
        
        domain = []
        if self_brw.last_currency_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_currency_exported_date),('write_date','>=',self_brw.last_currency_exported_date),('crms_id','=',False)] #domain filter
            
        currency_ids = currency_obj.search(cr,uid,domain) # Searching Currency Value Accordingly
        if currency_ids :
            currency_str = "<CurrencyList>\n"# Currency List String
            for currency_brw in currency_obj.browse(cr,uid,currency_ids):
                crms_str = False
                if currency_brw.crms_id:
                    crms_str = "\n<CRMSCurrencyID>%s</CRMSCurrencyID>"%(currency_brw.crms_id)
                    
                currency_str += """<Currency>
<ERPCurrencyID>%s</ERPCurrencyID>%s
<CurrencyName>%s</CurrencyName>
<CurrencyCode>%s</CurrencyCode>
</Currency>\n"""%(currency_brw.id, (crms_str or ''), currency_brw.currency_name, currency_brw.name)

            currency_str += "</CurrencyList>"
            
            responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(currency_str, 'CurrencyCreateRequest', 'CurrencyResponse')
            write = False
            for response_dict in responsearray:
                if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                    write = True  
                    cr.execute("update res_currency set crms_id=%s where id=%s",(int(response_dict.get('CRMSCurrencyID')), response_dict.get('ERPCurrencyID')))
            if write:
                self.write(cr, uid, ids, {'last_currency_exported_date':datetime.datetime.today()}) #Updating the Date
        
        return True
    
    #2. COUNTRY CREATE / UPDATE CODE
    def add_update_country(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        country_obj = self.pool.get('res.country')#Country instance
        
        domain = []
        if self_brw.last_country_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_country_exported_date),('write_date','>=',self_brw.last_country_exported_date),('crms_id','=',False)] #domain filter
            
        country_ids = country_obj.search(cr,uid,domain) # Searching Country Value Accordingly
        if country_ids :
            allow = False
            country_str = "<CountryList>\n"# Country List String
            for country_brw in country_obj.browse(cr,uid,country_ids):
                    
                if country_brw.id and country_brw.name and country_brw.arabic_name and country_brw.code and country_brw.calling_code and country_brw.currency_id and country_brw.currency_id.crms_id:
                    crms_str = False
                    if country_brw.crms_id:
                        crms_str = "\n<CRMSCountryID>%s</CRMSCountryID>"%(country_brw.crms_id)
                    allow = True    
                    country_str += """<Country>
<ERPCountryID>%s</ERPCountryID>%s
<CountryNameInEng>%s</CountryNameInEng>
<CountryNameInAra>%s</CountryNameInAra>
<CountryCode>%s</CountryCode>
<CallingCode>%s</CallingCode>
<ERPCurrencyID>%s</ERPCurrencyID>
<CRMSCurrencyID>%s</CRMSCurrencyID>
</Country>\n"""%(country_brw.id, (crms_str or ''), country_brw.name, country_brw.arabic_name, country_brw.code, country_brw.calling_code, country_brw.currency_id.id, country_brw.currency_id.crms_id)

            country_str += "</CountryList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(country_str, 'CountryCreateRequest', 'CountryResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update res_country set crms_id=%s where id=%s",(int(response_dict.get('CRMSCountryID')), response_dict.get('ERPCountryID')))
                if write:
                    self.write(cr, uid, ids, {'last_country_exported_date':datetime.datetime.today()}) #Updating the Date
        
        return True
    
    #3. REGION CREATE / UPDATE CODE 
    def add_update_region(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])
        region_obj = self.pool.get('res.country.state')# Instance
        
        domain = []
        if self_brw.last_region_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_region_exported_date),('write_date','>=',self_brw.last_region_exported_date),('crms_id','=',False)] #domain filter
            
        region_ids = region_obj.search(cr,uid,domain) # Searching state Value Accordingly
        if region_ids :
            allow = False
            region_str = "<RegionList>\n"# Region List String
            for region_brw in region_obj.browse(cr,uid,region_ids):
                
                if region_brw.name and region_brw.code and region_brw.country_id and region_brw.country_id.crms_id:
                    
                    crms_str = False
                    if region_brw.crms_id:
                        crms_str = "\n<CRMSRegionID>%s</CRMSRegionID>"%(region_brw.crms_id)
                    allow = True    
                    region_str += """<Region>
<ERPRegionID>%s</ERPRegionID>%s
<RegionName>%s</RegionName>
<RegionCode>%s</RegionCode>
<ERPCountryID>%s</ERPCountryID>
<CRMSCountryID>%s</CRMSCountryID>
</Region>\n"""%(region_brw.id, (crms_str or ''), region_brw.name, region_brw.code, region_brw.country_id.id, region_brw.country_id.crms_id)

            region_str += "</RegionList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(region_str, 'RegionCreateRequest', 'RegionResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update res_country_state set crms_id=%s where id=%s",(int(response_dict.get('CRMSRegionID')), response_dict.get('ERPRegionID')))
                if write:
                    self.write(cr, uid, ids, {'last_region_exported_date':datetime.datetime.today()}) #Updating the Date
            
        return True
    
    #4. City CREATE / UPDATE CODE 
    def add_update_city(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        city_obj = self.pool.get('res.state.city')#State instance
        
        domain = []
        if self_brw.last_city_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_city_exported_date),('write_date','>=',self_brw.last_city_exported_date),('crms_id','=',False)] #domain filter
            
        city_ids = city_obj.search(cr,uid,domain) # Searching state Value Accordingly
        if city_ids :
            allow = False
            city_str = "<CityList>\n"# City List String
            for city_brw in city_obj.browse(cr,uid,city_ids):
                crms_str = False
                    
                if city_brw.arabic_name and city_brw.state_id and city_brw.state_id.crms_id :
                    if city_brw.crms_id:
                        crms_str = "\n<CRMSCityID>%s</CRMSCityID>"%(city_brw.crms_id)
                        
                    allow = True    
                    city_str += """<City>
<ERPCityID>%s</ERPCityID>%s
<CityNameInEng>%s</CityNameInEng>
<CityNameInAra>%s</CityNameInAra>
<ERPRegionID>%s</ERPRegionID>
<CRMSRegionID>%s</CRMSRegionID>
<ERPCountryID>%s</ERPCountryID>
<CRMSCountryID>%s</CRMSCountryID>
</City>\n"""%(city_brw.id, (crms_str or ''), city_brw.name, city_brw.arabic_name, city_brw.state_id.id, city_brw.state_id.crms_id, city_brw.country_id.id, city_brw.country_id.crms_id)

            city_str += "</CityList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(city_str, 'CityCreateRequest', 'CityResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update res_state_city set crms_id=%s where id=%s",(int(response_dict.get('CRMSCityID')), response_dict.get('ERPCityID')))
                if write:
                    self.write(cr, uid, ids, {'last_city_exported_date':datetime.datetime.today()}) #Updating the Date
            
        return True
    
    #5. Area CREATE / UPDATE CODE 
    def add_update_area(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        area_obj = self.pool.get('res.city.area')#instance
        
        domain = []
        if self_brw.last_area_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_area_exported_date),('write_date','>=',self_brw.last_area_exported_date),('crms_id','=',False)] #domain filter
            
        area_ids = area_obj.search(cr,uid,domain) # Searching Value Accordingly
        if area_ids :
            allow = False
            area_str = "<AreaList>\n"# Currency List String
            for area_brw in area_obj.browse(cr,uid,area_ids):
                    
                if area_brw.name and area_brw.arabic_name and area_brw.city_id and area_brw.city_id.crms_id :
                    crms_str = False
                    if area_brw.crms_id:
                        crms_str = "\n<CRMSAreaID>%s</CRMSAreaID>"%(area_brw.crms_id)
                        
                    allow = True    
                    area_str += """<Area>
<ERPAreaID>%s</ERPAreaID>%s
<AreaNameInEng>%s</AreaNameInEng>
<AreaNameInAra>%s</AreaNameInAra>
<AreaCode>%s</AreaCode>
<ERPCityID>%s</ERPCityID>
<CRMSCityID>%s</CRMSCityID>
<ERPRegionID>%s</ERPRegionID>
<CRMSRegionID>%s</CRMSRegionID>
<ERPCountryID>%s</ERPCountryID>
<CRMSCountryID>%s</CRMSCountryID>
</Area>\n"""%(area_brw.id, (crms_str or ''), area_brw.name, area_brw.arabic_name, area_brw.code, area_brw.city_id.id, \
              area_brw.city_id.crms_id, area_brw.state_id.id, area_brw.state_id.crms_id, area_brw.country_id.id, area_brw.country_id.crms_id)

            area_str += "</AreaList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(area_str, 'AreaCreateRequest', 'AreaResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update res_city_area set crms_id=%s where id=%s",(int(response_dict.get('CRMSAreaID')), response_dict.get('ERPAreaID')))
                if write:
                    self.write(cr, uid, ids, {'last_area_exported_date':datetime.datetime.today()}) #Updating the Date
            
        return True
    
    #6. Branch CREATE / UPDATE CODE 
    def add_update_branch(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        branch_obj = self.pool.get('sale.shop')#instance
        
        domain = []
        if self_brw.last_branch_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_branch_exported_date),('write_date','>=',self_brw.last_branch_exported_date),('crms_id','=',False)] #domain filter
            
        branch_ids = branch_obj.search(cr,uid,domain) # Searching state Value Accordingly
        if branch_ids :
            allow = False
            branch_str = "<BranchList>\n"# Currency List String
            for branch_brw in branch_obj.browse(cr,uid,branch_ids):
                    
                if branch_brw.arabic_name and branch_brw.location_type and branch_brw.email and branch_brw.phone and branch_brw.zip and branch_brw.street and branch_brw.street2 and branch_brw.partner_id and branch_brw.area_id and branch_brw.area_id.crms_id and branch_brw.code:
                    crms_str = False
                    if branch_brw.crms_id:
                        crms_str = "\n<CRMSBranchID>%s</CRMSBranchID>"%(branch_brw.crms_id)
                    allow = True    
                    branch_str += """<Branch>
<ERPBranchID>%s</ERPBranchID>%s
<BranchNameInEng>%s</BranchNameInEng>
<BranchNameInAra>%s</BranchNameInAra>
<BranchCode>%s</BranchCode>
<Location>%s</Location>
<Email>%s</Email>
<Phone>%s</Phone>
<ZipCode>%s</ZipCode>
<AddressLine1>%s</AddressLine1>
<AddressLine2>%s</AddressLine2>
<ContactPerson>%s</ContactPerson>
<ERPAreaID>%s</ERPAreaID>
<CRMSAreaID>%s</CRMSAreaID>
<ERPCityID>%s</ERPCityID>
<CRMSCityID>%s</CRMSCityID>
<ERPRegionID>%s</ERPRegionID>
<CRMSRegionID>%s</CRMSRegionID>
<ERPCountryID>%s</ERPCountryID>
<CRMSCountryID>%s</CRMSCountryID>
</Branch>\n"""%(branch_brw.id, (crms_str or ''), branch_brw.name, branch_brw.arabic_name, branch_brw.code, branch_brw.location_type, branch_brw.email,\
                branch_brw.phone , branch_brw.zip, branch_brw.street, branch_brw.street2, branch_brw.partner_id.name, \
                branch_brw.area_id.id, branch_brw.area_id.crms_id, branch_brw.city_id.id, branch_brw.city_id.crms_id, branch_brw.state_id.id, branch_brw.state_id.crms_id, branch_brw.country_id.id, branch_brw.country_id.crms_id)

            branch_str += "</BranchList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(branch_str, 'BranchCreateRequest', 'BranchResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update sale_shop set crms_id=%s where id=%s",(int(response_dict.get('CRMSBranchID')), response_dict.get('ERPBranchID')))
                if write :
                    self.write(cr, uid, ids, {'last_branch_exported_date':datetime.datetime.today()}) #Updating the Date
            
        return True
    
    #7. Manufacturer CREATE / UPDATE CODE 
    def add_update_manufacturer(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        manufacturer_obj = self.pool.get('fleet.vehicle.model.brand')#instance
        
        domain = []
        if self_brw.last_manufacturer_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_manufacturer_exported_date),('write_date','>=',self_brw.last_manufacturer_exported_date),('crms_id','=',False)] #domain filter
              
        manufacturer_ids = manufacturer_obj.search(cr,uid,domain) # Searching state Value Accordingly
        if manufacturer_ids :
            allow = False
            manufacturer_str = "<ManufacturerList>\n"# Currency List String
            for manufacturer_brw in manufacturer_obj.browse(cr,uid,manufacturer_ids):
                      
                if manufacturer_brw.arabic_name and manufacturer_brw.routine_service_mileage:
                    crms_str = False
                    if manufacturer_brw.crms_id:
                        crms_str = "\n<CRMSManufacturerID>%s</CRMSManufacturerID>"%(manufacturer_brw.crms_id)
                      
                    allow = True    
                    manufacturer_str += """<Manufacturer>
<ERPManufacturerID>%s</ERPManufacturerID>%s
<ManufacturerNameInEng>%s</ManufacturerNameInEng>
<ManufacturerNameInAra>%s</ManufacturerNameInAra>
<RoutineServiceMileage>%s</RoutineServiceMileage>
</Manufacturer>\n"""%(manufacturer_brw.id, (crms_str or ''), manufacturer_brw.name, manufacturer_brw.arabic_name, manufacturer_brw.routine_service_mileage)
  
            manufacturer_str += "</ManufacturerList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(manufacturer_str, 'ManufacturerCreateRequest', 'ManufacturerResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update fleet_vehicle_model_brand set crms_id=%s where id=%s",(int(response_dict.get('CRMSManufacturerID')), response_dict.get('ERPManufacturerID')))
                if write :
                    self.write(cr, uid, ids, {'last_manufacturer_exported_date':datetime.datetime.today()}) #Updating the Date
            
        #Extra Code for Fetching Data from CRMS and writing values in ERP.
#         response_array = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request('', 'ManufacturerListRequest', 'ManufacturerList', 'Manufacturer')
#         context = context or {}
#         context.update({'crms_create':True})          
#         for response_dict in response_array:
#             manu_id = manufacturer_obj.search(cr, uid, [('name','ilike',response_dict.get('ManufacturerNameInEng'))])
#             if manu_id :
#                 manufacturer_obj.write(cr, uid, manu_id[0], {
#                                                           'crms_id':response_dict.get('CRMSManufacturerID'),
#                                                           'arabic_name':response_dict.get('ManufacturerNameInAra'),
#                                                           'routine_service_mileage':response_dict.get('RoutineServiceMileage'),
#                                                           },context)
#             else:
#                 manufacturer_obj.create(cr, uid, {
#                                                    'crms_id':response_dict.get('CRMSManufacturerID'),
#                                                    'arabic_name':response_dict.get('ManufacturerNameInAra'),
#                                                    'routine_service_mileage':response_dict.get('RoutineServiceMileage'),
#                                                    'name':response_dict.get('ManufacturerNameInEng'),
#                                                    },context)
            
        return True
    
    #8. CarType CREATE / UPDATE CODE 
    def add_update_cartype(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        cartype_obj = self.pool.get('fleet.type')#instance
        
        domain = []
        if self_brw.last_cartype_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_cartype_exported_date),('write_date','>=',self_brw.last_cartype_exported_date),('crms_id','=',False)] #domain filter
            
        cartype_ids = cartype_obj.search(cr,uid,domain) # Searching state Value Accordingly
        if cartype_ids :
            allow = False
            cartype_str = "<CarTypeList>\n"# List String
            for cartype_brw in cartype_obj.browse(cr,uid,cartype_ids):
                    
                if cartype_brw.name and cartype_brw.arabic_name:
                    crms_str = False
                    if cartype_brw.crms_id:
                        crms_str = "\n<CRMSCarTypeID>%s</CRMSCarTypeID>"%(cartype_brw.crms_id)
                    
                    allow = True    
                    cartype_str += """<CarType>
<ERPCarTypeID>%s</ERPCarTypeID>%s
<CarTypeNameInEng>%s</CarTypeNameInEng>
<CarTypeNameInAra>%s</CarTypeNameInAra>
</CarType>\n"""%(cartype_brw.id,(crms_str or ''), cartype_brw.name, cartype_brw.arabic_name)

            cartype_str += "</CarTypeList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(cartype_str, 'CarTypeCreateRequest', 'CarTypeResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update fleet_type set crms_id=%s where id=%s",(int(response_dict.get('CRMSCarTypeID')), response_dict.get('ERPCarTypeID')))
                if write :
                    self.write(cr, uid, ids, {'last_cartype_exported_date':datetime.datetime.today()}) #Updating the Date
                    
        #Extra Code for Fetching Data from CRMS and writing values in ERP.
#         response_array = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request('', 'CarTypeListRequest', 'CarTypeList', 'CarType')
#         context = context or {}
#         context.update({'crms_create':True})           
#         for response_dict in response_array:
#             type_id = cartype_obj.search(cr, uid, [('name','ilike',response_dict.get('ManufacturerNameInEng'))])
#             if type_id :
#                 cartype_obj.write(cr, uid, type_id[0], {
#                                                           'crms_id':response_dict.get('CRMSCarTypeID'),
#                                                           'name':response_dict.get('CarTypeNameInEng'),
#                                                           'arabic_name':response_dict.get('CarTypeNameInAra'),
#                                                           },context)
#             else:
#                 cartype_obj.create(cr, uid, {
#                                               'crms_id':response_dict.get('CRMSCarTypeID'),
#                                               'name':response_dict.get('CarTypeNameInEng'),
#                                               'arabic_name':response_dict.get('CarTypeNameInAra'),
#                                               },context)
            
        return True
    
    #9. Model CREATE / UPDATE CODE 
    def add_update_model(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        model_obj = self.pool.get('fleet.vehicle.model')#instance
        
        domain = []
        if self_brw.last_model_exported_date :
            domain = ['|','|',('create_date','>=',self_brw.last_model_exported_date),('write_date','>=',self_brw.last_model_exported_date),('crms_id','=',False)] #domain filter
             
        model_ids = model_obj.search(cr,uid,domain) # Searching state Value Accordingly
        if model_ids :
            allow = False
            model_str = "<ModelList>\n"# List String
            for model_brw in model_obj.browse(cr,uid,model_ids):
                     
                if model_brw.modelname and model_brw.arabic_name and model_brw.variant and model_brw.engine_capacity and model_brw.transmission and model_brw.no_of_seats and model_brw.no_of_luggages and model_brw.no_of_doors and model_brw.fuel and model_brw.fleet_type_id and model_brw.fleet_type_id.crms_id and model_brw.brand_id and model_brw.brand_id.crms_id :
                    crms_str = False
                    if model_brw.crms_id:
                        crms_str = "\n<CRMSModelID>%s</CRMSModelID>"%(model_brw.crms_id)
                     
                    allow = True    
                    model_str += """<Model>
<ERPModelID>%s</ERPModelID>%s
<ModelNameInEng>%s</ModelNameInEng>
<ModelNameInAra>%s</ModelNameInAra>
<Variant>%s</Variant>
<EngineCapacity>%s</EngineCapacity>
<Transmission>%s</Transmission>
<NumberOfPassengers>%s</NumberOfPassengers>
<NumberOfLuggages>%s</NumberOfLuggages>
<NumberOfDoors>%s</NumberOfDoors>
<Fuel>%s</Fuel>
<ERPCarTypeID>%s</ERPCarTypeID>
<CRMSCarTypeID>%s</CRMSCarTypeID>
<ERPManufacturerID>%s</ERPManufacturerID>
<CRMSManufacturerID>%s</CRMSManufacturerID>
</Model>\n""" % (model_brw.id, (crms_str or ''), model_brw.modelname, model_brw.arabic_name, model_brw.variant, model_brw.engine_capacity, model_brw.transmission,\
               model_brw.no_of_seats, model_brw.no_of_luggages, model_brw.no_of_doors, model_brw.fuel,\
               model_brw.fleet_type_id.id, model_brw.fleet_type_id.crms_id, model_brw.brand_id.id,model_brw.brand_id.crms_id)
 
            model_str += "</ModelList>"
            if allow :
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(model_str, 'ModelCreateRequest', 'ModelResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        write = True
                        cr.execute("update fleet_vehicle_model set crms_id=%s where id=%s",(int(response_dict.get('CRMSModelID')), response_dict.get('ERPModelID')))
                if write:
                    self.write(cr, uid, ids, {'last_model_exported_date':datetime.datetime.today()}) #Updating the Date
            
                    
        #Extra Code for importing Model from CRMS
#         response_array = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request('', 'ModelListRequest', 'ModelList', 'Model')
#         cartype_obj = self.pool.get('fleet.type')
#         manufacturer_obj = self.pool.get('fleet.vehicle.model.brand')
#         context = context or {}
#         context.update({'crms_create':True})
#         for response_dict in response_array:
#             manu_id = manufacturer_obj.search(cr, uid, [('crms_id','=',response_dict.get('CRMSManufacturerID'))])
#             type_id = cartype_obj.search(cr, uid, [('crms_id','=',response_dict.get('CRMSCarTypeID'))])
#             model_id = model_obj.search(cr, uid, [('crms_id','=',response_dict.get('CRMSModelID'))])
#             if manu_id and type_id:
#                 vals = {
#                   'crms_id': response_dict.get('CRMSModelID'),
#                   'modelname': response_dict.get('ModelNameInEng'),
#                   'arabic_name': response_dict.get('ModelNameInAra'),
#                   'fleet_type_id': type_id[0],
#                   'brand_id': manu_id[0],
#                   'engine_capacity': response_dict.get('EngineCapacity','Not-defined'),
#                   'no_of_seats': response_dict.get('NumberOfPassengers',4),
#                   'no_of_luggages': response_dict.get('NumberOfLuggages',4),
#                   'no_of_doors': response_dict.get('NumberOfDoors',5),
#                   'variant': response_dict.get('Variant','no-variant'),
#                   'transmission': response_dict.get('Transmission','Not-Defined'),
#                   'fuel': response_dict.get('Fuel','Petrol'),
#                   }
#             
#                 if not model_id:
#                     model_obj.create(cr, uid, vals, context)
#                 else:
#                     model_obj.write(cr, uid, model_id[0], vals, context)
            
        return True
    
    #10. Car CREATE / UPDATE CODE 
    def add_update_car(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        car_obj = self.pool.get('fleet.vehicle')#instance
        
        # Create Car in CRMS
        car_ids = car_obj.search(cr,uid,['|',('crms_id','=',False),('crms_id','<=',0),('company_id','=',1)]) # Searching Value Accordingly
        if car_ids :
            car_str = "<CarList>\n"# List String
            allow = False
            for vehicle_brw in car_obj.browse(cr,uid,car_ids):
                branch_id = False
                date_today = datetime.date.today()
                        
                if vehicle_brw.assigned_for and vehicle_brw.license_plate and vehicle_brw.license_plate_arabic and vehicle_brw.vin_sn and vehicle_brw.color and vehicle_brw.color_arabic and vehicle_brw.company_id and vehicle_brw.model_year and vehicle_brw.model_id and vehicle_brw.model_id.crms_id and vehicle_brw.current_branch_id and vehicle_brw.current_branch_id.crms_id:
                    allow = True
                    extra_str = ''
                    if vehicle_brw.acquisition_date:
                        extra_str += "\n<AcquisitionDate>%s</AcquisitionDate>"%(vehicle_brw.acquisition_date)
                    if  vehicle_brw.engine_number:
                        extra_str += "\n<EngineNumber>%s</EngineNumber>"%(vehicle_brw.engine_number)
                    if vehicle_brw.car_value:
                        extra_str += "\n<CarValue>%s</CarValue>"%(vehicle_brw.car_value)
                    if vehicle_brw.barcode:
                        extra_str += "\n<Barcode>%s</Barcode>"%(vehicle_brw.barcode)
                    if vehicle_brw.mvpi_expiry_date:
                        extra_str += "\n<MVPIExpiryDate>%s</MVPIExpiryDate>"%(vehicle_brw.mvpi_expiry_date)    
                    car_str += """<Car>
<ERPCarID>%s</ERPCarID>
<AssignedFor>%s</AssignedFor>
<LicenseInEng>%s</LicenseInEng>
<LicenseInAra>%s</LicenseInAra>
<VIN>%s</VIN>%s
<ColorInEng>%s</ColorInEng>
<ColorInAra>%s</ColorInAra>
<Odometer>%s</Odometer>
<CarOwner>%s</CarOwner>
<ModelYear>%s</ModelYear>
<ERPModelID>%s</ERPModelID>
<CRMSModelID>%s</CRMSModelID>
<ERPBranchID>%s</ERPBranchID>
<CRMSBranchID>%s</CRMSBranchID>
</Car>\n
"""%(vehicle_brw.id, vehicle_brw.assigned_for, vehicle_brw.license_plate, vehicle_brw.license_plate_arabic, vehicle_brw.vin_sn, extra_str, \
     vehicle_brw.color, vehicle_brw.color_arabic, int(vehicle_brw.odometer), vehicle_brw.company_id.name, vehicle_brw.model_year, vehicle_brw.model_id.id, vehicle_brw.model_id.crms_id, vehicle_brw.current_branch_id.id, vehicle_brw.current_branch_id.crms_id)
            
            car_str +="</CarList>"
              
            if allow : 
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(car_str, 'CarCreateRequest', 'CarResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update fleet_vehicle set crms_id=%s where id=%s",(int(response_dict.get('CRMSCarID')), response_dict.get('ERPCarID')))
        
        #Updating Car in OpenERP
        date_from = False
        date_to = False
        if self_brw.last_car_exported_date :
            date_to = "ToDate='%s'"%(str(datetime.datetime.today().replace(microsecond=0)))
            date_from = "FromDate='%s'"%(self_brw.last_car_exported_date)
              
        response_array = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request('', 'CarListRequest', 'CarList', 'Car', date_from, date_to)
         
        model_obj = self.pool.get('fleet.vehicle.model')
        shop_obj = self.pool.get('sale.shop')
        #fleet_analytic_obj = self.pool.get('fleet.analytic.account')
        
        context.update({'crms_create':True})
        
        for response_dict in response_array:
            vehicle_id = car_obj.search(cr, uid, [('vin_sn','=',response_dict.get('VIN'))])
            model_id = model_obj.search(cr,uid,[('crms_id','=',response_dict.get('CRMSModelID'))])
            branch_id = shop_obj.search(cr,uid,[('crms_id','=',response_dict.get('CRMSBranchID'))])
            
#             if not branch_id:# TODO: Need to put more logic for Corporate Segment.
#                 segment = 'corporate'
#                 field_name = 'client_id'
#                 value = 141 # hardcoded res.partner(Client) ID.
#             else:
#                 segment = 'retail'
#                 field_name = 'branch_id'
#                 value = branch_id[0]

            if model_id and branch_id:
                vals = {
                 'acquisition_date':response_dict.get('AcquisitionDate'),
                 'engine_number':response_dict.get('EngineNumber',False),
                 'vin_sn':response_dict.get('VIN'),
                 'license_plate':response_dict.get('LicenseInEng'),
                 'license_plate_arabic':response_dict.get('LicenseInAra'),
                 'odometer':response_dict.get('Odometer') if response_dict.get('Odometer',0) > 0 else False,
                 'color':response_dict.get('ColorInEng'),
                 'color_arabic':response_dict.get('ColorInAra') or response_dict.get('ColorInEng'),
                 'assigned_for':response_dict.get('AssignedFor'),
                 'barcode':response_dict.get('Barcode'),
                 'model_id':model_id[0],
                 'crms_id':response_dict.get('CRMSCarID'),
                 'model_year':response_dict.get('ModelYear'),
                 'company_id':1,
                 }
                
                if not vehicle_id :
                    vals['analytic_account_ids'] =[(0,0,{'branch_id':branch_id[0],'date_from':datetime.date.today(),'segment':'retail'})] if branch_id else False
                    car_obj.create(cr, uid, vals, context)
                else:
                    crms_osv.search_branch(self, cr, uid, vehicle_id[0], branch_id[0])                
                    car_obj.write(cr,uid, [vehicle_id[0]],vals)
                                
#                 if segment=='retail':
#                     crms_osv.search_branch(cr, uid, vehicle_id[0], branch_id)
#                 else:# TODO: Need to put more logic for corporate. This code is shit.
#                     fleet_ana_id = fleet_analytic_obj.search(cr,uid, [('vehicle_id','=',vehicle_id[0])])
#                     current_branch_id = car_obj.read(cr,uid,vehicle_id[0],['current_branch_id'])['current_branch_id']
#                     if not fleet_ana_id:
#                         fleet_analytic_obj.create(cr,uid,{field_name :value,'date_from':datetime.date.today(),'segment':segment,'vehicle_id':vehicle_id[0]})
#                         vals['analytic_account_ids'] =[(0,0,{field_name :value,'date_from':datetime.date.today(),'segment':segment})]
#                                         
#                 car_obj.write(cr,uid, vehicle_id[0],vals)
        
        self.write(cr, uid, ids, {'last_car_exported_date':datetime.datetime.today()})
                                
        return True
    
    #11. Customer CREATE / UPDATE CODE 
    def add_update_customer(self, cr, uid, ids, context=None):
        context = context or {}
        self_brw = self.browse(cr, uid, ids[0])        
        partner_obj = self.pool.get('res.partner')#instance
        
        date_from = False
        date_to = False
        if self_brw.last_customer_exported_date :
            date_to = "ToDate='%s'"%(str(datetime.datetime.today().replace(microsecond=0)))
            date_from = "FromDate='%s'"%(self_brw.last_customer_exported_date)
            
        response_array = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request('', 'CustomerListRequest', 'CustomerList', 'Customer', date_from, date_to)
        for response_dict in response_array:                
            country_id = self.pool.get('res.country').search(cr,uid,[('crms_id','=',response_dict.get('CRMSCountryID'))])
            vals = {
                 'crms_id':response_dict.get('CRMSCustomerID'),
                 'customer_type':response_dict.get('BusinessType'),
                 'retail_type':response_dict.get('RetailType'),
                 'id_number':response_dict.get('IDNumber'),
                 'employment_type':response_dict.get('EmploymentType'),
                 'company_id':1,
                 'function':response_dict.get('Designation'),
                 'employee_code':response_dict.get('EmpCode'),
                 'preferred_lang':response_dict.get('PreferredLanguage'),
                 'customer_title':response_dict.get('CustomerTitle'),
                 'name':response_dict.get('NameInEng'),
                 'arabic_name':response_dict.get('NameInAra'),
                 'dob':response_dict.get('DOB'),
                 'street':response_dict.get('Address1'),
                 'street1':response_dict.get('Address2'),
                 'city':response_dict.get('Address2'),
                 'zip':response_dict.get('Zip'),
                 'country_id':country_id and country_id[0] or False,
                 'mobile':response_dict.get('Mobile'),
                 'phone':response_dict.get('AltPhone'),
                 'working_number':response_dict.get('WorkNumber'),
                 'loyaltycard_id':response_dict.get('LoyaltyCardID'),
                 'fax':response_dict.get('Fax'),
                 'cardexpiry_date':response_dict.get('CardExpiryDate'),
                 'email':response_dict.get('Email'),
                 'spouser_name':response_dict.get('SponsorName'),
                 'spouser_id':response_dict.get('SponsorID'),
                 'nationality':response_dict.get('Nationality'), 
            }
            
            partner_id = partner_obj.search(cr, uid, [('crms_id','=',response_dict('CRMSCustomerID'))])
            if partner_id:
                partner_obj.write(cr,uid,partner_id[0],vals)
            else:
                partner_obj.create(cr,uid,vals)
               
        
        self.write(cr, uid, ids, {'last_customer_exported_date':datetime.datetime.today()}) #Updating the Date

        return True
    
crms_instance()