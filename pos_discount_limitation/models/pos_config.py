# -*- coding: utf-8 -*-

from odoo import api, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    @api.model
    def check_user_limit(self, pos_user, pc):
        user = pos_user.get('user_id')
        pos_discount_limitation_rec = self.env['pos.discount.limitation'].search([('user_id', '=', user[0])])
        disc_limit = pos_discount_limitation_rec.discount_percentage
        if pc > disc_limit:
            return {'disc_limit': disc_limit}
        return True

    @api.model
    def check_discount_per_amount(self, pos_user, discount):
        user = pos_user.get('user_id')
        pos_discount_limitation_rec = self.env['pos.discount.limitation'].search([('user_id', '=', user[0])])
        discount_amount = pos_discount_limitation_rec.discount_amount
        if -(discount) > discount_amount:
            return {'discount_amount': discount_amount}
        return True

    @api.model
    def check_user_limit_amount(self, pos_user, pc):
        user = pos_user.get('user_id')
        pos_discount_limitation_rec = self.env['pos.discount.limitation'].search([('user_id', '=', user[0])])
        disc_amount_limit = pos_discount_limitation_rec.discount_amount
        if pc > disc_amount_limit:
            return {'disc_limit': disc_amount_limit}
        return True
