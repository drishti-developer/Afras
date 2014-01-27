import ldap
from ldap.filter import filter_format
from openerp.osv import fields, osv
import logging
_logger = logging.getLogger(__name__)
class CompanyLDAP(osv.osv):
    _inherit = 'res.company.ldap'
    
    _columns ={
                'ladp_user_group' :fields.char('LDAP User Group'),
               }
    
    def map_ldap_attributes(self, cr, uid, conf, login, ldap_entry):
        
        """
        Compose values for a new resource of model res_users,
        based upon the retrieved ldap entry and the LDAP settings.
        
        :param dict conf: LDAP configuration
        :param login: the new user's login
        :param tuple ldap_entry: single LDAP result (dn, attrs)
        :return: parameters for a new resource of model res_users
        :rtype: dict
        """
        
        values = { 'name': ldap_entry[1]['cn'][0],
                   'login': login,
                   'company_id': conf['company']
                   }
        
        
        if conf['user']:
            company_id = self.pool.get('res.users').browse(cr,uid,conf['user']).company_id.id
            values['company_id'] = company_id
        
        
        
        return values
    
    def get_ldap_dicts(self, cr, ids=None):
        """ 
        Retrieve res_company_ldap resources from the database in dictionary
        format.

        :param list ids: Valid ids of model res_company_ldap. If not \
        specified, process all resources (unlike other ORM methods).
        :return: ldap configurations
        :rtype: list of dictionaries
        """

        if ids:
            id_clause = 'AND id IN (%s)'
            args = [tuple(ids)]
        else:
            id_clause = ''
            args = []
        cr.execute("""
            SELECT id, company, ldap_server, ldap_server_port, ldap_binddn,
                   ldap_password, ldap_filter,ladp_user_group, ldap_base, "user", create_user,
                   ldap_tls
            FROM res_company_ldap
            WHERE ldap_server != '' """ + id_clause + """ ORDER BY sequence
        """, args)
        return cr.dictfetchall()
    
    def authenticate(self, conf, login, password):
        """
        Authenticate a user against the specified LDAP server.

        In order to prevent an unintended 'unauthenticated authentication',
        which is an anonymous bind with a valid dn and a blank password,
        check for empty passwords explicitely (:rfc:`4513#section-6.3.1`)
        
        :param dict conf: LDAP configuration
        :param login: username
        :param password: Password for the LDAP user
        :return: LDAP entry of authenticated user or False
        :rtype: dictionary of attributes
        """

        if not password:
            return False

        entry = False
        
        if conf['ladp_user_group']:
            filter = filter_format(conf['ldap_filter'], (login, conf['ladp_user_group']))
        else:
            filter = filter_format(conf['ldap_filter'], (login,))    
            
        try:
            results = self.query(conf, filter)
            if results and len(results) == 1:
                dn = results[0][0]
                conn = self.connect(conf)
                
                conn.simple_bind_s(dn, password)
                conn.unbind()
                entry = results[0]
        except ldap.INVALID_CREDENTIALS:
            return False
        except ldap.LDAPError, e:
            _logger.error('An LDAP exception occurred: %s', e)
        return entry