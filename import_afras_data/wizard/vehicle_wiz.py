from osv import osv
from osv import fields
import datetime
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from tools.translate import _
import StringIO
import cStringIO
import base64
import xlrd
import string
class import_fleet(osv.osv_memory):
    _name='import.fleet'
    _columns={
            'file':fields.binary("File Path:"),
            'file_name':fields.char('File Name:'),
              }
    def import_fleet_info(self,cr,uid,ids,context=None):
        cur_obj = self.browse(cr,uid,ids)[0]
        file_data=cur_obj.file
        val=base64.decodestring(file_data)
        fp = StringIO.StringIO()
        fp.write(val)     
        wb = xlrd.open_workbook(file_contents=fp.getvalue())
        sheet=wb.sheet_by_index(0)
       # parent_id=parent1=parent2=parent3=parent4=parent5=parent6=False
        for i in range(1,sheet.nrows):
            plate_number =sheet.row_values(i,0,sheet.ncols)[0]
            brand_name =sheet.row_values(i,0,sheet.ncols)[2]
            modelname =sheet.row_values(i,0,sheet.ncols)[3]
            year =sheet.row_values(i,0,sheet.ncols)[4]
            serial =sheet.row_values(i,0,sheet.ncols)[5]
            vin_sn =sheet.row_values(i,0,sheet.ncols)[6]
            color =sheet.row_values(i,0,sheet.ncols)[7]
            status =sheet.row_values(i,0,sheet.ncols)[9]
            vin =sheet.row_values(i,0,sheet.ncols)[6]
            brand_id=self.pool.get('fleet.vehicle.model.brand').search(cr,uid,[('name','ilike',brand_name)])
            if brand_id:
                model_id=self.pool.get('fleet.vehicle.model').search(cr,uid,[('modelname','ilike',modelname),('brand_id','=',brand_id[0])])
                if model_id and isinstance(model_id,(list,tuple)):
                    model_id=model_id[0]
                if not model_id:
                    model_id=self.pool.get('fleet.vehicle.model').create(cr,uid,{'modelname':modelname,'arabic_name':modelname,'brand_id':brand_id[0],'transmission':'Manual','fuel':'Petrol','fleet_type_id':1,
                                                                                 'no_of_seats':0,'no_of_doors':0,'no_of_luggages':0})
            else:
                brand_id=self.pool.get('fleet.vehicle.model.brand').create(cr,uid,{'name':brand_name,'arabic_name':brand_name,'routine_service_mileage':'1'})
                model_id=self.pool.get('fleet.vehicle.model').search(cr,uid,[('modelname','ilike',modelname),('brand_id','=',brand_id)])
                if model_id and isinstance(model_id,(list,tuple)):
                    model_id=model_id[0] 
                if not model_id:
                    model_id=self.pool.get('fleet.vehicle.model').create(cr,uid,{'modelname':modelname,'arabic_name':modelname,'brand_id':brand_id,'transmission':'Manual','fuel':'Petrol',
                                                                                 'fleet_type_id':1,'no_of_seats':0,'no_of_doors':0,'no_of_luggages':0})
            if model_id:
                vehicle_id=self.pool.get('fleet.vehicle').create(cr,uid,{'model_id':model_id,'license_plate':plate_number,'license_plate_arabic':plate_number,'barcode':serial,'vin_sn':vin_sn,
                                                                     'assigned_for':'Retail','color':color,'color_arabic':color})
        return True
