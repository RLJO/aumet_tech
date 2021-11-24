# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    partial_payment = fields.Boolean(string="Allow Partial Payment", default=True)
