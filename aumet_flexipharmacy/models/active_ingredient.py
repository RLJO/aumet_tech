# -*- coding: utf-8 -*-

from odoo import fields, models


class ActiveIngredient(models.Model):
    _inherit = 'active.ingredient'
    atc_code = fields.Char('ATC  code',required=True)
    _sql_constraints = [('active_ingredient_atc_code_unique', 'unique(atc_code)', 'ATC Code already defined')]
