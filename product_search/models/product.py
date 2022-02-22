# -*- coding: utf-8 -*-

from odoo import api, fields, models

import json


class ProductTemplate(models.Model):
    _inherit = "product.template"
    supplier_data_json = fields.Char(
        "Supplier data dict", readonly=True,
        compute="_compute_supplier_data_json")

    # @api.multi
    def _compute_supplier_data_json(self):
        for t in self:
            res = []
            for s in t.seller_ids:
                res.append({
                    'supplier_name': s.name.display_name,
                })
            t.supplier_data_json = json.dumps(res)
