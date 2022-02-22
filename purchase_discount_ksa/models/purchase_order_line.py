from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount_2 = fields.Float(string="Discount2(%)", digits="Discount")

    def _get_discounted_price_unit(self):
        self.ensure_one()
        price_unit = super(PurchaseOrderLine, self)._get_discounted_price_unit()
        if self.discount_2:
            price_discount = self.price_unit * (self.discount_2 / 100)
            return price_unit - price_discount
        return price_unit
