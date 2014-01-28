import time
from openerp.report import report_sxw
from common_report_header import common_report_header

class account_fleet_report(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(account_fleet_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update( {
            'get_lines': self.get_lines,
            'time': time,
            'get_fiscalyear': self._get_fiscalyear,
            'get_account': self._get_account,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period,
            'get_filter': self._get_filter,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'get_cost_center': self._get_cost_center,
            'get_entry_type': self._get_entry_type,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_fleet_report, self).set_context(objects, data, new_ids, report_type=report_type)

    def get_lines(self, data):
        lines = []
        account_obj = self.pool.get('account.account')
        analytic_obj = self.pool.get('account.analytic.account')
        vehicle_obj = self.pool.get('fleet.vehicle')
        branch_obj = self.pool.get('sale.shop')
        
        form_value = data['form']
        
        ## Date and Period Conditions
        where = [tuple([0,])]
        date_str = False
        
        filter_by = form_value.get('filter')
        # Date Condition
        if filter_by == 'filter_date':
            date_str = "date>=%s and date<=%s"
            where.append(tuple([form_value.get('date_from')]))
            where.append(tuple([form_value.get('date_to')]))
        
        # Period Condition
        elif filter_by == 'filter_period':
            date_str = "date>=%s and date<=%s"
            period_obj = self.pool.get('account.period')
            date_from,date_to = None,None
            period_ids = []            
            if form_value.get('period_from'):
                period_ids.append(form_value.get('period_from'))
            if form_value.get('period_to'):
                period_ids.append(form_value.get('period_to'))
            if period_ids :
                period_values = period_obj.read(self.cr,self.uid,period_ids,['date_start','date_stop'])
                for period_dict in period_values:
                    if period_dict['id'] == form_value['period_from'] :
                        date_from = period_dict['date_start']
                    elif period_dict['id'] == form_value['period_to'] :
                        date_to = period_dict['date_stop']
            
            if not date_from or not date_to:
                fiscal_dates = self.pool.get('account.fiscalyear').read(self.cr,self.uid,form_value['fiscalyear_id'],['date_start','date_stop'])
                if not date_from:
                    date_from = fiscal_dates['date_start']
                if not date_to:
                    date_to = fiscal_dates['date_stop']
            
            where.append(tuple([date_from]))
            where.append(tuple([date_to]))
        
        ## Entry Conditions
        
        ids2 = self.pool.get('account.financial.report')._get_children_by_order(self.cr, self.uid, [data['form']['account_report_id'][0]], context=data['form']['used_context'])      
        for report in self.pool.get('account.financial.report').browse(self.cr, self.uid, ids2, context=data['form']['used_context']):
            where = [tuple([0,])]
            vals = {
                'name': report.name,
                'balance':  0.0,
                'type': 'report',
                'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
                'account_type': report.type =='sum' and 'view' or False, #used to underline the financial report balances
            }
           
           
            account_ids = []
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if report.type == 'accounts' and report.account_ids:
                account_ids = account_obj._get_children_and_consol(self.cr, self.uid, [x.id for x in report.account_ids])
            elif report.type == 'account_type' and report.account_type_ids:
                account_ids = account_obj.search(self.cr, self.uid, [('user_type','in', [x.id for x in report.account_type_ids])])
            account_str =False
            account_str = 'account_id in %s'
            if not account_ids:
                l =[1]
                where.append(tuple(l))
            else:
                where.append(tuple(account_ids))
            entry_str = False
            entry_list = []
                
            if form_value.get('entry_type',False):
                entry_type = form_value.get('entry_type')
                if entry_type == 'car' and form_value.get('cost_analytic_ids'):
                    entry_str = 'vehicle_id in %s'
                    entry_list = vehicle_obj.search(self.cr, self.uid, [('analytic_id','in',form_value.get('cost_analytic_ids'))])
                    
                    where.append(tuple(entry_list))
                elif entry_type == 'branch' and form_value.get('cost_analytic_ids'):
                    entry_str = 'branch_id in %s'
                    entry_list = branch_obj.search(self.cr, self.uid, [('project_id','in',form_value.get('cost_analytic_ids'))])
                    where.append(tuple(entry_list))
                elif entry_type == 'area' and form_value.get('cost_analytic_ids'):
                    entry_str = 'area_id in %s'
                    for obj in analytic_obj.browse(self.cr, self.uid,form_value.get('cost_analytic_ids')):
                            entry_list.append(obj.area_id.id)
                    where.append(tuple(entry_list))
                elif entry_type == 'city' and form_value.get('cost_analytic_ids'):
                    entry_str = 'city_id in %s'
                    for obj in analytic_obj.browse(self.cr, self.uid,form_value.get('cost_analytic_ids')):
                            entry_list.append(obj.city_id.id)
                    where.append(tuple(entry_list))
                elif entry_type == 'region_id' and form_value.get('cost_analytic_ids'):
                    entry_str = 'region_id in %s'
                    for obj in analytic_obj.browse(self.cr, self.uid,form_value.get('cost_analytic_ids')):
                            entry_list.append(obj.region_id.id)
                    where.append(tuple(entry_list))
                elif entry_type == 'segment' and form_value.get('cost_analytic_ids'):
                    for obj in analytic_obj.browse(self.cr, self.uid,form_value.get('cost_analytic_ids')):
                            entry_list.append(obj.segment) 
                    entry_str = 'segment in %s'     
                    where.append(tuple(entry_list))     
                elif entry_type == 'company' and form_value.get('cost_analytic_ids'):
                    for obj in analytic_obj.browse(self.cr, self.uid,form_value.get('cost_analytic_ids')):
                            entry_list.append(obj.country_id.id)
                    entry_str = 'company_id in %s'
                    where.append(tuple(entry_list))
                    
                                
    #         ## Entry Conditions
    #         entry_str = False    
    #         if form_value.get('entry_type',False):
    #             entry_type = form_value.get('entry_type')
    #             if entry_type == 'car' and form_value.get('car_id'):
    #                 entry_str = 'vehicle_id=%s'
    #                 where.append(tuple([form_value.get('car_id')]))
    #             elif entry_type == 'branch' and form_value.get('branch_id'):
    #                 entry_str = 'branch_id=%s'
    #                 where.append(tuple([form_value.get('branch_id')]))
    #             elif entry_type == 'area' and form_value.get('area_id'):
    #                 entry_str = 'area_id=%s'
    #                 where.append(tuple([form_value.get('area_id')]))
    #             elif entry_type == 'city' and form_value.get('city_id'):
    #                 entry_str = 'city_id=%s'
    #                 where.append(tuple([form_value.get('city_id')]))
    #             elif entry_type == 'region_id' and form_value.get('region_id'):
    #                 entry_str = 'region_id=%s'
    #                 where.append(tuple([form_value.get('region_id')]))
    #             elif entry_type == 'nlco' and form_value.get('country_id'):
    #                 entry_str = 'country_id=%s'
    #                 where.append(tuple([form_value.get('country_id')]))
            
            self.cr.execute(
                    'select account_id,sum(amount)'\
                    'from fleet_vehicle_cost_distribution '\
                    'where amount != %s ' + (date_str and 'and '+date_str+' ' or '') + (account_str and 'and '+account_str+' ' or '') + (entry_str and 'and '+entry_str+' ' or '')  +' '\
                    'group by account_id',tuple(where))
            query_result = self.cr.fetchall()
            
            account_dict = {}
            
            for value in query_result:
                parent_id = False
                check_id = value[1]
                account = account_obj.browse(self.cr, self.uid, value[0])
                parent = account.parent_id
                while parent:
                    inside_dict = account_dict.get(parent.id,{})
                    inside_dict['balance'] = inside_dict.get('balance',0.0) + value[1]<0 and -value[1] or value[1]
                    inside_dict['level'] = parent.level or 0
                    inside_dict['parent_id'] = parent.parent_id and parent.parent_id.id or False
                    inside_dict['name'] = parent.code + ' ' + parent.name
                    inside_dict['type'] = 'account'
                    inside_dict['account_type'] = parent.type,
                    account_dict[parent.id] = inside_dict
                    parent = parent.parent_id
                    
                account_dict[value[0]] = {
                                          'balance':value[1]<0 and -value[1] or value[1],
                                          'level':account.level,
                                          'parent_id':account.parent_id.id,
                                          'name':account.code + ' ' + account.name,
                                          'type':'account',
                                          'account_type':account.type,
                                          }
            
            final_array = []
            account_id_list = []
            level = int(form_value.get('level','7'))
            
            
            def recursive_fnct(check_value):
                indiv_dict = account_dict[check_value]
                parent_id = indiv_dict.get('parent_id')
                if parent_id:
                    recursive_fnct(parent_id)
                current_level = indiv_dict.get('level')
                if check_value not in account_id_list and current_level <= level:
                    final_array.append(account_dict.get(check_value))
                    account_id_list.append(check_value)
                    
                return parent_id
                
            for value in query_result:
                recursive_fnct(value[0])
            for array in final_array:
                if array.get('level')==0:
                    vals['balance'] += array.get('balance')
            lines.append(vals)        
            lines += final_array            
        return lines            
        
report_sxw.report_sxw('report.account.fleet.report', 'fleet.report',
    'addons/drishti_account_report/report/account_fleet_report.rml', parser=account_fleet_report, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
