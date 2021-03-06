from openerp.osv import fields, osv
import datetime

_ENTRY_TYPE = [('car', 'Car'), ('branch', 'Branch'),('area', 'Area'), ('city', 'City'),
                ('region', 'Region'), ('segment','Segment'),('company', 'Company'),]

class account_analytic_line(osv.osv):
    _inherit = 'account.analytic.line'
    _description = 'Analytic Line'
    _columns = {
                'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle'),
                'split_entry' : fields.selection([('draft','New'),('progress','Progress'),('done','Done')],'Split Entry'),
                'entry_type': fields.selection(_ENTRY_TYPE, 'Analytic Entry Type',),
                'from_date' : fields.date('From Date'),
                'to_date' : fields.date('To Date'),
                'next_split_date' : fields.date('Next Split Date')                               
                } 
    _defaults = {
                 'split_entry' : 'draft'
                 }
    
    def unlink(self, cr, uid, ids, context=None):
        distribution_obj = self.pool.get('fleet.vehicle.cost.distribution')
        for rec in ids:
            rec_ids = distribution_obj.search(cr, uid, [('analytic_line_id', '=', rec)])
            if rec_ids:
                distribution_obj.unlink(cr, uid, rec_ids, context=context)    
        return super(account_analytic_line, self).unlink(cr, uid, ids, context=context)
    
    def split_analytic_line(self, cr, uid, ids, context=None):
        date = datetime.datetime.today()
        line_obj = self.pool.get('account.analytic.line') 
        fleet_analytic_obj = self.pool.get('fleet.analytic.account')
        branch_obj =  self.pool.get('sale.shop')
        vehicle_obj =  self.pool.get('fleet.vehicle')
        line_id = line_obj.search(cr, uid, [('next_split_date','<=',date),
                                                               ('split_entry','<>','done')])
        analytic_line_objs = line_obj.browse(cr,uid, line_id)
        for alo in analytic_line_objs:
            if not alo.from_date or  not alo.to_date:
                amount = alo.amount        
            if alo.from_date:
                        # find different between two date
                from_date = datetime.datetime.strptime(alo.from_date,"%Y-%m-%d")
                to_date = datetime.datetime.strptime(alo.to_date,"%Y-%m-%d") 
                no_of_days = (to_date - from_date).days +1
                amount = alo.amount/no_of_days 
            try:     
                next_split_date =  datetime.datetime.strptime(alo.next_split_date,"%Y-%m-%d") 
            except:
                next_split_date = datetime.datetime.strptime(alo.next_split_date,"%Y-%m-%d %H:%M:%S")           
            vehicle_id = False
            branch_id = False
            fleet_analytic_ids = False
            if alo.entry_type == 'car':
                vehicle_id =  vehicle_obj.search(cr ,uid,[('analytic_id','=',alo.account_id.id)])
                
                fa_line = []
                if vehicle_id:
                    fa_line = fleet_analytic_obj.search(cr, uid,[('vehicle_id','=',vehicle_id[0])])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line)
                   
            elif alo.entry_type == 'branch':
                branch_id = branch_obj.search(cr,uid,[('project_id','=',alo.account_id.id)]) 
                fa_line = fleet_analytic_obj.search(cr, uid,[('branch_id','in',branch_id)])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line)
            
            elif alo.entry_type =='area':
                fa_line = fleet_analytic_obj.search(cr, uid,[('area_id','=',alo.account_id.area_id.id)])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line)
               
            elif alo.entry_type == 'city':               
                fa_line = fleet_analytic_obj.search(cr, uid,[('city_id','=',alo.account_id.city_id.id)])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line)
            
            elif alo.entry_type == 'region':
                fa_line = fleet_analytic_obj.search(cr, uid,[('region_id','=',alo.account_id.region_id.id)])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line)
            elif alo.entry_type == 'segment':
                fa_line = fleet_analytic_obj.search(cr, uid,[('segment','=',alo.account_id.segment)])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line)     
             
            elif alo.entry_type == 'company' :
                fa_line = fleet_analytic_obj.search(cr, uid,[('company_id','=',alo.account_id.company_id.id)])
                fleet_analytic_ids = fleet_analytic_obj.browse(cr,uid,fa_line) 
            
            while next_split_date <= date:   
                total_value  = 0
                dic = {}
                if fleet_analytic_ids:
                    for analytic_id in fleet_analytic_ids:
                        if datetime.datetime.strptime( analytic_id.date_from,"%Y-%m-%d") <= next_split_date and (not analytic_id.date_to or datetime.datetime.strptime( analytic_id.date_to,"%Y-%m-%d") >= next_split_date ):
                               
                            total_value  += analytic_id.vehicle_id.car_value  
                            dic[analytic_id.vehicle_id.id] = {
                                    'name': alo.name,
                                    'vehicle_id' : analytic_id.vehicle_id.id,
                                    'branch_id': analytic_id.branch_id.id,
                                    'area_id': analytic_id.area_id.id,
                                    'city_id': analytic_id.city_id.id, 
                                    'region_id': analytic_id.region_id.id,
                                    'country_id': analytic_id.country_id.id,
                                    'debit' : 0,
                                    'credit': 0,
                                    'amount': 0,
                                    'date': next_split_date,
                                    'entry_type': alo.entry_type,
                                    'car_value' : analytic_id.vehicle_id.car_value,
                                    'account_id' : alo.general_account_id.id,
                                    'analytic_line_id': alo.id,
                                    'move_id': alo.move_id.id,
                                    
                                }
                           
                           
                if  not fleet_analytic_ids:
                    dic1 = {
                                'name': alo.name,
                                'company_id': alo.account_id.company_id.id,
                                'debit' : (amount >=0) and amount or 0,
                                'credit': (amount < 0) and amount* -1 or 0,
                                'amount': amount,
                                'date': next_split_date,
                                'entry_type': alo.entry_type,
                                'account_id' : alo.general_account_id.id,
                                'analytic_line_id': alo.id,
                                'move_id': alo.move_id.id,
                             }   
                     
                    if alo.entry_type == 'segment':
                        dic1['segment'] =  alo.account_id.segment
                    if alo.entry_type == 'region':
                        dic1['region_id'] =  alo.region_id.id
                        dic1['country_id'] = alo.region_id.country_id.id
                    if alo.entry_type == 'city':
                        dic1['city_id'] =  alo.city_id.id
                        dic1['region_id'] =  alo.city_id.region_id.id
                        dic1['country_id'] = alo.city_id.country_id.id
                            
                    if alo.entry_type == 'area':
                        dic1['area_id'] =  alo.area_id.id
                        dic1['city_id'] =  alo.area_id.city_id.id
                        dic1['region_id'] =  alo.area_id.region_id.id
                        dic1['country_id'] = alo.area_id.country_id.id  
                    if alo.entry_type == 'branch':
                        branch_id = branch_obj.search(cr,uid,[('project_id','=',alo.account_id.id)]) 
                        if branch_id:
                            branch = branch_obj.browse(cr,uid,branch_id[0])
                            dic1['branch_id'] =  branch.id
                            dic1['area_id'] =  branch.area_id.id
                            dic1['city_id'] =  branch.city_id.id
                            dic1['region_id'] =  branch.state_id.id
                            dic1['country_id'] = branch.country_id.id
                    if  alo.entry_type == 'car':
                        vehicle_id =  vehicle_obj.search(cr ,uid,[('analytic_id','=',alo.account_id.id)])
                        dic1['vehicle_id'] =  vehicle_id and vehicle_id[0]   
                    self.pool.get('fleet.vehicle.cost.distribution').create(cr, uid, dic1)               

                for key,v1 in dic.items():
                    
                    dic[key]['amount'] = (dic[key]['car_value'] * amount) / total_value
                    dic[key]['debit'] =   (dic[key]['amount'] >=0) and  dic[key]['amount'] or 0
                    dic[key]['credit'] =   (dic[key]['amount'] < 0) and  dic[key]['amount'] * -1 or 0
                    self.pool.get('fleet.vehicle.cost.distribution').create(cr, uid, dic[key])
                         
                if not alo.from_date or datetime.datetime.strptime(alo.to_date,"%Y-%m-%d")  <= next_split_date:
                    next_split_date += datetime.timedelta(days=1) 
                    break
                next_split_date += datetime.timedelta(days=1) 
                 
            if not alo.to_date or alo.to_date and datetime.datetime.strptime(alo.to_date,"%Y-%m-%d")  <=date :
                split_entry  = 'done'
            else:
                split_entry = 'progress'
                
            line_obj.write(cr,uid, alo.id,{'split_entry' : split_entry,
                                           'next_split_date':next_split_date})       

        return True
    ###################################
    # Need to create a function to split the analytic line to all the car related to that record
    ####################################
    
class account_analytic_account(osv.osv):
    _name = "account.analytic.account"
    _inherit = "account.analytic.account"
    
    def _get_children(self,cr,uid, ids, context=None):
        ids2 = self.search(cr, uid, [('parent_id', 'in', ids)], context=context)
        ids3 = list(set(ids2+ids))
        ids4 = self.search(cr, uid, [('parent_id', 'in', ids3)], context=context)
        while sorted(ids2) <> sorted(ids4):
            ids2 = ids4
            ids3 = list(set(ids2+ids))
            ids4 = self.search(cr, uid, [('parent_id', 'in', ids3)], context=context) 
                         
        return ids4+ids
    
    _columns = {
                'use_distribution_plan': fields.boolean('Use Distribution Plan'),
                'entry_type': fields.selection(_ENTRY_TYPE, 'Cost Center Type',),
                'vehicle_id' : fields.many2one('fleet.vehicle','vehicle'),
                'branch_id': fields.many2one('sale.shop',  'Branch'),
                'area_id': fields.many2one('res.city.area',  'Area'),
                'city_id': fields.many2one('res.state.city',  'City'), 
                'region_id': fields.many2one('res.country.state',  'Region'),
                'segment': fields.selection([('retail','Retail'),('corporate','Corporate')],'Segment'),
                'country_id': fields.many2one('res.country',  'Country'),
                 'journal_ids': fields.many2many('account.journal', 'rel_journal_analytic_id', 
                  'analytic_id', 'journal_id',  'Journal', ), 
                }
    
    _sql_constraints = [
        ('code_uniq',
         'unique (code)',
         'analytic account code must be unique')
    ]
    
    def name_get(self, cr, uid, ids, context=None):

        return super(osv.osv,self).name_get(cr, uid, ids, context=context)
     
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=None):
        limit = 50000
        if not args:
            args=[]
        if context is None:
            context={}
        if name:
            account_ids = self.search(cr, uid, [('code', '=', name)] + args, limit=limit, context=context)
            if not account_ids:
                dom = []
                for name2 in name.split('/'):
                    name = name2.strip()
                    account_ids = self.search(cr, uid, dom + [('name', 'ilike', name)] + args, limit=limit, context=context)
                    if not account_ids: break
                    dom = [('parent_id','in',account_ids)]
        else:
            account_ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, account_ids, context=context)
    
    
