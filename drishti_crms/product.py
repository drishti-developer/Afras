from openerp.osv import fields, osv

class product_product(osv.osv):
    _inherit = "product.product"
    
    # For each model of vehicle  create one product 
    _columns = {
                'car' : fields.boolean('Car'),
                'model_id': fields.many2one('fleet.vehicle.model','Model'),
                'asset_category_id': fields.many2one('account.asset.category','Asset Category'),
                'vehicle_ids': fields.one2many('fleet.vehicle', 'product_id', 'Vehicle'),
                }
    
    # Base on model selection image of model should auto populate
    def on_change_model(self, cr, uid, ids, model_id, context=None):
        if not model_id:
            return {}
        model = self.pool.get('fleet.vehicle.model').browse(cr, uid, model_id, context=context)
        return {
            'value': {
                'image_medium': model.image,
            }
        }
        
    #If Car field is selected then track_incoming and track_outgoing field autoselected 
    def onchange_car(self, cr, uid, ids, car,context=None):
        """
        onchange Car.
        """
        
        if car:
            return {'value': { 'track_incoming': True, 'track_outgoing': True }}
        if not car:
            return {'value': {'track_incoming': False, 'track_outgoing': False}}
        