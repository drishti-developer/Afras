{
    'name': ' Invoice',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """
 """,
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'depends': ['base','account','drishti_crms'],
    'data': [
             'acc_financial_report_view.xml',
             'wizard/level_wizard_view.xml',
             'wizard/fleet_report_view.xml',
             'wizard/account_chart_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
