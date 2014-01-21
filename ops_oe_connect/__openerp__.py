{
    'name': 'Afras Xml Rpc',
    'version': '1.0',
    'category': 'Xml Rpc',
    'description': """
        This module have the format of afras  Xml Rpc
 """,
    'author': 'OpenERP SA',
    'website': 'http://www.drishtitech.com',
    'depends': ['base','purchase','product','purchase_requisition','project'],
    'data': [
             'xml_rpc_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
