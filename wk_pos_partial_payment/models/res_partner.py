# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'


    @api.depends('prevent_partial_payment','property_payment_term_id')
    def _get_prevent_partial_payment(self):
        for obj in self:
            obj.prevent_partial_payment = obj.property_payment_term_id.prevent_partial_payment

    prevent_partial_payment = fields.Boolean(compute="_get_prevent_partial_payment", string="Don't allow partial payment in POS")
