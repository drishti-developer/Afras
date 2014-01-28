from openerp.osv import fields, osv
from datetime import datetime,timedelta
from openerp.tools import  DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
import datetime
class asset_sale(osv.osv):
    _name='asset.sale'
    _columns={
              'asset_id':fields.many2one('account.asset.asset','Asset Name'),
              'partner_id':fields.many2one('res.partner','Customer'),
              'vehicle_id':fields.related('asset_id', 'vehicle_id', type='many2one', relation='fleet.vehicle', string='Vehicle', store=True,  readonly=True),
              'date':fields.date('Date'),
              'state':fields.selection([('draft','Draft'),('ready','Ready to Sell'),('sold','Sold'),('cancel','Cancel')],'Status'),
              'amount':fields.float('Price'),
              'property_asset_sale_journal': fields.property('account.journal', type='many2one', relation='account.journal', string="Asset Journal", view_load=True, help="Cash Journal",),
              }
    _defaults={
               'state':'draft',
               }
    def onchange_asset(self,cr,uid,ids,asset_id,context=None):
        if asset_id:
            res={
                 'date':self.pool.get('account.asset.asset').browse(cr,uid,asset_id).purchase_date,
                 }
        
        return {'value':res}
    def confirm(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'ready'})
    
    def sell_asset(self,cr,uid,ids,context=None):
        obj=self.browse(cr,uid,ids[0])
        invoice_pool=self.pool.get('account.invoice')
        cost_analytic_id=obj.asset_id.cost_analytic_id.id if obj.asset_id.cost_analytic_id else obj.asset_id.analytic_id.id or False
        invoice_dic={
                     'partner_id':obj.partner_id.id,
                     'cost_analytic_id':cost_analytic_id,
                     'date_invoice':datetime.date.today(),
                     'journal_id':obj.property_asset_sale_journal.id,
                     'account_id':obj.asset_id.category_id.account_asset_id.id
                     }
        invoice_id=invoice_pool.create(cr,uid,invoice_dic,context)
        account_analytic_id=obj.vehicle_id.analytic_id.id if obj.vehicle_id else obj.asset_id.cost_analytic_id.id or False
        invoice_line={
                      'invoice_id':invoice_id,
                      'name':obj.asset_id.name,
                      'price_unit':obj.amount,
                      'account_analytic_id':account_analytic_id,
                      'quantity':1,
                      'account_id':obj.asset_id.category_id.account_asset_id.id
                      }
        self.pool.get('account.invoice.line').create(cr,uid,invoice_line,context)
        self.pool.get('account.asset.asset').set_to_close(cr,uid,obj.asset_id.id,context)
        
        return self.write(cr,uid,ids,{'state':'sold'})
    def cancel(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'cancel'})