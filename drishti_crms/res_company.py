from openerp.osv import fields, osv

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
                'revenue_account' : fields.many2one('account.account','Main Revenue Account'),
                'type':fields.selection([('nlco','NALCO')],'Company Name'),
                'cost_center_id':fields.many2one('account.analytic.account','Cost Center'),
                }