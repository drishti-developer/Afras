from osv import osv
from osv import fields
import time

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
                'revenue_account' : fields.many2one('account.account','Main Revenue Account')
                }