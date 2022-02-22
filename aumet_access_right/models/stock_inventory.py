# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero


# class Inventory(models.Model):
#     _inherit = "stock.inventory"
#
#
#     def action_validate(self):
#         if not self.exists():
#             return
#         self.ensure_one()
#         if not self.user_has_groups('stock.group_stock_manager,aumet_access_right.allow_user_to_validate_inventory_adjustment'):
#             raise UserError(_("Only a stock manager can validate an inventory adjustment."))
#         if self.state != 'confirm':
#             raise UserError(_(
#                 "You can't validate the inventory '%s', maybe this inventory "
#                 "has been already validated or isn't ready.", self.name))
#         inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot', 'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
#         lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
#         if inventory_lines and not lines:
#             wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in inventory_lines.mapped('product_id')]
#             wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
#             return {
#                 'name': _('Tracked Products in Inventory Adjustment'),
#                 'type': 'ir.actions.act_window',
#                 'view_mode': 'form',
#                 'views': [(False, 'form')],
#                 'res_model': 'stock.track.confirmation',
#                 'target': 'new',
#                 'res_id': wiz.id,
#             }
#         self._action_done()
#         self.line_ids._check_company()
#         self._check_company()
#         return True



# class Users(models.Model):
#     _inherit = 'res.users'
#
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         result = super(Users,self).create(vals_list)
#         for res in result:
#             res.write({'in_group_7': False})
#         return result
