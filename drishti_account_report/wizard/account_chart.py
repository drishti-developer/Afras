from openerp.osv import fields, osv

class account_chart(osv.osv_memory):
    """
    For Chart of Accounts
    """
    _inherit = "account.chart"
    
    _columns = {
                'cost_analytic_ids' : fields.many2many('account.analytic.account','rel_chart_analytic_id',
                                                'report_id', 'analytic_id',  'Cost Center', ) ,
                 'child_cost_center':fields.boolean('Include Child Cost Center'),  
                }
    _defaults = {
                 'child_cost_center': True,
                 }
    
    def account_chart_open_window(self, cr, uid, ids, context=None):
     
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        period_obj = self.pool.get('account.period')
        fy_obj = self.pool.get('account.fiscalyear')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_account_tree')
        result = act_obj.read(cr, uid, [result and result[1] or False], context=context)[0]
        fiscalyear_id = data.get('fiscalyear', False) and data['fiscalyear'][0] or False
        cost_analytic_ids = data.get('cost_analytic_ids', False) and data['cost_analytic_ids'] or False
        child_cost_center = data.get('child_cost_center', False) and data['cost_analytic_ids'] or False
        
        result['periods'] = []
        if data['period_from'] and data['period_to']:
            period_from = data.get('period_from', False) and data['period_from'][0] or False
            period_to = data.get('period_to', False) and data['period_to'][0] or False
            result['periods'] = period_obj.build_ctx_periods(cr, uid, period_from, period_to)
        result['context'] = str({'fiscalyear': fiscalyear_id, 'periods': result['periods'], \
                                    'state': data['target_move'], 'cost_analytic_ids': cost_analytic_ids,\
                                    'child_cost_center': child_cost_center})
        if fiscalyear_id:
            result['name'] += ':' + fy_obj.read(cr, uid, [fiscalyear_id], context=context)[0]['code']
        return result