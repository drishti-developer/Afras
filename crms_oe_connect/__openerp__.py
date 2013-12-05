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
    'name': 'CRMS OpenERP Connection',
    'version': '1.0',
    'author': 'Drishti Tech',
    'category': '/',
    'sequence': 22,
    'website': 'http://www.drishtitech.com',
    'summary': '',
    'description': """
         Connect With Car Rental Management System.
         """,
 
    'images': [
               ],
    'depends': ['base', 'product', 'stock', 'drishti_crms'],
    'data': [    
                'crms_instance_view.xml',
                'inherited_object_view.xml'
                 ],
    'demo': [],
    'test': [  
    ],
#     'js': [
#         'static/src/js/calendar.js',
#         'static/src/js/calendar-fa.js',
#         'static/src/js/jalali.js',
#     ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [  ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: