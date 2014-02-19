{
    'name': 'Afras Security',
    'version': '1.0',
    'category': 'Account',
    'description': """
        This module have the format of afras Security
 """,
    'author': 'OpenERP SA',
    'website': 'http://www.drishtitech.com',
    'depends': ['base','account','Multicompany_billing','afras_revenue_report','drishti_account_report','crms_oe_connect'],
    'data': [
             'security/company_security1.xml',
              'security/ir.model.access.csv',
            'security/ir.ui.menu.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
