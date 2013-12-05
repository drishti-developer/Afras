from osv import osv
from osv import fields
import datetime
import time
from datetime import date
from dateutil.relativedelta import relativedelta
from openerp import tools
from openerp.addons.base_status.base_stage import base_stage
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import html2plaintext
class account_analytic_account(osv.osv):
     _name='account.analytic.account'
     _inherit='account.analytic.account'
    
