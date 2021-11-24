# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hi_percentage = fields.Float("HI Percentage")
    member_number = fields.Char("Member Number")
    under_insurance = fields.Boolean("Under Insurance")
    commission = fields.Float("Holder Commission")

    @api.depends('prevent_partial_payment','property_payment_term_id')
    def _get_prevent_partial_payment(self):
        for obj in self:
            obj.prevent_partial_payment = obj.property_payment_term_id.prevent_partial_payment

    prevent_partial_payment = fields.Boolean(compute="_get_prevent_partial_payment", string="Don't allow partial payment in POS")

    @api.constrains('hi_percentage')
    def _check_unique_constraint(self):
        if self.hi_percentage < 0 or self.hi_percentage > 100:
            raise ValidationError('HI percentage must be in the range of 0-100%')

    @api.constrains('commission')
    def _check_unique_constraint_commission(self):
        if self.commission < 0 or self.commission > 100:
            raise ValidationError('Holder commission must be in the range of 0-100%')

    @api.model
    def create_from_ui(self, partner):
        partner_rec = self.browse(partner['id'])
        condition_insurance = partner[
            'under_insurance'] if 'under_insurance' in partner else partner_rec.under_insurance
        hi_percentage = partner[
            'hi_percentage'] if 'hi_percentage' in partner else partner_rec.hi_percentage
        member_number = partner[
            'member_number'] if 'member_number' in partner else partner_rec.member_number
        phone = partner[
            'phone'] if 'phone' in partner else partner_rec.phone
        if condition_insurance:
            if not hi_percentage:
                raise UserError("HI % required")
            if not member_number:
                raise UserError("Member ID required")
            if not phone:
                raise UserError("Phone number required")

        if 'parent_id' in partner:
            partner['parent_id'] = int(partner['parent_id'])
        return super(ResPartner, self).create_from_ui(partner)
