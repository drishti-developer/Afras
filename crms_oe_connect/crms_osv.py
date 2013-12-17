# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv.orm import Model
from openerp.osv.osv import except_osv
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import datetime
import urllib
from xml.dom.minidom import parse, parseString

STANDARD_LIST_RESPONSE = """<?xml version="1.0" encoding="utf-8"?><ResponseGroup xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><ERPResponse><ResponseData DataCollectionDate="%(collectiondate)s" ResponseService="%(responsename)s"><ResponseCode>1</ResponseCode><ResponseMessage>SUCCESS</ResponseMessage>%(responsedata)s</ResponseData></ERPResponse></ResponseGroup>"""

VIEW_CLASS_LIST = ['res.currency', 'res.country', 'res.country.state', 'res.state.city', 'res.city.area', 'sale.shop', 'fleet.vehicle.model.brand', 'fleet.type', 'fleet.vehicle.model','fleet.vehicle','res.partner','crms.payment']

CREATE_CLASS_LIST = ['res.partner', 'crms.payment', 'fleet.vehicle',]

CURRENCY_LIST = [
			('id','ERPCurrencyID'),
			('crms_id','CRMSCurrencyID'),
			('currency_name','CurrencyName'),
			('name','CurrencyCode')]

COUNTRY_LIST = [
			('id','ERPCountryID'),
			('crms_id','CRMSCountryID'),
			('name','CountryName'),
			('code','CountryCode'),
			('calling_code','CallingCode'),
			('currency_id',('id','ERPCurrencyID')),
			('currency_id',('crms_id','CRMSCurrencyID')),
			]

REGION_LIST = [
			('id','ERPRegionID'),
			('crms_id','CRMSRegionID'),
			('name','RegionName'),
			('code','RegionCode'),
			('country_id',('id','ERPCountryID')),
			('country_id',('crms_id','ERPCountryID')),
			]

CITY_LIST = [
			('id','ERPCityID'),
			('crms_id','CRMSCityID'),
			('name','CityNameInEng'),
			('arabic_name','CityNameInAra'),
			('state_id',('id','ERPRegionID')),
			('state_id',('crms_id','CRMSRegionID')),
			('country_id',('id','ERPCountryID')),
			('country_id',('crms_id','ERPCountryID')),
			]

AREA_LIST = [
			('id','ERPAreaID'),
			('crms_id','CRMSAreaID'),
			('name','AreaNameInEng'),
			('arabic_name','AreaNameInAra'),
			('city_id',('id','ERPCityID')),
			('city_id',('crms_id','CRMSCityID')),
			('state_id',('id','ERPRegionID')),
			('state_id',('crms_id','CRMSRegionID')),
			('country_id',('id','ERPCountryID')),
			('country_id',('crms_id','ERPCountryID')),
			]

BRANCH_LIST = [
			('id','ERPBranchID'),
			('crms_id','CRMSBranchID'),
			('name','BranchNameInEng'),
			('arabic_name','BranchNameInAra'),
			('location_type','Location'),
			('email','Email'),
			('phone','PhoneNumber'),
			('zip','ZipCode'),
			('street','AddressLine1'),
			('street2','AddressLine2'),
			('partner_id',('name','ContactPerson')),
			('area_id',('id','ERPAreaID')),
			('area_id',('crms_id','CRMSAreaID')),
			('city_id',('id','ERPCityID')),
			('city_id',('crms_id','CRMSCityID')),
			('state_id',('id','ERPRegionID')),
			('state_id',('crms_id','CRMSRegionID')),
			('country_id',('id','ERPCountryID')),
			('country_id',('crms_id','ERPCountryID')),
			]

MANUFACTURER_LIST = [
			('id','ERPManufacturerID'),
			('crms_id','CRMSManufacturerID'),
			('name','ManufacturerNameInEng'),
			('arabic_name','ManufacturerNameInAra'),
			('routine_service_mileage','RoutineServiceMileage'),
			]

CARTYPE_LIST = [
			('id','ERPCarTypeID'),
			('crms_id','CRMSCarTypeID'),
			('name','CarTypeNameInEng'),
			('arabic_name','CarTypeNameInAra'),
			]

MODEL_LIST = [
			('id','ERPModelID'),
			('crms_id','CRMSModelID'),
			('name','ModelNameInEng'),
			('arabic_name','ModelNameInAra'),
			('variant','Variant'),
			('engine_capacity','EngineCapacity'),
			('transmission','Transmission'),
			('no_of_seats','NumberOfPassengers'),
			('no_of_luggages','NumberOfLuggages'),
			('no_of_doors','NumberOfDoors'),
			('fuel','Fuel'),
			('fleet_type_id',('id','ERPCarTypeID')),
			('fleet_type_id',('crms_id','CRMSCarTypeID')),
			('brand_id',('id','ERPManufacturerID')),
			('brand_id',('crms_id','CRMSManufacturerID')),
			]

CAR_LIST = [
			('id','ERPCarID'),
			('crms_id','CRMSCarID'),
			('model_id',('id','ERPModelID',1,'fleet.vehicle.model')),
			('model_id',('crms_id','CRMSModelID',1,'fleet.vehicle.model')),
			('license_plate','LicenseInEng'),
			('license_plate_arabic','LicenseInAra'),
			('assigned_for','AssignedFor'),
			('vin_sn','VIN'),
			('engine_number','EngineNumber'),
			('car_value','CarValue'),
			('color','ColorInEng'),
			('color_arabic','ColorInAra'),
			('acquisition_date','AcquisitionDate'),
			('mvpi_expiry_date','MVPIExpiryDate'),
			('odometer','Odometer'),
			('barcode','Barcode'),
			('model_year','ModelYear'),
			('company_id',('name','CarOwner',1,'res.company')),
			('current_branch_id',('id','ERPBranchID',1,'sale.shop')),
			('current_branch_id',('crms_id','CRMSBranchID',1,'sale.shop')),
			('analytic_account_ids','ERPBranchID'),
			]

CUSTOMER_LIST  = [
			('id','ERPCustomerID'),
            ('crms_id','CRMSCustomerID'),
            ('customer_type','BusinessType'),
            ('retail_type','RetailType'),
            ('id_number','IDNumber'),
            ('employment_type','EmploymentType'),
            ('company_id',('name','CompanyName',1,'res.company')),
            ('function','Designation'),
            ('employee_code','EmpCode'),
            ('preferred_lang','PreferredLanguage'),
            ('customer_title','CustomerTitle'),
            ('name','NameInEng'),
            ('arabic_name','NameInAra'),
            ('dob','DOB'),
            ('street','Address1'),
            ('street2','Address2'),
            ('city','City'),
            ('zip','Zip'),
            ('country_id',('id','ERPCountryID',194,'res.country')),
            ('mobile','Mobile'),
            ('phone','AltPhone'),
            ('working_number','WorkNumber'),
            ('loyaltycard_id','LoyaltyCardID'),
            ('fax','Fax'),
            ('cardexpiry_date','CardExpiryDate'),
            ('email','Email'),
            ('spouser_name','SponsorName'),
            ('spouser_id','SponsorID'),
            ('nationality','Nationality'),
            ]

RENTAL_PAYMENT_LIST = [
			('id','ERPRentalPaymentID'),
            ('crms_id','CRMSRentalPaymentID'),
            ('partner_id',('id','ERPCustomerID',0,'res.partner')),
            ('vehicle_id',('id','ERPCarID',0,'fleet.vehicle')),
            ('car_type_id',('id','ERPCarTypeID',0,'fleet.type')),
            ('model_id',('id','ERPModelID',0,'fleet.vehicle.model')),
            ('crms_booking_id','CRMSBookingID'),
            ('rental_from_date','RentalFromDate'),
            ('rental_to_date','RentalToDate'),
            ('no_of_days','NoOfDays'),
            ('pickup_branch_id',('id','ERPPickupBranchID',0,'sale.shop')),
            ('drop_branch_id',('id','ERPDropBranchID',0,'sale.shop')),
            ('booking_branch_id',('id','ERPBookingBranchID',0,'sale.shop')),
            ('amount_paid','AmountPaidByCustomer'),
            ('amount_receive_date','AmountReceivedDate'),
            ('rental_amount','RentalAmount'),
            ('holding_amount','HoldingAmount'),
            ('advance_amount','Advance'),
            ('balance_due_amount','BalanceDue'),
            ('payment_type','PaymentMode'),
            ]

def getDataArray(responseDOM, tag, level_1, level_2=False):
    
    responsearray = []
    for node in responseDOM.getElementsByTagName(tag):
        for cNode in node.childNodes:
            if cNode.nodeName == level_1:
                info_1 = {}
                for scNode in cNode.childNodes:
                    if level_2:
                        info_2 = {}
                        for sscNode in scNode.childNodes:
                            if sscNode.childNodes:
                                info_2[sscNode.nodeName] = sscNode.childNodes[0].data
                        if info_2:
                            responsearray.append(info_2)
                    else :
                        info_1[scNode.nodeName] = scNode.childNodes[0].data
                if info_1:
                    responsearray.append(info_1)
                    
    return responsearray

# Send Request from OpenERP --> CRMS System.
class Call:
    
    def __init__(self, URL, IPAddress, Username, Password):
        self.URL = URL
        self.IPAddress = IPAddress
        self.Username = Username
        self.Password = Password
         
    def send_request(self, request_str, request_type, level_1, level_2=False, from_date=False, to_date=False):
        
        responsearray = []
        try : 
            request_data = """<?xml version="1.0" encoding="utf-8"?>
<RequestGroup xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<CRMSRequest>
<RequestData DataCollectionDate='%(collectiondate)s' RequestedService="%(requestname)s" %(fromdate)s %(todate)s>
<IPAddress>%(ipaddress)s</IPAddress>
<UserName>%(username)s</UserName>
<Password>%(password)s</Password>
%(requestdata)s
</RequestData>    
</CRMSRequest>
</RequestGroup>""" % {
                    'ipaddress' : self.IPAddress,
                    'username' : self.Username,
                    'password' : self.Password,
                    'collectiondate' : str(datetime.date.today()),
                    'requestname' : request_type,
                    'fromdate' : from_date or '',
                    'todate' : to_date or '',
                    'requestdata' : request_str,
                    }
    
            #print "XML Requested Data:\n",request_data
            encoded_data = urllib.quote_plus(request_data.encode('utf-8')) # Encoding the XML Request
            encoded_data = "xml="+encoded_data
            #print "Encoded Requested Data:\n",encoded_data
            webf = urllib.urlopen(self.URL, encoded_data) #Sending the URL Request with encoded code using urllib library
            response = webf.read() #Web Response
            #print "Response",response
            webf.close()
            responseDOM = parseString(response) #Parsing the Response
            #print "Response from CRMS:\n",responseDOM.toprettyxml()
            responsearray = getDataArray(responseDOM, 'ResponseData', level_1, level_2)
        
        except Exception,e:
            raise osv.except_osv(_('Error'),_(e))
                    
        return responsearray
    
def generateXML(response_name, browse_record, browse_list):
    
    response_data = "<%s>"%(response_name)
        
    for browse_value in browse_list:
    	if browse_value[0] != 'analytic_account_ids':
	        if isinstance(browse_value[1],tuple):
	        	new_browse_record = getattr(browse_record, browse_value[0])
	        	new_browse_value = browse_value[1]
	        	response_data += "<%s>%s</%s>"%(new_browse_value[1], getattr(new_browse_record, new_browse_value[0]), new_browse_value[1])
	        else:
	            response_data += "<%s>%s</%s>"%(browse_value[1], getattr(browse_record, browse_value[0]), browse_value[1])
    response_data +="</%s>"%(response_name)
    return response_data

def search_branch(self,cr,uid,car_id,branch_id):
	acc_obj = self.pool.get('fleet.analytic.account')
	car_brw = self.pool.get('fleet.vehicle').browse(cr,uid,car_id)
	date_today = datetime.date.today()
	current_branch_date = False
	current_branch_id = False
	fleet_account_id = False
	
	#cr.execute('select id from fleet_analytic_account where date_from = (select max(date_from) from fleet_analytic_account where vehicle_id=%s) and vehicle_id=%s limit 1',(car_id,car_id))
	#branch_id = cr.fetchone()
	for ana_acc_id in car_brw.analytic_account_ids:
		if not current_branch_date:
			current_branch_date = ana_acc_id.date_from
			current_branch_id = ana_acc_id.branch_id.id
			fleet_account_id = ana_acc_id.id
			
		elif current_branch_date < ana_acc_id.date_from:
			current_branch_date = ana_acc_id.date_from
			current_branch_id = ana_acc_id.branch_id.id
			fleet_account_id = ana_acc_id.id
			
	if current_branch_id:# TODO: Need to put more logic on creating/updating a branch.
		if current_branch_id != int(branch_id):
			acc_obj.create(cr,uid,{'vehicle_id':car_id,'branch_id':branch_id,'date_from':date_today,'segment':'retail'})
			acc_obj.write(cr,uid,fleet_account_id,{'date_to':date_today})
		
	else :
		acc_obj.create(cr,uid,{'vehicle_id':car_id,'branch_id':branch_id,'date_from':date_today})
	return True    

def extend(class_to_extend):
    """
    Decorator to use to extend a existing class with a new method
    Example :
    @extend(Model)
    def new_method(self, *args, **kwargs):
        print 'I am in the new_method', self._name
        return True
    Will add the method new_method to the class Model
    """
    def decorator(func):
        if hasattr(class_to_extend, func.func_name):
            raise except_osv(_("Developper Error"),
                _("You can extend the class %s with the method %s.",
                "Indeed this method already exist use the decorator 'replace' instead"))
        setattr(class_to_extend, func.func_name, func)
        return class_to_extend
    return decorator

# Extra ORM Methods
# Send Response to CRMS for its particular Request.    
@extend(Model)
def ListRequest(self, cr, uid, date_from=False, date_to=False):
    
    return_response = "Invalid Request"
    if self._name in VIEW_CLASS_LIST:
    	domain = ['|',('crms_id','!=',False),('crms_id','>',0)]    	
    	browse_list = []
    	response_name = False
    	
    	if self._name == 'res.currency' :
            response_name = "Currency"
            browse_list = CURRENCY_LIST
    	elif self._name == 'res.country' :
            response_name = "Country"
            browse_list = COUNTRY_LIST
    	elif self._name == 'res.country.state' :
            response_name = "Region"
            browse_list = REGION_LIST
    	elif self._name == 'res.state.city' :
            response_name = "City"
            browse_list = CITY_LIST
    	elif self._name == 'res.city.area' :
            response_name = "Area"
            browse_list = AREA_LIST
    	elif self._name == 'sale.shop' :
            response_name = "Branch"
            browse_list = BRANCH_LIST
    	elif self._name == 'fleet.vehicle.model.brand' :
            response_name = "Manufacturer"
            browse_list = MANUFACTURER_LIST
    	elif self._name == 'fleet.type' :
            response_name = "CarType"
            browse_list = CARTYPE_LIST
    	elif self._name == 'fleet.vehicle.model' :
            response_name = "Model"
            browse_list = MODEL_LIST
    	elif self._name == 'fleet.vehicle' :
            browse_list = CAR_LIST
            response_name = "Car"
        elif self._name == 'res.partner' :
            browse_list = CUSTOMER_LIST
            response_name = "Customer"
            domain = ['|',('crms_id','!=',False),('crms_id','>',0),('customer','=',True)]
        elif self._name == 'crms.payment' :
            browse_list = RENTAL_PAYMENT_LIST
            response_name = "RentalPayment"
    	
    	if date_from : domain.append(('write_date','>=',date_from))
    	if date_to : domain.append(('write_date','<=',date_to))
    	
    	search_ids = self.search(cr, uid, domain)
        
        response_service = response_name+"ListResponse"
        response_data = ''
        if search_ids and browse_list:
            response_data += "<RecordCount>%s</RecordCount>"%(len(search_ids))
            response_data += "<%s>"%(response_name+"List")
            for record in self.browse(cr, uid, search_ids):
                response_data += generateXML(response_name, record, browse_list)
            response_data += "</%s>"%(response_name+"List")
#            print response_data
            
        return_response = STANDARD_LIST_RESPONSE % {'collectiondate':str(datetime.date.today()), 'responsename': response_service, 'responsedata':response_data}
#     	responseDOM = parseString(return_response) #Parsing the Response
#         print "Response from CRMS:\n",responseDOM.toprettyxml()
    return return_response

@extend(Model)
def CreateRequest(self, cr, uid, data):
    
    return_response = "Invalid Request"
    if self._name in CREATE_CLASS_LIST:

        if self._name == 'res.partner':#Customer
            response_type = 'Customer'
            field_list = CUSTOMER_LIST
        elif self._name == 'crms.payment':#Rental Payment
            response_type = 'RentalPayment'
            field_list = RENTAL_PAYMENT_LIST
        elif self._name == 'fleet.vehicle':#Car
            response_type = 'Car'
            field_list = CAR_LIST
             
        response_data = ''
        response_name = response_type+"Response"
        response_service = response_type+"CreateResponse"
        
        data = data.strip()
        data = " ".join(data.split())
        data = data.encode('utf-8')
        responseDOM = parseString(data)
        responsearray = getDataArray(responseDOM, 'RequestData', response_type+'List', response_type)       
        for response in responsearray:
            response_data += "<%s>"%(response_name)
            crms_id = response['CRMS'+response_type+'ID']
            response_data += "<%s>%s</%s>"%('CRMS'+response_type+'ID', crms_id, 'CRMS'+response_type+'ID')
            search_id = self.search(cr,uid,[('crms_id','=',crms_id)])
            record_value = {}
            
            for field in field_list:
            	if field[0] not in ['id','current_branch_id']:#skip fields
	            	if field[0] == 'analytic_account_ids' and len(search_id) > 0:
	            		search_branch(self,cr,uid,search_id[0],response.get(field[1]))
	                else :
	                	if isinstance(field[1],tuple):
	                		ext_field = field[1]
	                		if ext_field[0] not in ['crms_id']:#skip fields
		                		search_value_id = self.pool.get(ext_field[3]).search(cr,uid,[(ext_field[0],'=',response.get(ext_field[1]))])
	                			record_value[field[0]] = search_value_id and search_value_id[0] or ext_field[2]
	                	else:
	                		record_value[field[0]] = response.get(field[1],False)
	                	
            try :
            	msg = 'SUCCESS'
            	record_id = 0
                if len(search_id) == 0 and record_value:
                    record_id = self.create(cr,uid,record_value,{'mail_create_nosubscribe':True,'crms_create':True})
                elif len(search_id) > 0 and record_value:
                    self.write(cr,uid,search_id,record_value)
                    record_id = search_id[0]
                else:
                	msg = 'FAILURE - CRMSID NOT FOUND'
                    
                response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', record_id, 'ERP'+response_type+'ID')
                response_data += "<RecordStatus>%s</RecordStatus>"%(msg)
            except Exception ,e:
                response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', 0, 'ERP'+response_type+'ID')
                response_data += "<RecordStatus>%s</RecordStatus>"%(e)
                
            response_data += "</%s>"%(response_name)
        
        return_response = STANDARD_LIST_RESPONSE % {'collectiondate':str(datetime.date.today()), 'responsename': response_service, 'responsedata':response_data}     
#         responseDOM = parseString(return_response) #Parsing the Response
#         print "Response from ERP:\n",responseDOM.toprettyxml()
    return return_response
