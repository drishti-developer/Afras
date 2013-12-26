from openerp.osv import fields, osv, orm
import time
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
import datetime

from dateutil.relativedelta import relativedelta
import calendar
from openerp.tools import float_compare
from openerp import netsvc
import openerp.addons.decimal_precision as dp


class fleet_vehicle(osv.osv):
    _inherit = "fleet.vehicle"
    
    _columns = {
    'product_id' : fields.many2one('product.product','Product'),
    'model_year' : fields.integer('Model Year'),
    'barcode' : fields.char('Vehicle Barcode',size=128),
    'choose_car' : fields.char('Choose Car(Native/Foreign)',size=128),
    'engine_number' : fields.char('Engine Number',size=128),
    'analytic_account_ids': fields.one2many('fleet.analytic.account', 'vehicle_id', 'Vehicle'),
    'branch_id': fields.many2one('sale.shop',  'Branch'),
    'area_id': fields.many2one('res.city.area',  'Area'),
    'city_id': fields.many2one('res.state.city',  'City'), 
    'region_id': fields.many2one('res.country.state',  'State'),
    'country_id': fields.many2one('res.country',  'Country'),
    'analytic_id': fields.many2one('account.analytic.account', 'Analytic Account', ),
    }
    
    _defaults = {
     'car_value' : 1,
     }
     
    def create(self, cr, uid, values, context=None):
        analytic_obj = self.pool.get('account.analytic.account')
        parent_id = analytic_obj.search(cr, uid, [('name','=','Vehicle')])
        analytic_id = analytic_obj.create(cr ,uid, {
                         'name': values['license_plate'],
                         'entry_type': 'car',
                         'parent_id':parent_id and parent_id[0] or False
                         })
        values['analytic_id'] = analytic_id
        
        id = super(fleet_vehicle,self).create(cr, uid, values, context=context)
        
        return id
    
    def write(self, cr, uid, ids, vals, context=None):
        fleet_analytic_account_obj = self.pool.get('fleet.analytic.account')
        assetObj = self.pool.get('account.asset.asset')
        
        super(osv.osv, self).write(cr, uid, ids, vals, context=context)
        fleet_obj = self.browse(cr, uid, ids[0], context=context)
        if 'analytic_account_ids' in vals:
           fleet_branch_ids = fleet_analytic_account_obj.search(cr,uid,[('vehicle_id','=',ids[0])],order='date_from ASC',)
           i =0
           for branch_id in  fleet_branch_ids:
               i +=1
               branchDict = fleet_analytic_account_obj.read(cr, uid, branch_id,['date_from','date_to'])
               if i ==1:
                   date_to = branchDict['date_to']
               if not branchDict['date_to'] and i != len(fleet_branch_ids):
                  raise osv.except_osv(_('To Date'),_("Please select to date of all branches except last branch") )
               if i>=2 and branchDict['date_from']<= date_to:
                   raise osv.except_osv(_('To Date'),_("Vehcle can not be assign to two branch on the same date") )
               else:
                   date_to = branchDict['date_to']
                       
               
           if fleet_branch_ids:
               date_from = fleet_analytic_account_obj.read(cr, uid, fleet_branch_ids[0],['date_from','date_to'])
               
               asset_id = assetObj.search(cr,uid,[('vehicle_id','=',ids[0])]) 
               if asset_id:
                   asset = assetObj.browse(cr,uid,asset_id[0])
                   if asset.depreciation_start_date > date_from['date_from'] and not asset.account_move_line_ids:
                       assetObj.write(cr, uid, asset_id[0],{'depreciation_start_date': date_from['date_from']})
                       assetObj.compute_depreciation_board(cr, uid, asset_id, context=context)      
              
        return True
    
fleet_vehicle()

class fleet_analytic_account(osv.osv):
    
    _name = "fleet.analytic.account"
    _rec_name = "vehicle_id"
    
    def _city(self, cr, uid, ids, name, args, context=None):
        res = {}
        for val in self.browse(cr,uid,ids):
            res[val.id] = False
            if val.segment == 'retail':
                if val.branch_id:
                    res[val.id] = val.branch_id.area_id and val.branch_id.area_id.city_id and val.branch_id.area_id.city_id.id or False
                
            else:
                if val.client_id:
                    res[val.id] = val.client_id.section_id and val.client_id.section_id.city_id and val.client_id.section_id.city_id.id or False
        return res
    
    _columns = {
            'vehicle_id' : fields.many2one('fleet.vehicle', 'Vehicle'),
            'branch_id': fields.many2one('sale.shop',  'Branch'),
            'area_id' : fields.related('branch_id','area_id',type='many2one',relation='res.city.area',string='Area',readonly=True,store=True),
            'city_id' : fields.function(_city, string='City',type='many2one',relation='res.state.city',store=True),
            'region_id' : fields.related('city_id','state_id',type='many2one',relation='res.country.state',string='Region',readonly=True,store=True),
            'country_id': fields.related('city_id', 'country_id', type='many2one', relation='res.country', string='Country', readonly=True,store=True),
            'company_id': fields.many2one('res.company','Company'), 
            'segment': fields.selection([('retail','Retail'),('corporate','Corporate')],'Segment'),                        
            'analytic_id' : fields.many2one('account.analytic.account','Analytic Account',),
            'date_from': fields.date('From Date',required=True),
            'date_to': fields.date('To Date'),
            'client_id':fields.many2one('res.partner','Client'),
            'team_id':fields.related('client_id','section_id',type='many2one',relation='crm.case.section',string='Team',readonly=True,store=True),
            }
    def create(self, cr, uid, data, context=None):
        lst=[]
        analytic_fleet_id=super(fleet_analytic_account, self).create(cr, uid, data, context=context)
        lst.append((0,0,{'analytic_id':data['analytic_id'],'from_date':data['date_from'],'to_date':data['date_to']})),
        account_asset_obj=self.pool.get('account.asset.asset')
        account_cost_center_obj=self.pool.get('account.asset.cost.center')
        asset_ids=account_asset_obj.search(cr,uid,([('vehicle_id','=',data['vehicle_id'])]))
        if asset_ids:
              account_costcenter_line_id = account_cost_center_obj.create(cr,uid,{'analytic_id':data['analytic_id'],'from_date':data['date_from'],'to_date':data['date_to'],'asset_id':asset_ids[0],'fleet_analytic_id':analytic_fleet_id},context=context)
        return analytic_fleet_id
    

    def write(self, cr, uid, ids, vals, context=None):
        res={}
        date_from=vals['date_from']
        to_date=vals['date_to']
        if date_from:
            date_from=vals['date_from']
            res.update({'from_date':date_from})
        if to_date:
            to_date=vals['date_to']
            res.update({'to_date':to_date})
        if date_from and to_date:
            res.update({'from_date':date_from,'to_date':to_date})     
        account_cost_center_obj=self.pool.get('account.asset.cost.center')
        account_asset_obj=self.pool.get('account.asset.asset')
        obj=self.browse(cr,uid,ids[0])
        asset_ids=account_asset_obj.search(cr,uid,([('vehicle_id','=',obj.vehicle_id.id)]))
        asset_line_ids=account_asset_obj.browse(cr,uid,asset_ids[0])
        cost_center_ids=account_cost_center_obj.search(cr,uid,[('fleet_analytic_id','=',ids)])
        if cost_center_ids:
            account_update=account_cost_center_obj.write(cr,uid,cost_center_ids,res,context=context)
        return super(fleet_analytic_account, self).write(cr, uid, ids, vals, context=context)
    
fleet_analytic_account()      
    
class fleet_type(osv.osv):
    _name = "fleet.type"    
    _columns = {
    'name' : fields.char('Car Type',size=128,required=True),
    }
    
fleet_type()

class fleet_vehicle_model(osv.osv):
    _inherit ="fleet.vehicle.model"

    _columns = {
                'fleet_type_id' : fields.many2one('fleet.type','Car Type', required=True),
                'variant' : fields.char('Variant',size=128),
                'engine_capacity' : fields.char('Engine Capacity',size=128),
                'transmission' : fields.char('Transmission',size=128,required=True),
                'no_of_seats' :  fields.integer('Number of Seats',required=True),
                'no_of_doors' : fields.integer('Number of Doors',required=True),
                'no_of_luggages' : fields.integer('Number of Luggages',required=True),
                'fuel':fields.char(string="Fuel",required=True,size=256)
                }
    
    
    def create(self, cr, uid, values, context=None):
        id=super(fleet_vehicle_model,self).create(cr, uid, values, context=context)
        brand_obj = self.pool.get('fleet.vehicle.model.brand').browse(cr, uid, values['brand_id'])
        
        dic = {
               'model_id' : id,
               'name':brand_obj.name + ' ' + values['modelname'],
               #'image_medium': values['image_medium'],
               'image_medium': values.get('image_medium', False),
               'car': True,
               'track_incoming': True, 
               'track_outgoing': True,
               
               }
        
        self.pool.get('product.product').create(cr,uid,dic)
        return id
    
fleet_vehicle_model()    
    
class fleet_vehicle_cost_distribution(osv.osv):
    
    _name = "fleet.vehicle.cost.distribution"
    _columns = {
                'name': fields.char('Name',size=128),
                'analytic_line_id' : fields.many2one('account.analytic.line','Analytic Line'),
                'move_id' : fields.many2one('account.move.line','Move Line'),
                'vehicle_id' : fields.many2one('fleet.vehicle','vehicle'),
                'branch_id': fields.many2one('sale.shop',  'Branch'),
                'account_id' : fields.many2one('account.account','Account'),
                'area_id': fields.many2one('res.city.area',  'Area'),
                'city_id': fields.many2one('res.state.city',  'City'), 
                'region_id': fields.many2one('res.country.state',  'State'),
                'country_id': fields.many2one('res.country',  'Country'),
                'segment': fields.selection([('retail','Retail'),('corporate','Corporate')],'Segment'),
                'company_id': fields.many2one('res.company',  'Company'),
                'debit' : fields.float('Revenue'),
                'credit': fields.float('Expenses'),
                'amount': fields.float('amount'),
                'date': fields.date('Date'),
                'entry_type': fields.selection([('car', 'Car'), ('branch', 'Branch'),
                                                 ('area', 'Area'), ('city', 'City'),
                                                 ('region', 'Region'), ('segment','Segment'),('company', 'Company'),
                                                 ], 'Cost Center Type',readonly=True),
    
                }
    
fleet_vehicle_cost_distribution()

class crm_case_section(osv.osv):
    _inherit='crm.case.section'
    _columns={
              'partner_ids':fields.one2many('res.partner','section_id','Client'),
              'analytic_id' : fields.many2one('account.analytic.account','Analytic Account'),
              'city_id' : fields.many2one('res.state.city', 'City', required=True),
              'state_id' : fields.related('city_id','state_id',type='many2one',relation='res.country.state',string='Region',readonly=True),
              'country_id': fields.related('state_id', 'country_id', type='many2one', relation='res.country', string='Country', readonly=True),
              'arabic_name':fields.char('Arabic Name',size=64)
              }

crm_case_section()