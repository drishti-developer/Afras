from functools import partial
import logging
from lxml import etree
from lxml.builder import E

import openerp
from openerp import SUPERUSER_ID
from openerp import pooler, tools
import openerp.exceptions
from openerp.osv import fields,osv
from openerp.osv.orm import browse_record
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
    _description = 'Partner'
    _name = "res.partner"
    _inherit='res.partner'
    def write(self, cr, uid, ids, vals, context=None):
         if isinstance(ids, (int, long)):
             ids = [ids]
         #res.partner must only allow to set the company_id of a partner if it
         #is the same as the company of all users that inherit from this partner
         #(this is to allow the code from res_users to write to the partner!) or
         #if setting the company_id to False (this is compatible with any user company)
         if vals.get('company_id'):
            user_pool = self.pool.get('res.users')
            for partner in self.browse(cr, uid, ids, context=context):
                user_companies = set([users.company_id.id for users in partner.user_ids])
                if len(user_companies) > 1 or vals.get('company_id') not in user_companies:
                    raise osv.except_osv(_("Warning"),_("You can not change the company as the partner/user has mutiple user linked with different companies."))
         result = super(res_partner,self).write(cr, uid, ids, vals, context=context)
         for partner in self.browse(cr, uid, ids, context=context):
             self._fields_sync(cr, uid, partner, vals, context)
         return result
res_partner()
     
     
class res_users(osv.osv):
    _name = "res.users"
    _description = 'Users'
    _inherit='res.users'
     
    def create(self, cr, uid, vals, context=None):
        user_id = super(res_users, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        if user.partner_id.company_id: 
            user.partner_id.write({'company_id': user.company_id.id})
        return user_id


    def write(self, cr, uid, ids, values, context=None):
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        if ids == [uid]:
            for key in values.keys():
                if not (key in self.SELF_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    if not (values['company_id'] in self.read(cr, SUPERUSER_ID, uid, ['company_ids'], context=context)['company_ids']):
                        del values['company_id']
                uid = 1 
                # safe fields only, so we write as super-user to bypass access rights

        res = super(res_users, self).write(cr, uid, ids, values, context=context)
        
        if 'company_id' in values:
            for user in self.browse(cr, uid, ids, context=context):
                # if partner is global we keep it that way
                if user.partner_id.company_id and user.partner_id.company_id.id != values.get('company_id'): 
                    user.partner_id.write({'company_id': user.company_id.id})
        
#         if 'company_id' in values:
#             for user in self.browse(cr, uid, ids, context=context):
#                 # if partner is global we keep it that way
#                 if user.partner_id.company_id and user.partner_id.company_id.id != values['company_id']: 
#                     user.partner_id.write({'company_id': user.company_id.id})
                    
                    
        # clear caches linked to the users
        self.pool.get('ir.model.access').call_cache_clearing_methods(cr)
        clear = partial(self.pool.get('ir.rule').clear_cache, cr)
        map(clear, ids)
        db = cr.dbname
        if db in self._uid_cache:
            for id in ids:
                if id in self._uid_cache[db]:
                    del self._uid_cache[db][id]
        self.context_get.clear_cache(self)
        return res
    
res_users()