# -*- coding: utf-8 -*-
from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        super(PurchaseOrder, self).button_confirm()
        for order in self:
            for l in order.order_line:
                if l.product_id.lst_price != l.prod_sale_price and l.prod_sale_price != 0:
                    l.product_id.lst_price = l.prod_sale_price


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    prod_sale_price = fields.Float(
        'Sales Price', digits='Product Price', track_visibility='onchange',
        help="Price at which the product is sold to customers.")
    profit = fields.Float('Profit(%)', compute='_compute_profit')

    def _track_sale_price(self,new_price):
        self.ensure_one()
        if new_price != self.prod_sale_price:
            self.order_id.message_post_with_view(
                'aumet_purchase_order.track_po_line_sale_price_template',
                values={'line': self, 'prod_sale_price': new_price},
                subtype_id=self.env.ref('mail.mt_note').id
            )
    def write(self, values):
        if 'prod_sale_price' in values:
            for line in self:
                line._track_sale_price(values['prod_sale_price'])
        return super(PurchaseOrderLine, self).write(values)

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id:
            self.prod_sale_price = self.product_id.lst_price

    def _compute_profit(self):
        for l in self:
            sp = l.prod_sale_price or l.product_id.lst_price
            if sp:
                l.profit = (sp - l.price_unit) / sp * 100
            else:
                l.profit = 0
