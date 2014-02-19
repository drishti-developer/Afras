# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import fields, osv
import StringIO
import base64
import xlrd
from datetime import timedelta
import datetime
DATA_DIC={
         
           'Computer Hardware':8,
           'Furniture':4,
           'Equipments & Tools':3,
           'Prefabricated buildings':28,
           
            }

class data_import(osv.osv_memory):
    _name='data.import'
    _columns={
              'file':fields.binary("File Path:",required=True),
              'file_name':fields.char('File Name:'),
              'date' : fields.date('Depreciation Last date',required=True),
              'category_id': fields.many2one('account.asset.category','Asset Category', required=True),
              'company_id':fields.many2one('res.company','Company'),
              'page_index' : fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Page Index'),
              }
    
    
    def import_data(self,cr,uid,ids,context=None):
        assetObj = self.pool.get('account.asset.asset')
        analytic_Obj = self.pool.get('account.analytic.account')
        dataObj = self.browse(cr,uid,ids)[0]
        val=base64.decodestring(dataObj.file)
        fp = StringIO.StringIO()
        fp.write(val)     
        wb = xlrd.open_workbook(file_contents=fp.getvalue())
        sheet=wb.sheet_by_index(1)
        companyId = 1
        analyticId = 4762
       
        i =1
        assetDic ={
                   'company_id':companyId,
                   }
        for i in range(1,sheet.nrows):
            categoryName =sheet.row_values(i,0,sheet.ncols)[2]
            categoryId = DATA_DIC.get(categoryName,False)
            result = assetObj.onchange_category_id(cr, uid,  [],categoryId)
            assetDic.update(result['value'])
            purchase_date=sheet.row_values(i,0,sheet.ncols)[5]
            purchase_date_conv= datetime.date(1900, 1, 1) + datetime.timedelta(int(purchase_date)-2)
            depreciation_date=sheet.row_values(i,0,sheet.ncols)[11]
            depreciation_date_conv= datetime.date(1900, 1, 1) + datetime.timedelta(int(depreciation_date)-2)
            analytic_create_id=analytic_Obj.create(cr,uid,{'name':sheet.row_values(i,0,sheet.ncols)[7]})
            assetDic.update({'name' :sheet.row_values(i,0,sheet.ncols)[7],
                             'category_id': categoryId,
                             'purchase_date':purchase_date_conv, #5
                             'cost_analytic_id' : analyticId,
                             'analytic_id' : analytic_create_id,
                             'depreciation_start_date':depreciation_date_conv, #11
                             'purchase_value':sheet.row_values(i,0,sheet.ncols)[8],
                             'prorata' : True,
                             'cost_center_ids':  [(0,0,{
                                                         'analytic_id': analyticId,
                                                         'from_date' : purchase_date_conv, #5
                                                })],
                             
                        })
            assetQty = int(sheet.row_values(i,0,sheet.ncols)[9])
            for j in range(assetQty):
                assetObj.create(cr ,uid,assetDic)
        return True  
    
    
#     def import_data1(self,cr,uid,ids,context=None):
#         
#         depreciation_lin_obj = self.pool.get('account.asset.depreciation.line')
#         asset_obj = self.pool.get('account.asset.asset')
#         fleet_obj = self.pool.get('fleet.vehicle')
#         
#         cur_obj = self.browse(cr,uid,ids)[0]
#         val=base64.decodestring(cur_obj.file)
#         fp = StringIO.StringIO()
#         fp.write(val)     
#         wb = xlrd.open_workbook(file_contents=fp.getvalue())
#         sheet=wb.sheet_by_index(0)
#         i = 1801
#         dep_start_date = datetime.strptime(cur_obj.date,"%Y-%m-%d") + timedelta(days=1)
#         tot_dep_days = 365*5
#         
#         while i < 2175:
#             
#             asset_name =sheet.row_values(i,0,sheet.ncols)[0]
#             asset_id = asset_obj.search(cr, uid, [('name','ilike',asset_name)])
#             if not asset_id:
#                 vehicle_id = fleet_obj.search(cr, uid, [('license_plate_arabic','ilike',asset_name)])
#                 if vehicle_id:
#                     vehicle_obj = fleet_obj.browse(cr, uid, vehicle_id[0])
#                     analytic_id = vehicle_obj.analytic_id.id
#             
#                     purchase_date =datetime.strptime(sheet.row_values(i,0,sheet.ncols)[1],"%Y/%m/%d")
#                     gross_value =sheet.row_values(i,0,sheet.ncols)[2]
#                     acumulated_depreciation = sheet.row_values(i,0,sheet.ncols)[3]
#                     
#                     already_dept_days = (dep_start_date - purchase_date).days
#                     remaining_days = tot_dep_days - already_dept_days
#                     depreciation_per_days = gross_value/tot_dep_days
#                     real_accumlated_dept = already_dept_days *depreciation_per_days
#                     dept_arrear  =  real_accumlated_dept-acumulated_depreciation
#                     value_residual = gross_value - real_accumlated_dept
#                     
#                     asset_id = asset_obj.create(cr ,uid, {
#                     'name' : asset_name,
#                     'vehicle_id' : vehicle_id[0],
#                     'category_id' : cur_obj.category_id.id,
#                     'purchase_date':purchase_date,
#                     'depreciation_start_date' : dep_start_date,
#                     'purchase_value':gross_value,
#                     'method_number' : remaining_days,
#                     'value_residual' : value_residual,
#                     'depreciation_period' : 'days',
#                     'cost_analytic_id': analytic_id or 26,
#                     'method_period': 1,
#                     'non_depreciation_value' : 0,
#                     'non_depreciation_period' : 'days',
#                     'prorata' : True,
#                     'already_depreciated_amt' :real_accumlated_dept ,
#                     'dept_arrear' : dept_arrear, 
#                     'analytic_id': analytic_id,
#                     })
#                     
#                     asset_obj.write(cr, uid,asset_id,{'already_depreciated_amt' : acumulated_depreciation, 'method_number':tot_dep_days} )
#             
#                     vals = {
#                     'amount': dept_arrear,
#                     'asset_id': asset_id,
#                     'sequence': 1,
#                     'name': 'test',
#                     'remaining_value': 0,
#                     'depreciated_value': gross_value-dept_arrear,
#                     'depreciation_date': datetime.strptime(cur_obj.date,"%Y-%m-%d") +timedelta(days=remaining_days+1),
#                     }
#                     
#                     if dept_arrear and dept_arrear < 0:
#                         number = int(dept_arrear/depreciation_per_days) *-1
#                         dep_date1 = datetime.strptime(cur_obj.date,"%Y-%m-%d") + timedelta(days=(remaining_days-number-1)) 
#                         depreciated_value1 =   dept_arrear*-1 - depreciation_per_days*number
#                         vals['amount'] = depreciated_value1
#                         vals['depreciated_value'] = gross_value-depreciated_value1
#                         vals['depreciation_date'] = dep_date1
#                         #dep_date = datetime.strptime(cur_obj.date,"%Y-%m-%d") + timedelta(days=(remaining_days-number))    
#                         line_id = depreciation_lin_obj.search(cr, uid, [('asset_id','=',asset_id),('remaining_value','<',0 )])
#                         depreciation_lin_obj.unlink(cr,uid,line_id)
#                     depreciation_lin_obj.create(cr, uid,vals)
#             
#             i +=1
#                    
#         return True
    
data_import()
