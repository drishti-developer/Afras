from openerp.osv import fields, osv
from openerp.tools.translate import _


class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    
    _columns = {
                'vehicle_id' : fields.many2one('fleet.vehicle','Product'),
                }
    
    
    def create(self, cr, uid, values, context=None):
        
        if 'product_id' in values:
            product_obj = self.pool.get('product.product').browse(cr,uid,values['product_id'])
            if product_obj.car:
                ids = self.search(cr,uid, [('name','=',values['name'])])
                if ids:
                    raise osv.except_osv(_('Duplicate Car Number!'),_("You Must have to define unique car serial number!") )
                dic = {
                       'license_plate': values['name'],
                       'model_id':product_obj.model_id.id,
                       'product_id': values['product_id'],
                       }
                vehicle_id = self.pool.get('fleet.vehicle').create(cr,uid,dic)
                values['vehicle_id'] = vehicle_id
        return super(stock_production_lot,self).create(cr, uid, values, context=context)
    
    
class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id,
        invoice_vals, context=None):
        """ Builds the dict containing the values for the invoice line
            @param group: True or False
            @param picking: picking object
            @param: move_line: move_line object
            @param: invoice_id: ID of the related invoice
            @param: invoice_vals: dict used to created the invoice
            @return: dict that will be used to create the invoice line
        """
        if group:
            name = (picking.name or '') + '-' + move_line.name
        else:
            name = move_line.name
        origin = move_line.picking_id.name or ''
        if move_line.picking_id.origin:
            origin += ':' + move_line.picking_id.origin

        if invoice_vals['type'] in ('out_invoice', 'out_refund'):
            account_id = move_line.product_id.property_account_income.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_income_categ.id
        else:
            account_id = move_line.product_id.property_account_expense.id
            if not account_id:
                account_id = move_line.product_id.categ_id.\
                        property_account_expense_categ.id
        if invoice_vals['fiscal_position']:
            fp_obj = self.pool.get('account.fiscal.position')
            fiscal_position = fp_obj.browse(cr, uid, invoice_vals['fiscal_position'], context=context)
            account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)
        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move_line.product_uos and move_line.product_uos.id or False
        if not uos_id and invoice_vals['type'] in ('out_invoice', 'out_refund'):
            uos_id = move_line.product_uom.id
        invoice_dict = {
            'name': name,
            'origin': origin,
            'invoice_id': invoice_id,
            'uos_id': uos_id,
            'product_id': move_line.product_id.id,
            'account_id': account_id,
            'price_unit': self._get_price_unit_invoice(cr, uid, move_line, invoice_vals['type']),
            'discount': self._get_discount_invoice(cr, uid, move_line),
            'quantity': move_line.product_uos_qty or move_line.product_qty,
            'invoice_line_tax_id': [(6, 0, self._get_taxes_invoice(cr, uid, move_line, invoice_vals['type']))],
            'account_analytic_id': self._get_account_analytic_invoice(cr, uid, picking, move_line),
        } 
        if move_line.product_id.car:
            invoice_dict['asset_category_id'] = move_line.product_id.asset_category_id and move_line.product_id.asset_category_id.id or False
            invoice_dict['vehicle_id'] = move_line.prodlot_id and move_line.prodlot_id.vehicle_id and move_line.prodlot_id.vehicle_id.id or False
            if move_line.prodlot_id.vehicle_id:
                self.pool.get('fleet.vehicle').write(cr,uid,[move_line.prodlot_id.vehicle_id.id],{'car_value' : invoice_dict['price_unit']})
        return invoice_dict   