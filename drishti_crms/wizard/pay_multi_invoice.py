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

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
import time

class pay_multi_invoice(osv.osv_memory):
    _name = "pay.multi.invoice"
    _description = "Pay Multi Invoice Wizard"
    
    def _get_currency(self, cr, uid, context=None):
        if context is None: context = {}
        journal_pool = self.pool.get('account.journal')
        journal_id = context.get('journal_id', False)
        if journal_id:
            journal = journal_pool.browse(cr, uid, journal_id, context=context)
            if journal.currency:
                return journal.currency.id
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.currency_id.id
    
    def _get_journal_currency(self, cr, uid, ids, name, args, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = voucher.journal_id.currency and voucher.journal_id.currency.id or voucher.company_id.currency_id.id
        return res
    
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        ctx = dict(context, account_period_prefer_normal=True)
        periods = self.pool.get('account.period').find(cr, uid, context=ctx)
        return periods and periods[0] or False
    
    def _get_company(self, cr, uid, context={}):
        return context.get('company_id',False)
    
    def _get_amount(self, cr, uid, context={}):
        return context.get('amount_total', 0.0)
        
    _columns = {
    'name':fields.char('Memo', size=256, ),
    'date':fields.date('Date', select=True, help="Effective date for accounting entries"),
    'journal_id':fields.many2one('account.journal', 'Journal', required=True),
    'period_id': fields.many2one('account.period', 'Period', required=True),
    'currency_id': fields.function(_get_journal_currency, type='many2one', relation='res.currency', string='Currency', required=True),
    'company_id': fields.many2one('res.company', 'Company', required=True),
    'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True),
    'reference': fields.char('Ref #', size=64, help="Transaction reference number."),
    'analytic_id': fields.many2one('account.analytic.account','Write-Off Analytic Account'),
    }
    
    _defaults = {
    'amount':_get_amount,
    'date': lambda *a: time.strftime('%Y-%m-%d'),
    'company_id': _get_company,
    'period_id': _get_period,
    'currency_id': _get_currency,
    }
    
    def button_create_multi_payment(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_id = context.get('active_id',False)
        
        if active_id:
            
            multi_invoice_pool = self.pool.get('account.multi.invoice')
            voucher_pool = self.pool.get('account.voucher')
            
            wizard  = self.browse(cr,uid,ids[0])
            voucher_ids = []
            multi_invoice = multi_invoice_pool.browse(cr,uid,active_id)
            
            amount_percent = wizard.amount / multi_invoice.residual_amount
            for invoice in multi_invoice.invoice_ids:
                ctx = context.copy()
                amount = invoice.residual * amount_percent
                ctx['default_amount']= invoice.residual 
                ctx['close_after_process']= True 
                ctx['payment_expected_currency']= wizard.currency_id.id 
                ctx['active_model']= 'account.invoice'
                ctx['invoice_id']= invoice.id 
                ctx['journal_type']= 'purchase' 
                ctx['default_type']= 'payment'
                ctx['invoice_type']= 'in_invoice' 
                ctx['search_disable_custom_filters']= True 
                ctx['default_reference']= False
                ctx['default_partner_id']= invoice.partner_id.id 
                ctx['active_ids']=[invoice.id] 
                ctx['type']= 'payment' 
                ctx['active_id']= invoice.id
                ctx['close_after_process']= True
                ctx['invoice_type']= invoice.type
                ctx['payment_expected_currency']= wizard.currency_id.id 
                
                vals = {
                'name':wizard.name,
                'reference':wizard.reference,
                'journal_id':wizard.journal_id.id,
                'company_id':wizard.company_id.id,
                'partner_id':invoice.partner_id.id,
                'amount':amount,
                'date':wizard.date or False,
                'journal_id':wizard.journal_id.id,
                'type':'payment',
                }
                
                partner_ochg = voucher_pool.onchange_partner_id(cr, uid, [], invoice.partner_id.id, wizard.journal_id.id, amount, wizard.currency_id.id, 'payment', wizard.date, ctx)
                if partner_ochg.get('value',False):
                    vals.update(partner_ochg.get('value'))
                date_ochg = voucher_pool.onchange_date(cr, uid, [], wizard.date, wizard.currency_id.id, False, amount, wizard.company_id.id, ctx)
                if date_ochg.get('value',False):
                    vals.update(date_ochg.get('value'))
                voucher_ochg = voucher_pool.onchange_amount(cr, uid, [], amount, 1.0, invoice.partner_id.id, wizard.journal_id.id, wizard.currency_id.id, 'payment', wizard.date, False, wizard.company_id.id, ctx)
                if voucher_ochg.get('value',False):
                    vals.update(voucher_ochg.get('value'))
                journal_ochg = voucher_pool.onchange_journal(cr, uid, [], wizard.journal_id.id, [], False, invoice.partner_id.id, wizard.date, amount, 'payment', wizard.company_id.id, ctx)
                if journal_ochg.get('value',False):
                    vals.update(journal_ochg.get('value'))
                
                if vals.get('line_cr_ids',False):
                    line_cr_ids = []
                    for line in vals.get('line_cr_ids'):
                        line_cr_ids.append((0,0,line))
                    vals['line_cr_ids'] = line_cr_ids
                if vals.get('line_dr_ids',False):
                    line_dr_ids = []
                    for line in vals.get('line_dr_ids'):
                        line_dr_ids.append((0,0,line))
                    vals['line_dr_ids'] = line_dr_ids
                    
                voucher_id = voucher_pool.create(cr, uid, vals, ctx)
                voucher_ids.append(voucher_id)
                voucher_pool.button_proforma_voucher(cr, uid, [voucher_id], ctx)
            
            if multi_invoice.residual_amount <= wizard.amount:
                multi_invoice_pool.write(cr, uid, [active_id], {'state':'paid','residual_amount' : 0})
            else:
                multi_invoice_pool.write(cr, uid, [active_id], {'residual_amount' : multi_invoice.residual_amount - wizard.amount})
        
        return True


pay_multi_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: