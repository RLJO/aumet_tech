# -*- coding: utf-8 -*-

from odoo import fields, models


class PosDiscount(models.Model):
    _name = 'pos.discount.limitation'
    _rec_name = 'user_id'

    def filter_user(self):
        result = []
        group = self.env["res.groups"].search([("name", "=", "Settings")])
        if group:
            self._cr.execute(f"""select uid from res_groups_users_rel 
                                where gid={group.id}""")
            group_rel = self._cr.fetchall()
            for rel in group_rel:
                result.append(rel[0])
        return [("id", "not in", result)]

    user_id = fields.Many2one('res.users', domain=lambda self: self.filter_user())
    discount_percentage = fields.Float("Discount(%)")
    discount_amount = fields.Float("Discount Amount")
