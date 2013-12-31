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
import math
class import_hijri_date(osv.osv_memory):
    _name='import.hijri.date'
    _columns={
            'file':fields.binary("File Path:"),
            'file_name':fields.char('File Name:'),
              }
    def intPart(self,floatNum):
        if floatNum < -0.0000001: return math.ceil(floatNum - 0.0000001)
        return math.floor(floatNum + 0.0000001)
    
    
    def Hijri2Gregorian(self,yr, mth, day):
        jd1 = self.intPart((11 * yr + 3) / 30.0)
        jd2 = self.intPart((mth - 1) / 2.0)
        jd = jd1 + 354 * yr + 30 * mth - jd2 + day + 1948440 - 385
    
        if jd > 2299160:
           l = jd + 68569
           n = self.intPart((4 * l) / 146097.0)
           l = l - self.intPart((146097 * n + 3) / 4.0)
           i = self.intPart((4000 * (l + 1)) / 1461001.0)
           l = l - self.intPart((1461 * i) / 4.0) + 31
           j = self.intPart((80 * l) / 2447.0)
           d = l - self.intPart((2447 * j) / 80.0)
           l = self.intPart(j / 11.0)
           m = j + 2 - 12 * l
           y = 100 * (n - 49) + i + l
        else:
           j = jd + 1402
           k = self.intPart((j - 1) / 1461.0)
           l = j - 1461 * k
           n = self.intPart((l - 1) / 365.0) - self.intPart(l / 1461.0)
           i = l - 365 * n + 30
           j = self.intPart((80 * i) / 2447.0)
           d = i - self.intPart((2447 * j) / 80.0)
           i = self.intPart(j / 11.0)
           m = j + 2 - 12 * i
           y = 4 * k + n + i - 4716
        d,m,y=int(d),int(m),int(y)
        birthday=str(y)+str('-')+str(m)+str('-')+str(d)
        return birthday
    
    def import_date_info(self,cr,uid,ids,context=None):
        cur_obj = self.browse(cr,uid,ids)[0]
        file_data=cur_obj.file
        val=base64.decodestring(file_data)
        fp = StringIO.StringIO()
        fp.write(val)     
        wb = xlrd.open_workbook(file_contents=fp.getvalue())
        sheet=wb.sheet_by_index(0)
        for i in range(1,sheet.nrows):
            first_date =sheet.row_values(i,0,sheet.ncols)[0]
            split_rec=first_date.split('/')
            day=int(split_rec[0])
            month=int(split_rec[1])
            year=int(split_rec[2])
            birth_date=self.Hijri2Gregorian(year, month, day)
            if first_date:
                emp_birthday=self.pool.get('hr.employee').create(cr,uid,{'name':'Test','birthday':birth_date})
            else:
                pass
        return True
