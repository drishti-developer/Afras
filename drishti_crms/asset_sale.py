from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import datetime
from openerp.tools.translate import _
class account_asset_asset(osv.osv):
    _inherit='account.asset.asset'
    _columns={
              'sold_value':fields.char('Sold Value'),
              }
    
    
    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','code'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = name + record['code']
            res.append((record['id'], name))
        return res
    
class asset_sale(osv.osv):
    _name='asset.sale'
    _columns={
              'asset_id':fields.many2one('account.asset.asset','Asset',required=True),
              'category_id':fields.many2one('account.asset.category','Category'),
              'partner_id':fields.many2one('res.partner','Customer'),
              'company_id':fields.many2one('res.company','Company'),
              'vehicle_id':fields.related('asset_id', 'vehicle_id', type='many2one', relation='fleet.vehicle', string='Vehicle', store=True,  readonly=True),
              'date':fields.date('Purchase Date',),
              'state':fields.selection([('draft','Draft'),('ready','Sale Request'),('sold','Sold'),('cancel','Cancel')],'Status'),
              'amount':fields.float('Price'),
              'property_asset_sale_journal': fields.property('account.journal', type='many2one', relation='account.journal', string="Asset Journal", view_load=True, help="Cash Journal",),
              'asset_invoice_ids':fields.one2many('account.invoice','asset_sale_id','Invoice'),
              'request_by':fields.many2one('res.users','Requested By',readonly=True),
              'approve_by':fields.many2one('res.users','Approve By',readonly=True),
              
              }
    _defaults={
               'state':'draft',
               }
    def onchange_asset(self,cr,uid,ids,asset_id,context=None):
        if asset_id:
            obj=self.pool.get('account.asset.asset').browse(cr,uid,asset_id)
            res={
                 'date':obj.purchase_date,
                 'category_id':obj.category_id.id if obj.category_id else False,
                 'company_id':obj.company_id.id,
                 }
        
        return {'value':res}
    def confirm(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'ready','request_by':uid})
    
    def sell_asset(self,cr,uid,ids,context=None):
        obj=self.browse(cr,uid,ids[0])
        if obj.amount == 0.0:
            raise osv.except_osv(_('Warning !!'),_('Please Enter Valid Amount'))
        invoice_pool=self.pool.get('account.invoice')
        cost_analytic_id=obj.asset_id.cost_analytic_id.id if obj.asset_id.cost_analytic_id else obj.asset_id.analytic_id.id or False
        invoice_dic={
                     'asset_sale_id':obj.id,
                     'partner_id':obj.partner_id.id,
                     'cost_analytic_id':cost_analytic_id,
                     'date_invoice':datetime.date.today(),
                     'reference_type':'none',
                     'type':'out_invoice',
                     'journal_id':obj.property_asset_sale_journal.id,
                     'account_id':obj.partner_id.property_account_receivable.id
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
        self.pool.get('account.asset.asset').write(cr,uid,obj.asset_id.id,{'sold_value':obj.amount})
        return self.write(cr,uid,ids,{'state':'sold','approve_by':uid})
    def cancel(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids,{'state':'cancel'})

asset_sale()

class account_invoice(osv.osv):
    _inherit='account.invoice'
    _columns={
              'asset_sale_id':fields.many2one('asset.sale','Asset')
              }