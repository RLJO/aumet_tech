# -*- coding: utf-8 -*-

from odoo import models, fields


class Partner(models.Model):
    _inherit = 'res.partner'

    is_agent = fields.Boolean('Is a Sub Agent', default=False)
