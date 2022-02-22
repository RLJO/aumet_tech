# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _, SUPERUSER_ID


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    multi_uom_price_id = fields.One2many('product.multi.uom.price', 'product_id', _("UOM price"))

    @tools.ormcache()
    def _get_default_uom_id(self):
        # Deletion forbidden (at least through unlink)
        return self.env.ref('uom.product_uom_unit')

    uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=_get_default_uom_id, required=True, readonly=True,
        help="Default unit of measure used for all stock operations.")
    uom_name = fields.Char(string='Unit of Measure Name', related='uom_id.name', readonly=True)
    uom_po_id = fields.Many2one(
        'uom.uom', 'Purchase Unit of Measure',
        default=_get_default_uom_id, required=True, readonly=True,
        help="Default unit of measure used for purchase orders. It must be in the same category as the default unit of measure.")

