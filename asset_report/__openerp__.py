{
    'name': 'Afras Asset Report',
    'version': '1.0',
    'category': 'Account',
    'description': """
        This module have the format of afras asset
 """,
    'author': 'OpenERP SA',
    'website': 'http://www.drishtitech.com',
    'depends': ['base','account','account_asset','drishti_crms'],
    'data': [
             'afras_account_view.xml',
             'wizard/asset_view_wiz.xml',
             'report/asset_report_view.xml',
             
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
