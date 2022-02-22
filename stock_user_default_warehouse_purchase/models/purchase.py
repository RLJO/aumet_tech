# -*- coding: utf-8 -*-


from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _default_pref_picking_type(self):
        default_in_type = self.env.user.property_warehouse_id.in_type_id
        if default_in_type:
            return default_in_type.id
        return self._default_picking_type()

    picking_type_id = fields.Many2one(default=_default_pref_picking_type)
