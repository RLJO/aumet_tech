# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    insurance_company = fields.Many2one('res.partner', string='Insurance Company')
    hi_percentage = fields.Float("HI Percentage")
    member_number = fields.Char("Member Number")
    under_insurance = fields.Boolean("Under Insurance")
    commission = fields.Float("Holder Commission")
    is_insurance = fields.Boolean("Is Insurance Company")

    def _get_total_credit(self):
        self.total_credit = 0
        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self.filtered('id'):
            # price_total is in the company currency
            all_partners_and_children[partner] = self.with_context(active_test=False).search(
                [('id', 'child_of', partner.id)]).ids
            all_partner_ids += all_partners_and_children[partner]

        domain = [
            ('partner_id', 'in', all_partner_ids),
            ('state', 'not in', ['draft', 'cancel']),
            ('payment_state', 'in', ['partial', 'not_paid']),
        ]
        price_totals = self.env['account.move'].read_group(domain, ['amount_residual'], ['partner_id'])
        for partner, child_ids in all_partners_and_children.items():
            partner.total_credit = sum(
                price['amount_residual'] for price in price_totals if price['partner_id'][0] in child_ids)

    total_credit = fields.Float("credit", compute="_get_total_credit",
                                groups='account.group_account_invoice,account.group_account_readonly')

    def action_view_partner_credit(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['domain'] = [('payment_state', 'in', ['partial', "not_paid"]), ('partner_id', 'child_of', self.id)]
        action['context'] = {'default_move_type': 'out_invoice', 'move_type': 'out_invoice', 'journal_type': 'sale'}
        return action

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
            'hi_percentage'] if 'hi_percentage' in partner else partner_rec.hi_percentage or 0.0
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

        if 'insurance_company' in partner:
            partner['insurance_company'] = int(partner['insurance_company'])
        return super(ResPartner, self).create_from_ui(partner)
