# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
    product_bonus_qty = fields.Float('Bonus Quantity', default=0, help='Quantity in the default UoM of the product')

    def _get_price_unit(self):
        """ Returns the unit price to value this stock move """
        if self.product_bonus_qty > 0:
            return 0
        return super(StockMove, self)._get_price_unit()