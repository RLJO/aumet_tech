# -*- coding: utf-8 -*-


from odoo import models, api


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    @api.model
    def default_get(self, fields_list):
        res = super(StockChangeProductQty, self).default_get(fields_list)
        if self.env.user.property_warehouse_id:
            res['location_id'] = self.env.user.property_warehouse_id.\
                lot_stock_id.id
        return res
