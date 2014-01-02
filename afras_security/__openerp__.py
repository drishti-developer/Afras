{
    'name': 'Afras Security',
    'version': '1.0',
    'category': 'Account',
    'description': """
        This module have the format of afras Security
 """,
    'author': 'OpenERP SA',
    'website': 'http://www.drishtitech.com',
    'depends': ['base','Multicompany_billing','drishti_account_report','crms_oe_connect','import_afras_data','asset_report','afras_fleet','import_afras_data'],
    'data': [
             'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
