from osv import osv,fields
import datetime

class fleet_vehicle_insurance(osv.osv):
    _name='fleet.vehicle.insurance'
    _columns={
              'car_insurance_no':fields.char('Name',size=64,required=True),
              'insurance_start_date': fields.date('Insurance Start Date'),
              'insurance_end_date': fields.date('Insurance End Date'),
              'vehicle_ids':fields.many2many('fleet.vehicle','fleet_insu_table','fleet_id','vehicle_id','Vehicle')
              }
fleet_vehicle_insurance()


class fleet_vehicle_registration(osv.osv):
    _name='fleet.vehicle.registration'
    _columns={
              'car_insurance_no':fields.char('Name',size=64,required=True),
              }
fleet_vehicle_registration()