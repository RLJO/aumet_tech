# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    discount_amount = fields.Float(string='Total Discount', compute='_compute_discount', digits='Discount')
    bonus_discount_amount = fields.Float(string='Bonus Discount', compute='_compute_discount', digits='Discount')

    @api.depends('partner_id', 'order_line.price_total')
    def _compute_discount(self):
        for order in self:
            discount_amount = sum(line.discount_amount for line in order.order_line)
            if order.partner_id.is_agent:
                order.update({'bonus_discount_amount': discount_amount,
                              'discount_amount': 0})
            else:
                order.update({'discount_amount': discount_amount,
                              'bonus_discount_amount': 0})


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(string="Discount (%)", digits="Discount",
                            compute="_compute_discount", inverse='_inverse_discount', store=True)

    @api.depends("discount_amount")
    def _compute_discount(self):
        for rec in self:
            if rec.discount_amount:
                if rec.price_unit and rec.product_qty:
                    sale_price = rec.price_unit - rec.discount_amount
                    discount = ((rec.price_unit - sale_price) / rec.price_unit) * 100
                    rec.discount = discount / rec.product_qty

    def _inverse_discount(self):
        for rec in self:
            rec.discount = rec.discount

    discount_amount = fields.Float(string="Discount Amount", digits="Discount",
                                   compute="_compute_discount_amount", inverse='_inverse_discount_amount', store=True)

    @api.depends("discount")
    def _compute_discount_amount(self):
        for rec in self:
            if rec.discount:
                if rec.order_id.partner_id.is_agent and rec.discount:
                    subtotal = rec.price_unit / (1 + rec.discount / 100)
                    rec.discount_amount = (rec.price_unit - subtotal) * rec.product_qty
                elif rec.discount:
                    rec.discount_amount = (rec.price_unit * (rec.discount / 100)) * rec.product_qty

    def _inverse_discount_amount(self):
        for rec in self:
            rec.discount_amount = rec.discount_amount

    is_agent = fields.Boolean(related='order_id.partner_id.is_agent')

    _sql_constraints = [('discount_limit', 'check(1=1)', 'No error'), ]

    def _prepare_compute_all_values(self):
        vals = super()._prepare_compute_all_values()
        vals.update({'price_unit': self._get_discounted_price_unit()})
        return vals

    def _get_discounted_bonus_amount(self):
        self.ensure_one()
        discount = 0
        if self.order_id.partner_id.is_agent and self.discount:
            subtotal = self.price_unit / (1 + self.discount / 100)
            discount = (self.price_unit - subtotal) * self.product_qty
        elif self.discount:
            discount = (self.price_unit * (self.discount / 100)) * self.product_qty
        return discount

    def _get_discounted_price_unit_percent(self):
        discount = 0
        if self.price_unit and self.product_qty:
            sale_price = self.price_unit - self.discount_amount
            discount = ((self.price_unit - sale_price) / self.price_unit) * 100
            discount = discount / self.product_qty
        return discount

    def _get_discounted_price_unit(self):
        self.ensure_one()
        if self.discount:
            if self.order_id.partner_id.is_agent:
                return self.price_unit / (1 + self.discount / 100)  # Sub-Agent
            if self.discount <= 100.0:
                return self.price_unit * (1 - self.discount / 100)
            else:
                raise ValidationError("Discount (%) must be lower than 100%.")
        return self.price_unit

    def _get_stock_move_price_unit(self):
        price_unit = False
        price = self._get_discounted_price_unit()
        if price != self.price_unit:
            # Only change value if it's different
            price_unit = self.price_unit
            self.price_unit = price
        price = super()._get_stock_move_price_unit()
        if price_unit:
            self.price_unit = price_unit
        return price

    def _prepare_account_move_line(self, move=False):
        vals = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        vals["discount"] = self.discount
        return vals

    @api.model
    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, supplier, po):
        """Apply the discount to the created purchase order"""
        res = super()._prepare_purchase_order_line(product_id, product_qty, product_uom, company_id, supplier, po)
        res.update({'discount': self.discount})
        return res
