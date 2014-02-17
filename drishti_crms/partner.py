from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = "res.partner"    
    _columns = {
    'customer_type': fields.selection([('retailer', 'Retailer'), ('corporate', 'Corporate')], 'Customer Type',),
    'city_id': fields.many2one('res.state.city','City'),
    'account_analytic_id':fields.many2one('account.analytic.account','Analytic Account'),
    }
    
#     def onchange_city(self, cr, uid, ids, city_id, context=None):
#         if city_id:
#             city_obj = self.pool.get('res.state.city').browse(cr, uid, city_id, context)
#             state_id = city_obj.state_id.id
#             country_id = city_obj.country_id.id
#             city = city_obj.name
#             return {'value':{'city':city,'state_id': state_id, 'country_id':country_id}}
#         return {}
res_partner()
    
class res_country(osv.osv):
    _inherit = "res.country"    
    _columns = {
    'calling_code': fields.char('Calling Code',size=10,required=True),
    'analytic_id' : fields.many2one('account.analytic.account','Analytic Account'),
    'analytic_ids': fields.one2many('account.analytic.account', 'country_id', 'Analytic Accounts'),
    'car_ids': fields.one2many('fleet.analytic.account', 'country_id', 'Car'),
    }
    
res_country()

class CountryState(osv.osv):
    _inherit = "res.country.state"
    _columns = {
    'name' : fields.char('Region Name',required=True, size=20),
    'code': fields.char('Region Code', size=3,help='The Region code in max. three chars.', required=True),
    'analytic_id' : fields.many2one('account.analytic.account','Analytic Account',),    
    'analytic_ids': fields.one2many('account.analytic.account', 'region_id', 'Analytic Accounts'),
    'car_ids': fields.one2many('fleet.analytic.account', 'region_id', 'Car'),
    }
    
CountryState()

class res_state_city(osv.osv): 
    _name = "res.state.city"    
    _columns = {
    'name' : fields.char('City Name',required=True,size=30),
    'code': fields.char('City Code', size=3,help='The City code in max. three chars.', required=True),
    'state_id' : fields.many2one('res.country.state','Region',required=True),
    'country_id': fields.related('state_id', 'country_id', type='many2one', relation='res.country', string='Country', readonly=True),
    'analytic_id' : fields.many2one('account.analytic.account','Analytic Account'),
    'analytic_ids': fields.one2many('account.analytic.account', 'city_id', 'Analytic Accounts'),
    'car_ids': fields.one2many('fleet.analytic.account', 'city_id', 'Car'),
    }

res_state_city()

class res_city_area(osv.osv): 
    _name = "res.city.area"    
    _columns = {
    'name' : fields.char('Area Name',required=True,size=30),
    'code': fields.char('Area Code', size=3,res_companyhelp='The Area code in max. three chars.', required=True),
    'city_id' : fields.many2one('res.state.city', 'City', required=True),
    'state_id' : fields.related('city_id','state_id',type='many2one',relation='res.country.state',string='Region',readonly=True),
    'country_id': fields.related('state_id', 'country_id', type='many2one', relation='res.country', string='Country', readonly=True),
    'analytic_id' : fields.many2one('account.analytic.account','Analytic Account',),
    'analytic_ids': fields.one2many('account.analytic.account', 'area_id', 'Analytic Accounts'),
    'car_ids': fields.one2many('fleet.analytic.account', 'area_id', 'Car'),
    }
    _sql_constraints = [
        ('name_area_uniqie', 'unique (name)', 'The Area name must be unique !')
    ]
res_city_area()
      
class sale_shop(osv.osv):
    _inherit = "sale.shop"    
    _columns = {
    'code': fields.char('Branch Code', required=True, size=30),
    'partner_id': fields.many2one('res.partner', 'Contact Person'),
    'street': fields.char('Address Line1', size=100),
    'street2': fields.char('Address Line2', size=50),
    'zip': fields.char('Zip Code', size=8),
    'email': fields.char('Email', size=50),
    'phone': fields.char('Phone', size=20),
    'name' : fields.char('Branch Name',required=True, size=30),
    'area_id' : fields.many2one('res.city.area', 'Area', required=True),
    'city_id' : fields.related('area_id','city_id',type='many2one',relation='res.state.city',string='City',readonly=True),
    'state_id' : fields.related('city_id','state_id',type='many2one',relation='res.country.state',string='Region',readonly=True),
    'country_id': fields.related('state_id', 'country_id', type='many2one', relation='res.country', string='Country', readonly=True),
    'journal_ids': fields.many2many('account.journal', 'rel_journal_shop_id', 
    'shop_id', 'journal_id',  'Payment Methods', domain="[('type', 'in', ['bank', 'cash'])]",),
    'analytic_ids': fields.one2many('account.analytic.account', 'area_id', 'Analytic Accounts'),
    'car_ids': fields.one2many('fleet.analytic.account', 'branch_id', 'Car'),
    }   
    
    _defaults = {
     'payment_default_id': 1,
     }
    
    def create(self, cr, uid, values, context=None):
        ana_acc_id = self.pool.get('account.analytic.account').create(cr,uid,{
        'name' : values.get('name',False),
        'entry_type' : 'branch',
        'company_id':values.get('company_id',False),
        'code': False,
        })
        values['project_id'] = ana_acc_id
        
        return super(sale_shop,self).create(cr, uid, values, context=context)

sale_shop()
    
class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
    'analytic_id' : fields.many2one('account.analytic.account','Analytic Account'),
    'car_ids': fields.one2many('fleet.analytic.account', 'company_id', 'Car'),
    }
    
res_company()        