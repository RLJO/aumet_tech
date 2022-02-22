# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockMove(models.Model):
    _inherit = "stock.move"

    inventory_adjustment_cost = fields.Float("Inventory Adjustment Cost")

    def _get_price_unit(self):
        """ Returns the unit price to value this stock move """
        if self.inventory_id:
            return self.inventory_adjustment_cost

        return super(StockMove, self)._get_price_unit()


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    expiration_date = fields.Date('Expiration Date', compute='_lot_expiration_date', inverse='_set_expiration_date')

    @api.model
    def _get_inventory_fields_create(self):
        """ Returns a list of fields user can edit when he want to create a quant in `inventory_mode`.
        """
        fields = super(StockQuant, self)._get_inventory_fields_create()
        fields.append('expiration_date')
        return fields

    @api.depends('lot_id')
    def _lot_expiration_date(self):
        for line in self:
            line.expiration_date = line.lot_id.expiration_date

    @api.depends('expiration_date')
    def _set_expiration_date(self):
        lot_id = self.env['stock.production.lot'].search([
            ('company_id', '=', self.company_id.id),
            ('product_id', '=', self.product_id.id),
            ('expiration_date', '=', self.expiration_date)
        ], limit=1)
        if not lot_id:
            lot_vals_dict = {
                'company_id': self.company_id.id,
                'name': self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                'product_id': self.product_id.id,
                'expiration_date': self.expiration_date if self.expiration_date else False,
            }
            lot_id = self.env['stock.production.lot'].create(lot_vals_dict)
        self.lot_id = lot_id.id
