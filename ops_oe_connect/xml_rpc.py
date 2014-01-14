from openerp.osv import fields, osv
#import xmlrpclib








class product_uom(osv.osv):
    _inherit = 'product.uom'
    _columns={
              'entity_code':fields.integer('Entity Code')
       }
    def CreateRecord(self, cr, uid, data, context=None):
        print"========product_uom=========",data
        self.pool.get('product.uom').create(cr,uid,data)
        return True
product_uom()    


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    _columns={
       }
    def CreateRecord(self, cr, uid, data, context=None):
        print"==========purchase_order============>>",data
        self.pool.get('purchase.order').create(cr,uid,data)
        return True
purchase_order()    


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns={
              'sector_code':fields.char('Sector Size',size=4)
       }
res_company()






