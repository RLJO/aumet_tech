# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import  models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.depends('company_id', 'location_id', 'owner_id', 'product_id', 'quantity')
    def _compute_value(self):
        super(StockQuant, self)._compute_value()
        for quant in self:
            domain = quant.action_view_stock_moves()['domain']
            org_sml = self.env['stock.move.line'].search(domain, order='id', limit=1)
            if org_sml:
                if org_sml.move_id.product_bonus_qty:
                    quant.value = 0.0
