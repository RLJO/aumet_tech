# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    prevent_partial_payment = fields.Boolean(string="Don't Allow Partial Payment In POS")