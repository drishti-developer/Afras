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
from openerp.osv import osv
from openerp.tools.translate import _
import datetime
import urllib
from xml.dom.minidom import parseString
import logging

_logger = logging.getLogger('CRMSLOG')

STANDARD_LIST_RESPONSE = """<?xml version="1.0" encoding="utf-8"?><ResponseGroup xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><ERPResponse><ResponseData DataCollectionDate="%(collectiondate)s" ResponseService="%(responsename)s"><ResponseCode>1</ResponseCode><ResponseMessage>%(success)s - SUCCESS, %(failure)s - FAILURE</ResponseMessage>%(responsedata)s</ResponseData></ERPResponse></ResponseGroup>"""

STANDARD_LIST_ERROR_RESPONSE = """<?xml version="1.0" encoding="utf-8"?><ResponseGroup xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><ERPResponse><ResponseData DataCollectionDate="%(collectiondate)s" ResponseService="%(responsename)s"><ResponseCode>0</ResponseCode><ResponseMessage>FAILURE - %(responsedata)s</ResponseMessage></ResponseData></ERPResponse></ResponseGroup>"""

VIEW_CLASS_LIST = ['res.currency', 'res.country', 'res.country.state', 'res.state.city', 'res.city.area', 'sale.shop', 'fleet.vehicle.model.brand', 'fleet.type', 'fleet.vehicle.model','fleet.vehicle','res.partner',]

CREATE_CLASS_LIST = ['res.partner', 'crms.payment', 'fleet.vehicle', 'crms.daily.revenue','crms.payment.car.history','crms.cash.branch','crms.payment.initializelive']

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
			('code','BranchCode'),
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
			('location','Location'),
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
            ('exa','Exa'),
            ]

RENTAL_PAYMENT_LIST = [
			('id','ERPBookingID'),
            ('crms_id','CRMSBookingID'),
            ('partner_id',('id','ERPCustomerID',0,'res.partner')),
            ('vehicle_id',('id','ERPCarID',0,'fleet.vehicle')),
            ('car_type_id',('id','ERPCarTypeID',0,'fleet.type')),
            ('model_id',('id','ERPModelID',0,'fleet.vehicle.model')),
            ('crms_payment_id','CRMSRentalPaymentID'),
            ('rental_from_date','RentalFromDate'),
            ('rental_to_date','RentalToDate'),
            ('no_of_days','NoOfDays'),
            ('no_of_hours','NoOfHours'),
            ('pickup_branch_id',('id','ERPPickupBranchID',0,'sale.shop')),
            ('drop_branch_id',('id','ERPDropBranchID',0,'sale.shop')),
            ('booking_branch_id',('id','ERPBookingBranchID',0,'sale.shop')),
            ('amount_paid','AmountPaidByCustomer'),
            ('amount_receive_date','AmountReceivedDate'),
            ('rental_amount','RentalAmount'),
            ('amount_returned','AmountReturned'),
            ('amount_returned_date','AmountReturnedDate'),
            ('holding_amount','HoldingAmount'),
            ('advance_amount','Advance'),
            ('balance_due_amount','BalanceDue'),
            ('admin_expenses','AdminExpenses'),
            ('damage_charges','DamageCharges'),
            ('other_charges','OtherCharges'),
            ('extra_hour_charges','AdditionalHourCharges'),
            ('extra_km_charges','ExtraKMCharges'),
            ('additional_driver_charges','AdditionalDriverCharges'),
            ('payment_type','PaymentMode'),
            ('state','RentalStatus'),
            ('per_day_amount','RatePerDay'),
            ('rental_extension','RentalExtension'),
            ('exa','Exa'),
            ('discount','Discounts'),
            ('discount_date','DiscountDate'),
            ('crms_discount_id','CRMSDiscountID'),
            ('traffic_violation_charges','TrafficViolationCharges'),
            ('traffic_violation_charges_date','TrafficViolationDate'),
            ('crms_traffic_violation_id','CRMSTrafficViolationID'),
            ]

INTERMEDIATE_PAYMENT_LIST = [
			('date','Date'),
			('crms_payment_id','ERPRentalPaymentID'),
			('amount','AmountPaid'),
			('payment_type','PaymentMode'),
			]

DISCOUNT_LIST = [
			('date','Date'),
			('crms_payment_id','ERPRentalPaymentID'),
			('discount','Discount'),
			]

DAILY_REVENUE_LIST = [
			('booking_id','ERPBookingID'),
			('date','Date'),
			('open_balance','OpenBalance'),
			('revenue','Revenue'),
			('discount','Discount'),
			('discount_amt','DiscountAmount'),
			('changed_discount','ChangedDiscount'),
			('amount_paid','AmountPaid'),
            ('amount_returned','AmountReturned'),
            ('admin_expenses','AdminExpenses'),
            ('damage_charges','DamageCharges'),
            ('traffic_violation_charges','TrafficViolationCharges'),
            ('other_charges','OtherCharges'),
            ('extra_hours_charges','AdditionalHourCharges'),
            ('extra_km_charges','ExtraKMCharges'),
            ('additional_driver_charges','AdditionalDriverCharges'),
            ('vehicle_id','ERPCarID'),
			]

CAR_HISTORY = [
            ('booking_id','ERPBookingID'),
            ('car_id','ERPCarID'),
            ('vehicle_model','ERPModelID'),
            ('change_date','ChangeDate'),
           ]

CASH_BRANCH = [
           ('date','Date'),
           ('branch_opening_bal','BranchOpeningBalance'),
           ('cash_received','CashReceived'),
           ('cash_paid','CashPaid'),
           ('branch_expenses_related_to_vehicle','BranchExpensesRelatedtoVehicle'),
           ('total_branch_expenses','TotalBranchExpenses'),
           ('cash_paid_head_office','CashPaidHeadOffice'),
           ('closing_bal','ClosingBalance'),
           ('branch_id','ERPBranchID'),
           ]

RENTAL_INITIALIZE = [
            ('crms_id','CRMSBookingID'),
            ('partner_id',('id','ERPCustomerID',0,'res.partner')),
            ('vehicle_id',('id','ERPCarID',0,'fleet.vehicle')),
            ('model_id',('id','ERPModelID',0,'fleet.vehicle.model')),
            ('rental_from_date','RentalFromDate'),
            ('rental_to_date','RentalToDate'),
            ('pickup_branch_id',('id','ERPBranchID',0,'sale.shop')),
            ('receivable_amt','ReceivableAmount'),
            ('live_date','LiveDate'),
            ('advance_amt','AdvanceAmount'),
            ('balance_due_amount','BalanceDue'),
            ('payment_type','PaymentMode'),
            ('state','RentalStatus'),
            ('per_day_amount','RatePerDay'),
            ('exa','Exa'),
            ('discount','Discounts'),
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
            _logger.info('Request Send to CRMS for %s :- %s', request_type, request_data)
            encoded_data = urllib.quote_plus(request_data.encode('utf-8')) # Encoding the XML Request
            encoded_data = "xml="+encoded_data
            #print "Encoded Requested Data:\n",encoded_data
            webf = urllib.urlopen(self.URL, encoded_data) #Sending the URL Request with encoded code using urllib library
            response = webf.read() #Web Response
            _logger.info('Return Response from CRMS for %s :- %s', request_type, response)
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
            acc_obj.write(cr,uid,[fleet_account_id],{'date_to':date_today})

    else :
        acc_obj.create(cr,uid,{'vehicle_id':car_id,'branch_id':branch_id,'date_from':date_today,'segment':'retail'})
    
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

# 1.LIST REQUEST (Send Response to CRMS for its particular Request).    
@extend(Model)
def ListRequest(self, cr, uid, date_from=False, date_to=False):
    
    return_response = "Invalid Request"
    if self._name in VIEW_CLASS_LIST:
        domain = ['|',('crms_id','!=',False),('crms_id','>',0)]
        browse_list = []
        response_name = False
        if self._name == 'res.currency':
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
        
        _logger.error('List Request from CRMS for %s from:%s to:%s', response_name, str(date_from), str(date_to))

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
        _logger.error('List Request Response for %s:- %s', response_name, return_response)
#         responseDOM = parseString(return_response) #Parsing the Response
#         print "Response from CRMS:\n",responseDOM.toprettyxml()
    return return_response

# 2.CREATE REQUEST (Create/Update record in OpenERP w.r.t. it's model)
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
        elif self._name == 'crms.daily.revenue':#Daily Revenue
            response_type = 'DailyRevenue'
            field_list = DAILY_REVENUE_LIST
        elif self._name == 'crms.payment.car.history':#CAR HISTORY
            response_type = 'CarHistory'
            field_list = CAR_HISTORY
        elif self._name == 'crms.cash.branch':#CRMS CASH BRANCH
            response_type = 'CashBranch'
            field_list = CASH_BRANCH
        elif self._name == 'crms.payment.initializelive':#CRMS CASH BRANCH
            response_type = 'RentalInitializeLive'
            field_list = RENTAL_INITIALIZE
                         
        response_data = ''
        response_name = response_type+"Response"
        response_service = response_type+"CreateResponse"
        _logger.info(data)
        data = data.strip()
        data = " ".join(data.split())
        data = data.replace('&','&amp;')
        data = data.encode('utf-8')
        _logger.info('Create Request from CRMS for %s :- %s', response_name, data)
        
        try :
            success = 0
            failure = 0
            responseDOM = parseString(data)
            responsearray = getDataArray(responseDOM, 'RequestData', response_type+'List', response_type)       
            for response in responsearray:
                crms_id=False
                response_data += "<%s>"%(response_name)
                if response_type == 'RentalPayment' : crms_id = response.get('CRMSBookingID',False)
                
                elif response_type not in ['DailyRevenue','RentalInitializeLive'] : crms_id = response.get('CRMS'+response_type+'ID',False)

                if response_type == 'DailyRevenue' : search_id = self.search(cr,uid,[('booking_id','=',int(response.get('ERPBookingID'))),('date','=',response.get('Date'))])
                
                elif response_type == 'Car' : search_id = self.search(cr,uid,[('vin_sn','=',str(response.get('VIN')))])
                
                elif response_type == 'CarHistory' : search_id = self.search(cr,uid,[('booking_id','=',int(response.get('ERPBookingID'))),('car_id','=',response.get('ERPCarID')),('change_date','=',response.get('ChangeDate'))])
                
                elif response_type == 'CashBranch': search_id = self.search(cr,uid,[('branch_id','=',int(response.get('ERPBranchID'))),('date','=',response.get('Date'))])

                elif crms_id : search_id = self.search(cr,uid,[('crms_id','=',int(crms_id))])

                else : search_id = []

                record_value = {}
                payment_id = 0
                discount_id = 0
                traffic_violation_id = 0
                booking_id = 0
                branch_id = 0
                
                for field in field_list:
                    if field[0] not in ['id','current_branch_id']:#skip fields
                        if field[0] == 'analytic_account_ids' and len(search_id) > 0 and response.get(field[1],False):
                            search_branch(self,cr,uid,search_id[0],response.get(field[1]))
                        else :
                            if isinstance(field[1],tuple):
                                ext_field = field[1]
                                if ext_field[0] not in ['crms_id'] and response.get(ext_field[1],False):#skip fields
                                    search_value_id = self.pool.get(ext_field[3]).search(cr,uid,[(ext_field[0],'=',response.get(ext_field[1]))])
                                    record_value[field[0]] = search_value_id and search_value_id[0] or ext_field[2]
                            elif response.get(field[1],False) :
                                record_value[field[0]] = response.get(field[1],False)
                                if field[1] == 'CRMSRentalPaymentID' :  payment_id = response.get(field[1])
                                if field[1] == 'CRMSDiscountID' :  discount_id = response.get(field[1])
                                if field[1] == 'CRMSTrafficViolationID' :  traffic_violation_id = response.get(field[1])
                                if field[1] == 'ERPBookingID' and response_type in ['DailyRevenue','CarHistory']:  booking_id = response.get(field[1])
                                if field[1] == 'CRMSBookingID' and response_type == 'RentalInitializeLive' :  booking_id = response.get(field[1])
                                if field[1] == 'ERPBranchID' and response_type == 'CashBranch':  branch_id = response.get(field[1])

                try :
                    msg = 'SUCCESS'
                    record_id = 0
                    
                    #Creating record.
                    if len(search_id) == 0 and record_value : record_id = self.create(cr,uid,record_value,{'mail_create_nosubscribe':True,'crms_create':True})
                    
                    #Updating record.
                    elif len(search_id) > 0 and record_value:
                        self.write(cr,uid,search_id,record_value)
                        record_id = search_id[0]
                    
                    #If search condition is not matching with the either of the condition then FAILURE msg will be send.
                    else :
                        msg = 'FAILURE'
                        success -= 1
                        failure += 1
    
                    if response_type in ['RentalPayment', 'RentalInitializeLive'] :
                        
                        response_data += "<%s>%s</%s>"%('ERPBookingID', record_id, 'ERPBookingID')
                        if  response_type ==  'RentalInitializeLive':
                            response_data += "<%s>%s</%s>"%('CRMSBookingID', booking_id or 0, 'CRMSBookingID')
                        else:
                            response_data += "<%s>%s</%s>"%('CRMSBookingID', crms_id or 0, 'CRMSBookingID')
                            
                        cr.execute("""select message_id from crms_payment where id=%s""",(record_id,))
                        msg_id = cr.fetchone()
                        response_data += "<%s>%s</%s>"%('ERPTransactionID', msg_id and msg_id[0] or 0, 'ERPTransactionID')
                        
                        if payment_id :
                            cr.execute('select id from crms_payment_intermediatepayment_history where crms_id=%s',(payment_id,))
                            record_id = cr.fetchone()
                            response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', record_id and record_id[0] or 0, 'ERP'+response_type+'ID')
                            response_data += "<%s>%s</%s>"%('CRMS'+response_type+'ID', payment_id, 'CRMS'+response_type+'ID')
                            
                        if discount_id :
                            cr.execute('select id from crms_payment_discount_history where crms_id=%s',(discount_id,))
                            record_id = cr.fetchone()
                            response_data += "<%s>%s</%s>"%('ERPDiscountID', record_id and record_id[0] or 0, 'ERPDiscountID')
                            response_data += "<%s>%s</%s>"%('CRMSDiscountID', discount_id, 'CRMSDiscountID')
                            
                        if traffic_violation_id :
                            cr.execute('select id from crms_payment_traffic_violation_history where crms_id=%s',(traffic_violation_id,))
                            record_id = cr.fetchone()
                            response_data += "<%s>%s</%s>"%('ERPTrafficViolationID', record_id and record_id[0] or 0, 'ERPTrafficViolationID')
                            response_data += "<%s>%s</%s>"%('CRMSTrafficViolationID', traffic_violation_id, 'CRMSTrafficViolationID')
                            
                    elif response_type == 'DailyRevenue' :
                        response_data += "<%s>%s</%s>"%('ERPBookingID', booking_id or 0, 'ERPBookingID')
                        response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', record_id, 'ERP'+response_type+'ID')
                    
                    elif response_type == 'CarHistory' : 
                        response_data += "<%s>%s</%s>"%('ERPBookingID', booking_id or 0, 'ERPBookingID')
                        response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', record_id, 'ERP'+response_type+'ID')
                   
                    elif response_type == 'CashBranch' : 
                        response_data += "<%s>%s</%s>"%('ERPBookingID', branch_id or 0, 'ERPBookingID')
                        response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', record_id, 'ERP'+response_type+'ID')
                    
                    else :    
                        response_data += "<%s>%s</%s>"%('CRMS'+response_type+'ID', crms_id or 0, 'CRMS'+response_type+'ID')
                        response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', record_id, 'ERP'+response_type+'ID')
                    
                    response_data += "<RecordStatus>%s</RecordStatus>"%(msg)
                    success += 1
                    
                except Exception ,e:
                    if response_type == 'RentalInitializeLive':
                        response_data += "<%s>%s</%s>"%('ERPBookingID', 0, 'ERPBookingID')
                    else:
                        response_data += "<%s>%s</%s>"%('ERP'+response_type+'ID', 0, 'ERP'+response_type+'ID')
                    if crms_id:
                        response_data += "<%s>%s</%s>"%('CRMS'+response_type+'ID', crms_id, 'CRMS'+response_type+'ID')
                    response_data += "<RecordStatus>FAILURE - %s</RecordStatus>"%(e)
                    failure += 1

                response_data += "</%s>"%(response_name)

            return_response = STANDARD_LIST_RESPONSE % {'collectiondate':str(datetime.date.today()), 'responsename': response_service, 'responsedata':response_data,'success':success,'failure':failure}
#             _logger.info('Return Response for %s :- %s', response_name, return_response)
# 	          responseDOM = parseString(return_response) #Parsing the Response
# 	          print "Response from ERP:\n",responseDOM.toprettyxml()
        except Exception ,e:
            _logger.error('Error Occured while processing the %s request:- %s', response_type, e)
            return_response = STANDARD_LIST_ERROR_RESPONSE % {'collectiondate':str(datetime.date.today()), 'responsename': response_service, 'responsedata':e}
        _logger.info('Return Response for %s :- %s', response_name, return_response)

    return return_response