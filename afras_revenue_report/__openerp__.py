{
    'name': 'afras_revenue_report',
    'version': '1.0',
    'category': '',
    'description': '',
    'author': 'Drishti Tech',
    'website': 'http://www.drishtitech.com',
    'depends': ['base','account'],
    'data': [
         'security/revenue_report_security.xml', 
         'security/ir.model.access.csv',
         'afras_revenue_report_view.xml',
         'report_sequence.xml',
         ],
    'installable': True,
    'auto_install': False,
    'application': True,


}  
    
