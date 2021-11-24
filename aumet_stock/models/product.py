# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    allow_negative_stock = fields.Boolean(
        string="Allow Negative Stock",
        help="If this option is not active on this product "
             "and this product is a stockable product, "
             "then the validation of the related stock moves will be blocked if "
             "the stock level becomes negative with the stock move.",
    )
