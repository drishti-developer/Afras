from openerp.osv import fields, osv, orm
import datetime
from openerp.tools.translate import _
from crms_osv import Call

class res_currency(osv.osv):
    _inherit = "res.currency"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'currency_name':fields.char(string="Currency Name")
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            currency_brw = self.browse(cr, uid, record_id)
            crms_str = False
            if currency_brw.crms_id and currency_brw.crms_id > 0:
                crms_str = "\n<CRMSCurrencyID>%s</CRMSCurrencyID>"%(currency_brw.crms_id)            
            currency_str = """<CurrencyList>\n"# Currency List String         
<Currency>
<ERPCurrencyID>%s</ERPCurrencyID>%s
<CurrencyName>%s</CurrencyName>
<CurrencyCode>%s</CurrencyCode>
</Currency>
</CurrencyList>"""%(currency_brw.id,  (crms_str or ''), currency_brw.currency_name, currency_brw.name)
            
            responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(currency_str, 'CurrencyCreateRequest', 'CurrencyResponse')
            for response_dict in responsearray:
                if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS': 
                    cr.execute("update res_currency set crms_id=%s where id=%s",(int(response_dict.get('CRMSCurrencyID')), response_dict.get('ERPCurrencyID')))
            
        return True
    
    def create(self, cr, uid, data, context=None):
        currency_id = super(res_currency, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, ids)
        return currency_id
    
    def write(self, cr, uid, ids, data, context=None):
        res = super(res_currency, self).create(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res
            
res_currency()

class Country(osv.osv):
    _inherit = "res.country"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",size=256)
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            country_brw = self.browse(cr, uid, record_id)
            if country_brw.id and country_brw.name and country_brw.arabic_name and country_brw.code and country_brw.calling_code and country_brw.currency_id and country_brw.currency_id.crms_id:
                crms_str = False
                if country_brw.crms_id and country_brw.crms_id > 0:
                    crms_str = "\n<CRMSCountryID>%s</CRMSCountryID>"%(country_brw.crms_id)
                    
                country_str = "<CountryList>\n"
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
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(country_str, 'CountryCreateRequest', 'CountryResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update res_country set crms_id=%s where id=%s",(int(response_dict.get('CRMSCountryID')), response_dict.get('ERPCountryID')))

        return True
    
    def create(self, cr, uid, data, context=None):
        country_id = super(Country, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, country_id)
        return country_id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(Country, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res         
        
Country()

class res_country_state(osv.osv):
    _inherit = "res.country.state"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            region_brw = self.browse(cr, uid, record_id)
            if region_brw.name and region_brw.code and region_brw.country_id and region_brw.country_id.crms_id:
                crms_str = False
                if region_brw.crms_id and region_brw.crms_id > 0:
                    crms_str = "\n<CRMSRegionID>%s</CRMSRegionID>"%(region_brw.crms_id)
                    
                region_str = "<RegionList>\n"
                region_str += """<Region>
<ERPRegionID>%s</ERPRegionID>%s
<RegionName>%s</RegionName>
<RegionCode>%s</RegionCode>
<ERPCountryID>%s</ERPCountryID>
<CRMSCountryID>%s</CRMSCountryID>
</Region>\n"""%(region_brw.id, (crms_str or ''), region_brw.name, region_brw.code, region_brw.country_id.id, region_brw.country_id.crms_id)
                region_str += "</RegionList>"
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(region_str, 'RegionCreateRequest', 'RegionResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update res_country_state set crms_id=%s where id=%s",(int(response_dict.get('CRMSRegionID')), response_dict.get('ERPRegionID')))

        return True
        
    def create(self, cr, uid, data, context=None):
        id = super(res_country_state, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(res_country_state, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res    
            
res_country_state()

class res_state_city(osv.osv):
    _inherit = "res.state.city"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",size=256)
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            city_brw = self.browse(cr, uid, record_id)
            if city_brw.arabic_name and city_brw.state_id and city_brw.state_id.crms_id :
                crms_str = False
                if city_brw.crms_id and city_brw.crms_id > 0:
                    crms_str = "\n<CRMSCityID>%s</CRMSCityID>"%(city_brw.crms_id)
                    
                city_str = "<CityList>\n"            
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
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(city_str, 'CityCreateRequest', 'CityResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update res_state_city set crms_id=%s where id=%s",(int(response_dict.get('CRMSCityID')), response_dict.get('ERPCityID')))
        
        return True
    
    def create(self, cr, uid, data, context=None):
        id = super(res_state_city, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(res_state_city, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res 
    
res_state_city()

class res_city_area(osv.osv):
    _inherit = "res.city.area"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",size=256)
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            area_brw = self.browse(cr, uid, record_id)
            if area_brw.name and area_brw.arabic_name and area_brw.city_id and area_brw.city_id.crms_id :
                crms_str = False
                if area_brw.crms_id and area_brw.crms_id > 0:
                    crms_str = "\n<CRMSAreaID>%s</CRMSAreaID>"%(area_brw.crms_id)
                    
                area_str = "<AreaList>\n"    
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
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(area_str, 'AreaCreateRequest', 'AreaResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update res_city_area set crms_id=%s where id=%s",(int(response_dict.get('CRMSAreaID')), response_dict.get('ERPAreaID')))
            
    def create(self, cr, uid, data, context=None):
        id = super(res_city_area, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(res_city_area, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res 
    
res_city_area()

class sale_shop(osv.osv):
    _inherit = "sale.shop"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",size=256),
        'location_type': fields.selection([('Branch', 'Branch'), ('Workshop', 'Workshop'),('Agency', 'Agency')], 'Location Type',),
        'project_id': fields.many2one('account.analytic.account', 'Analytic Account',),
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            branch_brw = self.browse(cr, uid, record_id)
            if branch_brw.arabic_name and branch_brw.location_type and branch_brw.email and branch_brw.phone and branch_brw.zip and branch_brw.street and branch_brw.street2 and branch_brw.partner_id and branch_brw.area_id and branch_brw.area_id.crms_id :
                crms_str = False
                if branch_brw.crms_id and branch_brw.crms_id > 0:
                    crms_str = "\n<CRMSBranchID>%s</CRMSBranchID>"%(branch_brw.crms_id)
                    
                branch_str = "<BranchList>\n"
                branch_str += """<Branch>
<ERPBranchID>%s</ERPBranchID>%s
<BranchNameInEng>%s</BranchNameInEng>
<BranchNameInAra>%s</BranchNameInAra>
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
</Branch>\n"""%(branch_brw.id, (crms_str or ''), branch_brw.name, branch_brw.arabic_name, branch_brw.location_type, branch_brw.email,\
            branch_brw.phone , branch_brw.zip, branch_brw.street, branch_brw.street2, branch_brw.partner_id.name, \
            branch_brw.area_id.id, branch_brw.area_id.crms_id, branch_brw.city_id.id, branch_brw.city_id.crms_id, branch_brw.state_id.id, branch_brw.state_id.crms_id, branch_brw.country_id.id, branch_brw.country_id.crms_id)

            branch_str += "</BranchList>"
            responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(branch_str, 'BranchCreateRequest', 'BranchResponse')
            for response_dict in responsearray:
                if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                    cr.execute("update sale_shop set crms_id=%s where id=%s",(int(response_dict.get('CRMSBranchID')), response_dict.get('ERPBranchID')))
            
    def create(self, cr, uid, data, context=None):
        id = super(sale_shop, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(sale_shop, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res
    
sale_shop()

class fleet_vehicle_model_brand(osv.osv):
    _inherit = "fleet.vehicle.model.brand"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",size=256),
        'routine_service_mileage':fields.char(string="Routine Service Mileage",size=256)
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            manufacturer_brw = self.browse(cr, uid, record_id)            
            if manufacturer_brw.arabic_name and manufacturer_brw.routine_service_mileage:
                crms_str = False
                if manufacturer_brw.crms_id and manufacturer_brw.crms_id > 0:
                    crms_str = "\n<CRMSManufacturerID>%s</CRMSManufacturerID>"%(manufacturer_brw.crms_id)
                    
                manufacturer_str = "<ManufacturerList>\n"
                manufacturer_str += """<Manufacturer>
<ERPManufacturerID>%s</ERPManufacturerID>%s
<ManufacturerNameInEng>%s</ManufacturerNameInEng>
<ManufacturerNameInAra>%s</ManufacturerNameInAra>
<RoutineServiceMileage>%s</RoutineServiceMileage>
</Manufacturer>\n"""%(manufacturer_brw.id, (crms_str or ''), manufacturer_brw.name, manufacturer_brw.arabic_name, manufacturer_brw.routine_service_mileage)
  
                manufacturer_str += "</ManufacturerList>"
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(manufacturer_str, 'ManufacturerCreateRequest', 'ManufacturerResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update fleet_vehicle_model_brand set crms_id=%s where id=%s",(int(response_dict.get('CRMSManufacturerID')), response_dict.get('ERPManufacturerID')))
    
        return True
    
    def create(self, cr, uid, data, context=None):
        id = super(fleet_vehicle_model_brand, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(fleet_vehicle_model_brand, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res
    
fleet_vehicle_model_brand()

class fleet_type(osv.osv):
    _inherit = "fleet.type"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",size=256),
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            cartype_brw = self.browse(cr, uid, record_id)
            if cartype_brw.name and cartype_brw.arabic_name:
                cartype_str = "<CarTypeList>\n"
                crms_str = False
                if cartype_brw.crms_id and cartype_brw.crms_id >0:
                    crms_str = "\n<CRMSCarTypeID>%s</CRMSCarTypeID>"%(cartype_brw.crms_id)
                
                cartype_str += """<CarType>
<ERPCarTypeID>%s</ERPCarTypeID>%s
<CarTypeNameInEng>%s</CarTypeNameInEng>
<CarTypeNameInAra>%s</CarTypeNameInAra>
</CarType>\n"""%(cartype_brw.id,(crms_str or ''), cartype_brw.name, cartype_brw.arabic_name)

                cartype_str += "</CarTypeList>"
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(cartype_str, 'CarTypeCreateRequest', 'CarTypeResponse')
                write = False
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update fleet_type set crms_id=%s where id=%s",(int(response_dict.get('CRMSCarTypeID')), response_dict.get('ERPCarTypeID')))
        
        return True
    
    def create(self, cr, uid, data, context=None):
        id = super(fleet_type, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(fleet_type, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res
    
fleet_type()

class fleet_vehicle_model(osv.osv):
    _inherit = "fleet.vehicle.model"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'arabic_name':fields.char(string="Arabic Name",required=True,size=256),
    }
    
    def update_crms(self,cr,uid,record_id):
        crms_obj = self.pool.get('crms.instance')
        crms_instance_id = crms_obj.search(cr,uid,[('active','=',True)])
        if crms_instance_id:
            self_brw = crms_obj.browse(cr,uid,crms_instance_id[0])
            model_brw = self.browse(cr, uid, record_id)
            if model_brw.modelname and model_brw.arabic_name and model_brw.variant and model_brw.engine_capacity and model_brw.transmission and model_brw.no_of_seats and model_brw.no_of_luggages and model_brw.no_of_doors and model_brw.fuel and model_brw.fleet_type_id and model_brw.fleet_type_id.crms_id and model_brw.brand_id and model_brw.brand_id.crms_id :
                crms_str = False
                if model_brw.crms_id and model_brw.crms_id >0:
                    crms_str = "\n<CRMSModelID>%s</CRMSModelID>"%(model_brw.crms_id)
                
                model_str = "<ModelList>\n"     
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
                responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(model_str, 'ModelCreateRequest', 'ModelResponse')
                for response_dict in responsearray:
                    if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                        cr.execute("update fleet_vehicle_model set crms_id=%s where id=%s",(int(response_dict.get('CRMSModelID')), response_dict.get('ERPModelID')))
        
        return True
    
    def create(self, cr, uid, data, context=None):
        id = super(fleet_vehicle_model, self).create(cr, uid, data, context=context)
        self.update_crms(cr, uid, id)
        return id
   
    def write(self, cr, uid, ids, data, context=None):
        res = super(fleet_vehicle_model, self).write(cr, uid, ids, data, context=context)
        self.update_crms(cr, uid, ids[0])
        return res
    
fleet_vehicle_model()

class fleet_vehicle(osv.osv):
    _inherit = "fleet.vehicle"
    
    def _vehicle_branch_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        
        for record in self.browse(cr, uid, ids, context=context):
            value_id = False
            date_today = datetime.datetime.today().replace(microsecond=0)
            for ana_acc_id in record.analytic_account_ids:
                from_date = datetime.datetime.strptime(ana_acc_id.date_from,"%Y-%m-%d")
                if date_today >= from_date:
                    if ana_acc_id.segment=='retail':
                        value_id = ana_acc_id.branch_id and ana_acc_id.branch_id.name or False
                    else:
                        value_id = ana_acc_id.client_id and ana_acc_id.client_id.name or False                        
                    if ana_acc_id.date_to:
                        to_date = datetime.datetime.strptime(ana_acc_id.date_to,"%Y-%m-%d")
                        if date_today <= to_date:
                            continue
                        else:
                            value_id = False
                    
            res[record.id] = value_id
        return res
    
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'license_plate_arabic':fields.char(string="License Plate Arabic Name",size=256),
        'color_arabic':fields.char(string="Color Arabic Name",size=256),
        'assigned_for': fields.selection([('Corporate','Corporate'),('Retail','Retail'),('Awaiting for Barcode','Awaiting for Barcode')],string="Assigned For"),
        'licence_plate_arabic':fields.char("Licence Plate Arabic Name",size=256),
        'color_arabic':fields.char(string="Color Arabic Name",size=256),
        'current_branch_id':fields.function(_vehicle_branch_get_fnc, type="char", string='Branch/Client'),
        'mvpi_expiry_date':fields.date(string='MVPIExpiryDate'),
    }
    
    def create(self, cr, uid, data, context=None):
        
        context = context or {} 
        vehicle_id = super(fleet_vehicle, self).create(cr, uid, data, context=context)
        if not context.get('crms_create',False):
            reference_obj = self.pool.get('crms.instance')
            reference_ids = reference_obj.search(cr,uid,[])
            if reference_ids:
                vehicle_brw = self.browse(cr, uid, vehicle_id)
                if len(vehicle_brw.analytic_account_ids) <=0:
                    raise osv.except_osv(_('Error'),_('Please add atleast one Branch'))
                
                self_brw = reference_obj.browse(cr,uid,reference_ids[0])
                branch_id = False
                date_today = datetime.date.today()
                             
                if vehicle_brw.assigned_for and vehicle_brw.license_plate and vehicle_brw.license_plate_arabic and vehicle_brw.vin_sn and vehicle_brw.color and vehicle_brw.color_arabic and vehicle_brw.company_id and vehicle_brw.model_year and vehicle_brw.model_id and vehicle_brw.model_id.crms_id and vehicle_brw.current_branch_id and vehicle_brw.current_branch_id.crms_id:
                    extra_str = ''
                    if vehicle_brw.acquisition_date:
                        extra_str += "\n<AcquisitionDate>%s</ AquisitionDate>"%(vehicle_brw.acquisition_date)
                    if  vehicle_brw.engine_number:
                        extra_str += "\n<EngineNumber>%s</EngineNumber>"%(vehicle_brw.engine_number)
                    if vehicle_brw.car_value:
                        extra_str += "\n<CarValue>%s</CarValue>"%(vehicle_brw.car_value)
                    if vehicle_brw.barcode:
                        extra_str += "\n<Barcode>%s</Barcode>"%(vehicle_brw.barcode)
                    
                    car_str = "<CarList>"        
                    car_str += """<Car>
<ERPCarID>%s</ERPCarID>
<AssignedFor>%s</AssignedFor>
<LicenseInEng>%s</LicenseInEng>
<LicenseInAra>%s</LicenseInAra>
<VIN>%s</VIN>%s
<ColorInEng>%s</ColorInEng>
<ColorInAra>%s</ColorInAra>
<MVPIExpiryDate>%s</MVPIExpiryDate>
<Odometer>%s</Odometer>
<CarOwner>%s</CarOwner>
<ModelYear>%s</ModelYear>
<ERPModelID>%s</ERPModelID>
<CRMSModelID>%s</CRMSModelID>
<ERPBranchID>%s</ERPBranchID>
<CRMSBranchID>%s</CRMSBranchID>
</Car>\n
"""%(vehicle_brw.id, vehicle_brw.assigned_for, vehicle_brw.license_plate, vehicle_brw.license_plate_arabic, vehicle_brw.vin_sn, extra_str, \
     vehicle_brw.color, vehicle_brw.color_arabic, date_today, int(vehicle_brw.odometer), vehicle_brw.company_id.name, vehicle_brw.model_year, vehicle_brw.model_id.id, vehicle_brw.model_id.crms_id, vehicle_brw.current_branch_id.id, vehicle_brw.current_branch_id.crms_id)
         
                    car_str +="</CarList>" 
                    responsearray = Call(self_brw.name, self_brw.erp_ip, self_brw.username, self_brw.password).send_request(car_str, 'CarCreateRequest', 'CarResponse')
                    for response_dict in responsearray:
                        if response_dict.get('RecordStatus',False) and response_dict.get('RecordStatus') == 'SUCCESS':
                            cr.execute("update fleet_vehicle set crms_id=%s where id=%s",(int(response_dict.get('CRMSCarID')), response_dict.get('ERPCarID')))
                 
        return vehicle_id
    
fleet_vehicle()

class fleet_vehicle_odometer(osv.Model):
    _inherit='fleet.vehicle.odometer'
    
    def _vehicle_log_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            name = record.vehicle_id.name
            if record.date and name:
                name = name+ ' / '+ str(record.date)
            res[record.id] = name
        return res
    
    _columns = {
                'name': fields.function(_vehicle_log_name_get_fnc, type="char", string='Name', store=True), 
                }
    
fleet_vehicle_odometer()

class res_partner(osv.osv):
    _inherit = "res.partner"
    _columns = {
        'crms_id':fields.integer(string="CRMS ID"),
        'customer_type': fields.selection([('Retail', 'Retail'), ('Corporate', 'Corporate')], 'Customer Type'),
        'retail_type': fields.selection([('Saudi National', 'Saudi National'), ('Saudi Resident', 'Saudi Resident'),('Visitor','Visitor')], 'Retail Type'),
        'id_number':fields.char(string="ID Number",size=256),
        'employment_type':fields.selection([('Government', 'Government'), ('Company', 'Company')], 'Employment Type'),
        'designation':fields.char(string="Designation",size=256),
        'employee_code':fields.char(string="Employee Code",size=64),
        'customer_title':fields.char(string="Title of the customer",size=124),
        'arabic_name':fields.char(string="Customer Name in Arabic",required=True,size=124),
        'dob':fields.date(string='Date of Birth'),
        'working_number':fields.char(string="Working Number",size=124),
        'loyaltycard_id':fields.integer(string="Loyalty Card Number"),
        'cardexpiry_date':fields.date(string='ID Card Expiry date'),
        'spouser_name':fields.char(string="Sponsor Name of the customer",size=64),
        'spouser_id':fields.integer(string="Sponsor ID of the customer"),
        'nationality': fields.char(string="Nationality",size=64),
        'preferred_lang': fields.char(string="Preferred Language",size=128),
        'company_name': fields.char(string="Company Name",size=128),
        }

res_partner()

class crms_payment(osv.osv):
    _name = 'crms.payment'
    
    _columns = {
       'name':fields.char('Name',size=64),
       'crms_id':fields.integer('Crms Payment Id'),
       'partner_id':fields.many2one('res.partner','Customer Name'),
       'vehicle_id':fields.many2one('fleet.vehicle','Vehicle'),
       'car_type_id':fields.many2one('fleet.type','Car Type'),
       'model_id':fields.many2one('fleet.vehicle.model','Vehicle Model'),
       'crms_booking_id':fields.integer('Crms Booking Id'),
       'rental_from_date':fields.datetime('Rental From Date'),
       'rental_to_date':fields.datetime('Rental To Date'),
       'no_of_days':fields.integer('No Of Days'),
       'pickup_branch_id':fields.many2one('sale.shop','Pickup Branch'),
       'drop_branch_id':fields.many2one('sale.shop','Drop Branch'),
       'booking_branch_id':fields.many2one('sale.shop','Booking Branch'),
       'amount_paid':fields.float('Amount Paid by Customer'),
       'amount_receive_date':fields.datetime('Amount Receive Date'),
       'rental_amount':fields.float('Rental Amount'),
       'holding_amount':fields.float('Holding Amount'),
       'advance_amount':fields.float('Advanced Amount'),
       'balance_due_amount':fields.float('Balance Due Amount'),
       'payment_type':fields.selection([('Cash','Cash'),('Card','Card')],'Payment Type'),
   }
    
crms_payment()
