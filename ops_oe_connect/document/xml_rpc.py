#!/usr/bin/python
# -*- coding: utf-8  -*-

import xmlrpclib
user = 'admin'
pwd = 'admin'
#dbname = 'assets_management'
dbname= 'ops_openerp'
#Please change IP Address if you are not able access global IP address from Afras Network
#87.101.236.121:8069 or #172.16.1.54:8069

sock = xmlrpclib.ServerProxy('http://87.101.236.120:8069/xmlrpc/common')
uid = sock.login(dbname ,user ,pwd)
sock = xmlrpclib.ServerProxy('http://87.101.236.120:8069/xmlrpc/object')

#sock = xmlrpclib.ServerProxy('http://localhost:6122/xmlrpc/common')
#uid = sock.login(dbname ,user ,pwd)
#sock = xmlrpclib.ServerProxy('http://localhost:6122/xmlrpc/object')


# CREATE A PRODUCT CATEGORY
model = 'product.category'
		
category_data = {'CATEGORYCODE': 2,'DESCRIPTIONE':'Computers', 
'DESCRIPTIONA': 'أجهزة حاسب آلي',
'CATEGORYSTATUS':'A',
}

category_id = sock.execute(dbname, uid, pwd, model, 'CreateRecord', category_data)
model = 'product.product'
product_data = {
'ITEMNAMEE':'Screen (Monitor)', 
'ITEMNAMEA':'شاشة', 
'ITEMNUMBER':1,
'CATEGORYCODE':1,
'ITEMSTATUS':'A'
}
product_id = sock.execute(dbname, uid, pwd, model, 'CreateRecord', product_data)

model = 'res.partner'
supplier_data = {
'VNO':141,
'VNAMEA':'الشركه السعوديه لانتاج مواد النظافه',
'FAX':'172233428',
'COUNTRY':'Saudi Arabia',
'CITY':'خميس مشيط',
'ADDRESS1':'خميس مشيط حي الهضبه',
'ADDRESS2':'الدمام المنطقه الصناعيه الثانيه',
'REGION' : 'محافظة عسير',
'EMAIL':'farag@sidco.com.sa',
'WEBSITE':'www.sidco com.sa',
'TELEPHONE':'172230807',
'ETELEPHONE': False,
'ETAX' : False,
'VNAMEE':'saudi industrial detergents co',
'STATUS':'A',
'MAXCREDITLIMIT':0,
'CRNO': False,
'CONTACTNO':'966556369979',
'CONTACTNAME':'محمد حنفي نصار',
'ECONTACTNO': False,
'OWNERNAME':'سعيد رداد سعيد الزهراني',
'OWNEREMAIL':'farag@sidco.com.sa',
'OWNERNUM':'556369979',
'CEONAME':'سعيد رداد سعيد الزهراني',
'BANKID':'9',   
'BENEFICIARYNAME':'الشركه السعوديه لانتاج مواد النظافه',
'ACCOUNTNO':'108009491260017',
'BRANCH':'324',
'IBAN':'108009491260017',
} 
SA3630400


#partner_id = sock.execute(dbname, uid, pwd, model, 'CreateRecord', supplier_data)            
print"======PRODUCT===5====",product_id

model = 'purchase.requisition'

requisition_data = {

'REQUESTNO': 1059,
'REQUESTDATE':'10/10/2010 00:00:00',
#'REQUESTSTATUS':'A',
'PROJECTCODE':'1011',
'LOCATIONSERIALCOUNTER':False,
'PURPOSE':'For Computer Section Use',
'RMRNUMBER':'',
'ISBUDGET': 0
}
#requisition_id = sock.execute(dbname, uid, pwd, model, 'CreateRecord', requisition_data) 

model = 'purchase.requisition.line'
requisition_line_data = {
'REQUESTNO':'1059',
'ITEMNUMBER':'1',
'QUANTITY':1,
'UNITTYPE':False,
'PURPOSE':'Nova',
#'RQSTDETAILSTATUS':'A',
'REQUESTDETAILID':1,
}
#requisition_line_id = sock.execute(dbname, uid, pwd, model, 'CreateRecord', requisition_line_data) 

