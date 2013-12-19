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

import openerp.addons.decimal_precision as dp
import openerp.exceptions
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import datetime

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
    'multi_invoice_id': fields.many2one('account.multi.invoice','Multi Expenses'),
    }
    
account_invoice()

class account_multi_invoice(osv.osv):
    
    def _amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = 0.0
            amount = 0.0
            for line in invoice.invoice_line:
                amount += line.price_subtotal
            res[invoice.id] = amount
        return res

    def _get_journal(self, cr, uid, context=None):
        if context is None:
            context = {}
        type_inv = 'purchase'
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = context.get('company_id', user.company_id.id)
        res = self.pool.get('account.journal').search(cr, uid, [('company_id', '=', company_id),('type', '=', 'purchase')], limit=1)
        return res and res[0] or False

    def _get_currency(self, cr, uid, context=None):
        res = False
        journal_id = self._get_journal(cr, uid, context=context)
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            res = journal.currency and journal.currency.id or journal.company_id.currency_id.id
        return res
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.multi.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()

    _name = "account.multi.invoice"
    #_inherit = ['mail.thread']
    _description = 'Multi-Invoice'
    _order = "id desc"
    
    _columns = {
        'name': fields.char('Description', size=64, select=True, readonly=True, states={'draft':[('readonly',False)]}),
        'origin': fields.char('Source Document', size=64, help="Reference of the document that produced this invoice.", readonly=True, states={'draft':[('readonly',False)]}),
        'internal_number': fields.char('Invoice Number', size=32, readonly=True, help="Unique number of the invoice, computed automatically when the invoice is created."),
        'reference': fields.char('Invoice Reference', size=64, help="The partner reference of this invoice."),
        'comment': fields.text('Additional Information'),
        'state': fields.selection([
            ('draft','Draft'),
            ('invoiced','Invoiced'),
            ('paid','Paid'),
            ],'Status', select=True, readonly=True, track_visibility='onchange',),
        'date_invoice': fields.date('Invoice Date', readonly=True, states={'draft':[('readonly',False)]}, select=True, help="Keep empty to use the current date",required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', change_default=True, readonly=True, required=True, states={'draft':[('readonly',False)]}, track_visibility='always'),
        'account_id': fields.many2one('account.account', 'Account', required=True, readonly=True, states={'draft':[('readonly',False)]}, help="The partner account used for this invoice."),
        'invoice_line': fields.one2many('account.multi.invoice.line', 'invoice_id', 'Invoice Lines', readonly=True, states={'draft':[('readonly',False)]}),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 20),
                'account.multi.invoice.line': (_get_invoice_line, ['price_unit','quantity','invoice_id'], 20),
            },),
        'currency_id': fields.many2one('res.currency', 'Currency', required=True, readonly=True, states={'draft':[('readonly',False)]}, track_visibility='always'),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'company_id': fields.many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly',False)]}),
        'invoice_ids':fields.one2many('account.invoice','multi_invoice_id','Invoices',readonly=True)
    }
    
    _defaults = {
        'state': 'draft',
        'journal_id': _get_journal,
        'currency_id': _get_currency,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
        'internal_number': False,
    }
#     _sql_constraints = [
#         ('number_uniq', 'unique(number, company_id, journal_id, type)', 'Invoice Number must be unique per Company!'),
#     ]

    def confirm_entry(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        vehicle_obj = self.pool.get('fleet.vehicle')
        fleet_ana_obj = self.pool.get('fleet.analytic.account')
        analytic_account_obj = self.pool.get('account.analytic.account')
        account_invoice_obj = self.pool.get('account.invoice')
        wf_service = netsvc.LocalService('workflow')
        
        self_brw = self.browse(cr, uid, ids)[0]
        invoice_date = datetime.datetime.strptime(self_brw.date_invoice,"%Y-%m-%d")        
        
        compy_ana_acc_id = analytic_account_obj.search(cr, uid, [('entry_type','=','company'),('company_id','=',1)])
        result = {}
            
        for line in self_brw.invoice_line:
            inv_ana_acc_id = line.account_analytic_id.id
            
            invoice_line_dict = {
            'name': line.name,
            'origin': line.origin,
            'sequence': line.sequence,
            'uos_id': line.uos_id.id,
            'product_id': line.product_id and line.product_id.id or False,
            'account_id': line.account_id.id,
            'price_unit': line.price_unit,
            'quantity': line.quantity,
            'account_analytic_id':line.account_analytic_id.id,
            }
            
            vehicle_id = vehicle_obj.search(cr, uid, [('analytic_id','=',inv_ana_acc_id)])
            if vehicle_id:
                vehicle_brw = vehicle_obj.browse(cr, uid, vehicle_id[0])
                branch_id = False
                for fleet_ana_acc in vehicle_brw.analytic_account_ids:
                    date_from = datetime.datetime.strptime(fleet_ana_acc.date_from,"%Y-%m-%d")
                    if invoice_date >= date_from:
                        if fleet_ana_acc.segment == 'corporate':
                            branch_id = fleet_ana_acc.client_id.analytic_account_id.id
                        else:
                            branch_id = fleet_ana_acc.branch_id.project_id.id
                            
                        if fleet_ana_acc.date_to:
                            date_to = datetime.datetime.strptime(fleet_ana_acc.date_to,"%Y-%m-%d")
                            if invoice_date <= date_to:
                                continue
                            else:
                                branch_id = False
                
                if branch_id:
                    parent_id = branch_id
                else:
                    parent_id = compy_ana_acc_id[0]
            
            else:
                if line.account_analytic_id.parent_id:
                    parent_id = line.account_analytic_id.parent_id.id
                else:
                    parent_id = line.account_analytic_id.id
                    
            invoice_line_list = result.get(parent_id,[])                    
            invoice_line_list.append((0,0,invoice_line_dict))
            result[parent_id] = invoice_line_list    
        
        for key,value in result.iteritems():
            acc_invoice_id = account_invoice_obj.create(cr, uid, {
            'type':'in_invoice',
            'origin': self_brw.origin,
            'internal_number': self_brw.internal_number,
            'reference': self_brw.reference,
            'comment': self_brw.comment,
            'date_invoice': self_brw.date_invoice,
            'partner_id': self_brw.partner_id.id,
            'account_id': self_brw.account_id.id,
            'invoice_line': value,
            'currency_id': self_brw.currency_id.id,
            'journal_id': self_brw.journal_id.id,
            'company_id':self_brw.company_id.id,
            'cost_analytic_id':key,
            'multi_invoice_id':ids[0]
            })
            wf_service.trg_validate(uid, 'account.invoice', acc_invoice_id, 'invoice_open', cr)
        
        self.write(cr, uid, ids, {'state':'invoiced'})
        return True
    
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoices = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []

        for t in invoices:
            if t['state'] not in ('draft'):
                raise openerp.exceptions.Warning(_('You cannot delete an invoice which is not draft .'))
            else:
                unlink_ids.append(t['id'])

        osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        return True

    def onchange_partner_id(self, cr, uid, ids, partner_id, date_invoice=False, company_id=False):
        acc_id = False

        if partner_id:

            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if p.property_account_payable.company_id and p.property_account_payable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_payable = pay_obj_acc[0]

            
            acc_id = p.property_account_payable.id

        result = {'value': {'account_id': acc_id}}

        return result

    def onchange_journal_id(self, cr, uid, ids, journal_id=False, context=None):
        result = {}
        if journal_id:
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context)
            currency_id = journal.currency and journal.currency.id or journal.company_id.currency_id.id
            company_id = journal.company_id.id
            result = {'value': {'currency_id': currency_id,'company_id': company_id}}
            
        return result

    def onchange_company_id(self, cr, uid, ids, company_id, part_id, invoice_line, currency_id):
        #TODO: add the missing context parameter when forward-porting in trunk so we can remove
        #      this hack!
        context = self.pool['res.users'].context_get(cr, uid)

        val = {}
        dom = {}
        obj_journal = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        inv_line_obj = self.pool.get('account.invoice.line')
        if company_id and part_id:
            acc_id = False
            partner_obj = self.pool.get('res.partner').browse(cr,uid,part_id)
            if partner_obj.property_account_payable:
                if partner_obj.property_account_payable.company_id.id != company_id:
                    property_obj = self.pool.get('ir.property')
                    pay_pro_id = property_obj.search(cr, uid, [('name','=','property_account_payable'),('res_id','=','res.partner,'+str(part_id)+''),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr, uid, [('name','=','property_account_payable'),('company_id','=',company_id)])
                    pay_line_data = property_obj.read(cr, uid, pay_pro_id, ['name','value_reference','res_id'])
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of account, you should create one from Settings\Configuration\Accounting menu.'))
                    
                    val= {'account_id': pay_res_id}
            if ids:
                if company_id:
                    inv_obj = self.browse(cr,uid,ids)
                    for line in inv_obj[0].invoice_line:
                        if line.account_id:
                            if line.account_id.company_id.id != company_id:
                                result_id = account_obj.search(cr, uid, [('name','=',line.account_id.name),('company_id','=',company_id)])
                                if not result_id:
                                    raise osv.except_osv(_('Configuration Error!'),
                                        _('Cannot find a chart of account, you should create one from Settings\Configuration\Accounting menu.'))
                                inv_line_obj.write(cr, uid, [line.id], {'account_id': result_id[-1]})
            else:
                if invoice_line:
                    for inv_line in invoice_line:
                        obj_l = account_obj.browse(cr, uid, inv_line[2]['account_id'])
                        if obj_l.company_id.id != company_id:
                            raise osv.except_osv(_('Configuration Error!'),
                                _('Invoice line account\'s company and invoice\'s company does not match.'))
                        else:
                            continue
        if company_id :
            journal_type = 'purchase'
            type = 'in_invoice'
            journal_ids = obj_journal.search(cr, uid, [('company_id','=',company_id), ('type', '=', journal_type)])
            if journal_ids:
                val['journal_id'] = journal_ids[0]
            ir_values_obj = self.pool.get('ir.values')
            res_journal_default = ir_values_obj.get(cr, uid, 'default', 'type=%s' % (type), ['account.invoice'])
            for r in res_journal_default:
                if r[1] == 'journal_id' and r[2] in journal_ids:
                    val['journal_id'] = r[2]
            if not val.get('journal_id', False):
                journal_type_map = dict(obj_journal._columns['type'].selection)
                journal_type_label = self.pool['ir.translation']._get_source(cr, uid, None, ('code','selection'),
                                                                             context.get('lang'),
                                                                             journal_type_map.get(journal_type))
                raise osv.except_osv(_('Configuration Error!'),
                                     _('Cannot find any account journal of %s type for this company.\n\nYou can create one in the menu: \nConfiguration\Journals\Journals.') % ('"%s"' % journal_type_label))
            dom = {'journal_id':  [('id', 'in', journal_ids)]}

        return {'value': val, 'domain': dom}

account_multi_invoice()

class account_multi_invoice_line(osv.osv):

    def _amount_line(self, cr, uid, ids, prop, unknow_none, unknow_dict):
        res = {}
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        for line in self.browse(cr, uid, ids):
            price = line.price_unit
            taxes = tax_obj.compute_all(cr, uid, [], price, line.quantity, product=line.product_id, partner=line.invoice_id.partner_id)
            res[line.id] = taxes['total']
            if line.invoice_id:
                cur = line.invoice_id.currency_id
                res[line.id] = cur_obj.round(cr, uid, cur, res[line.id])
        return res

    _name = "account.multi.invoice.line"
    _description = "Multi-Invoice Line"
    _columns = {
        'name': fields.text('Description', required=True),
        'origin': fields.char('Source Document', size=256, help="Reference of the document that produced this invoice."),
        'sequence': fields.integer('Sequence', help="Gives the sequence of this line when displaying the invoice."),
        'invoice_id': fields.many2one('account.multi.invoice', 'Invoice Reference', ondelete='cascade', select=True),
        'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null', select=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', select=True),
        'account_id': fields.many2one('account.account', 'Account', required=True, domain=[('type','<>','view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
        'price_subtotal': fields.function(_amount_line, string='Amount', type="float",
            digits_compute= dp.get_precision('Account'), store=True),
        'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure'), required=True),
        'account_analytic_id':  fields.many2one('account.analytic.account', 'Analytic Account',required=True),
    }

    def _default_account_id(self, cr, uid, context=None):
        # XXX this gets the default account for the user's company,
        # it should get the default account for the invoice's company
        # however, the invoice's company does not reach this point
        if context is None:
            context = {}
        
        prop = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category', context=context)
        return prop and prop.id or False

    _defaults = {
        'quantity': 1,
        'price_unit': 0,
        'account_id': _default_account_id,
    }

    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', partner_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id, 'force_company': company_id})
        if not partner_id:
            raise osv.except_osv(_('No Partner Defined!'),_("You must first select a partner!") )
        if not product:
            return {'value': {}, 'domain':{'product_uom':[]}}
        
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        if part.lang:
            context.update({'lang': part.lang})
        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        result.update( {'price_unit': price_unit or res.standard_price} )
        result['name'] = res.partner_ref

        result['uos_id'] = uom_id or res.uom_id.id
        if res.description:
            result['name'] += '\n'+res.description

        domain = {'uos_id':[('category_id','=',res.uom_id.category_id.id)]}

        res_final = {'value':result, 'domain':domain}

        if not company_id or not currency_id:
            return res_final

        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)

        if company.currency_id.id != currency.id:
            res_final['value']['price_unit'] = res.standard_price
            new_price = res_final['value']['price_unit'] * currency.rate
            res_final['value']['price_unit'] = new_price

        if result['uos_id'] and result['uos_id'] != res.uom_id.id:
            selected_uom = self.pool.get('product.uom').browse(cr, uid, result['uos_id'], context=context)
            new_price = self.pool.get('product.uom')._compute_price(cr, uid, res.uom_id.id, res_final['value']['price_unit'], result['uos_id'])
            res_final['value']['price_unit'] = new_price
            
        return res_final

    def uos_id_change(self, cr, uid, ids, product, uom, qty=0, name='', partner_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        context = dict(context)
        context.update({'company_id': company_id})
        warning = {}
        res = self.product_id_change(cr, uid, ids, product, uom, qty, name, partner_id, price_unit, currency_id, context=context)
        if not uom:
            res['value']['price_unit'] = 0.0
        if product and uom:
            prod = self.pool.get('product.product').browse(cr, uid, product, context=context)
            prod_uom = self.pool.get('product.uom').browse(cr, uid, uom, context=context)
            if prod.uom_id.category_id.id != prod_uom.category_id.id:
                warning = {
                    'title': _('Warning!'),
                    'message': _('The selected unit of measure is not compatible with the unit of measure of the product.')
                }
                res['value'].update({'uos_id': prod.uom_id.id})
            return {'value': res['value'], 'warning': warning}
        return res


account_multi_invoice_line()