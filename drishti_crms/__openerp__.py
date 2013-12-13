# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'CRMS',
    'version': '1.1',
    'author': 'Drishti Tech',
    'category': 'Fleet Management',
    'sequence': 21,
    'website': 'http://www.drishtitech.com',
    'summary': 'Car Rental Management System',
    'description': """
         Car Rental Management System
         """,
 
    'images': [
               ],
    'depends': [
                'base', 'purchase','stock',
                'fleet','account','account_asset',
                'account_voucher','sale','sale_stock','crm'
                ],
    'data': [    
               'account_asset_view.xml',  
               'account_view.xml',
               'advance_payment_view.xml',
               'analytic_account_view.xml',
               'fleet_view.xml',
               'partner_view.xml',
               'product_view.xml',
               'account_multi_invoice_view.xml',
            ],
    'demo': [],
    'test': [  
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [  ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: