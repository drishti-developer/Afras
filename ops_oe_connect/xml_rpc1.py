#!/usr/bin/python
# -*- coding: utf-8  -*-

import xmlrpclib
user = 'admin'
pwd = 'admin'
#dbname = 'assets_management'
dbname= 'afras'
#Please change IP Address if you are not able access global IP address from Afras Network
#87.101.236.121:8069 or #172.16.1.54:8069

sock = xmlrpclib.ServerProxy('http://localhost:6118/xmlrpc/common')
uid = sock.login(dbname ,user ,pwd)
sock = xmlrpclib.ServerProxy('http://localhost:6118/xmlrpc/object')



# CREATE A PRODUCT CATEGORY
model = 'res.country'
country_list = sock.execute(dbname, uid, pwd, model, 'ListRecord')
import pprint 
#pprint.pprint(country_list)

COUNTRY_DIC=[{
            'ERPID':'1',
            'OPSID':'5',},
            {
            'ERPID':'194',
            'OPSID':'7',},
            ]

update_data=sock.execute(dbname, uid, pwd, model, 'UpdateRecord',COUNTRY_DIC)
#print "status==========",update_data


#region api's

model = 'res.country.state'

region_list = sock.execute(dbname, uid, pwd, model, 'ListRecord')
#pprint.pprint(region_list)
#print region_list,'list============'


REGION_DATA=[{
             'ERPID':'58',
             'OPSID':'12',
            },{
             'ERPID':'54',
             'OPSID':'15',
            }]

update_data=sock.execute(dbname, uid, pwd, model, 'UpdateRecord',REGION_DATA)


model = 'res.state.city'

region_list = sock.execute(dbname, uid, pwd, model, 'ListRecord')
#print region_list,


CITY_DATA={
             
            }

update_data=sock.execute(dbname, uid, pwd, model, 'UpdateRecord',CITY_DATA)


CREATE_CITY={
              'CITYNAME':'Demo City',
              'CITYNAMEARABIC':'الرياض',
              'CITYCODE':'RH',
              'CITYOPSID':'92',
              'COUNTRYERPID':'194',
              'REGIONERPID':'58',
             }

model='res.bank'
bank_list = sock.execute(dbname, uid, pwd, model, 'ListRecord')
pprint.pprint(bank_list)

BANK_DATA=[{
             'ERPID':'1',
             'OPSID':'12',
            },{
             'ERPID':'2',
             'OPSID':'15',
            }]
update_data=sock.execute(dbname, uid, pwd, model, 'UpdateRecord',BANK_DATA)  

Create_BANK_DATA={
             'BANKNAME':'Test Bank1',
             'IDENTIFIERCODE':'01010129847',
             'OPSID':'002',
             'COUNTRYERPID':'194'
            }


create_data=sock.execute(dbname, uid, pwd, model, 'CreateRecord',Create_BANK_DATA)  

model='purchase.order'
purchase_data={
           'PURCHASEORDERNO':'37',  
           'PURCHASEDATE':'2014-01-18',
           'PURCHASEMETHOD':'',
           'VENDORNO':'8',
           
           'PROJECTCODE':'1011',
           'PURCHASETYPE':'demo',
           'LOCATIONSERIALCOUNTER':'123',
           
           'QUOTATIONNUMBER':'partner_ref',
           #'RECORDSTATUS':'state',
           'TOTALAMOUNT':'1999',
           'DISCOUNTACT':'value',  #selection value/percentage
           'SERVICEACT':'service',
           'DEDUCTIONACT':'value', #selection value/percentage
           'DISCOUNTAMOUNT':'250',
           'DEDUCTIONAMOUNT':'150',
           'SERVICEAMOUNT':'99',
           'NETAMOUNT':'2500',
           'EXPENSETYPE':'revenue',
           'REIMBURSESTATUS':'reimurses',
           'REIMBURSECOMMAMOUNT':'1200',
           'REIMBURSABLEAMOUNT':'1250',
           'DetailData' : [{
                            'PURCHASEORDERNO': '37' ,
                            'PURCHASEDETAILID': '2',
                            'QUOTATIONNUMBER': 'qa1123' ,
                            'REQUESTNO' : '1059',
                            'REQUESTDETAILID' : '1',
                            'ITEMPRICE' : '10',
                             'ITEMTOTAL' : '50',
                             'UNITDISCOUNT' : '5',
                             'VENDORSTATUS' :'available',
                             'ADDITIONAL_CHARGE' : '5',
                             'QUANTITY' : '5',
                             'QDETNO' : '0012',
                            }]

           
           
           
           
           
   }
   
purchase_id=sock.execute(dbname, uid, pwd, model, 'CreateRecord',purchase_data) 


model='account.invoice.payment'

PAYMENT_TERM_DATA=[{
                  'PURCHASEORDERNO':'33',
                  'PAYMENTID':'2',
                  'PAYABLEAMOUNT':'1000',
                  'PLUSDAYS':'20',
                  'DUEDATE':'2014-02-02',
                  #'PAYMENTSTATUS':'active',
                  'PAYMENTREMARKS':'payment',
                  'REFERENCENO':'ref 32',
                  'INSTALLMENTNO':'1',
                  'PAYMENTTYPE':'cash',
                  'APPROVALSTATUS':'approve',
                  'BANKSTATUS':'paid',
                  'CHEQUENO':'',
                  'BANKACCOUNTNO':'',
                  },]
                  
payment_id=sock.execute(dbname, uid, pwd, model, 'CreateRecord',PAYMENT_TERM_DATA) 
model='res.partner'

ACCOUNTANT_DATA={
                 'VNO':'',
                'ACCOUNTANTID':'',
                'EMPLOYEECODE':'',
                'PROJECTCODE':'',
                'LOCATIONSERIALNUMBER':'',
                }
partner_id=sock.execute(dbname, uid, pwd, model, 'CreateRecord',PAYMENT_TERM_DATA) 

model='account.invoice'

LOAN_DATA  = {
                'LOANCODE':'',
                'ACCOUNTANTID':'',
                'LOANSTATUS':'',
                'ROLLBACKSTATUS':'',
                'ROLLBACKREMARK':'',
                'AMOUNT':'',
                'RMRGRANDTOTAL':'',
                'RMRAMOUNT':'',
                'ISBUDGET':'',
                'CREATEDDATE':'',
                'LOAN_REQUEST_DEATIL':[ {
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
                                            },   ],
                'LOAN_DATAIL_DATA':[{
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
                                            } , ],
                
               
               
            }

loan_id=sock.execute(dbname, uid, pwd, model, 'CreateRecord',LOAN_DATA) 











#create_data=sock.execute(dbname, uid, pwd, model, 'CreateRecord',CREATE_CITY)
#requisition_line_id = sock.execute(dbname, uid, pwd, model, 'CreateRecord', requisition_line_data) 

