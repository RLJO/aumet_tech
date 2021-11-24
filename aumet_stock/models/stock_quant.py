# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.constrains("product_id", "quantity")
    def check_negative_qty(self):
        p = self.env["decimal.precision"].precision_get("Product Unit of Measure")

        for quant in self:
            disallowed_by_product = (not quant.product_id.allow_negative_stock)
            if (
                    float_compare(quant.quantity, 0, precision_digits=p) == -1
                    and quant.product_id.type == "product"
                    and quant.location_id.usage in ["internal", "transit"]
                    and disallowed_by_product
            ):
                msg_add = ""
                if quant.lot_id:
                    msg_add = _(" lot '%s'") % quant.lot_id.name_get()[0][1]
                raise UserError(
                    _(
                        "You cannot validate this stock operation because the "
                        "stock level of the product '%s'%s would become negative "
                        "(%s) and negative stock is "
                        "not allowed for this product."
                    )
                    % (
                        quant.product_id.name,
                        msg_add,
                        quant.quantity,
                    )
                )
