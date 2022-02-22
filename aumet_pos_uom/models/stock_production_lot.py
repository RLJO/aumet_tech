from datetime import datetime

from odoo import models
from odoo.tools import float_is_zero, float_compare

from itertools import groupby


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    def product_lot_and_serial(self, product_id, picking_type):
        picking_type_id = self.env['stock.picking.type'].browse(picking_type)
        domain = [('product_id', '=', product_id)]
        product_expiry_module_id = self.env['ir.module.module'].sudo().search([('name', '=', 'product_expiry')])
        if product_expiry_module_id.state == 'installed':
            domain += ('|', ('expiration_date', '>', datetime.utcnow().date().strftime("%Y-%m-%d")),
                       ('expiration_date', '=', False))
        lot_ids = self.env['stock.production.lot'].search_read(domain)
        for lot_id in lot_ids:
            quant_ids = self.env['stock.quant'].search([('id', 'in', lot_id.get('quant_ids')), (
                'location_id', 'child_of', picking_type_id.default_location_src_id.id), ('on_hand', '=', True)])
            qty = 0.0
            location_names = ','.join(quant_ids.mapped('location_id').mapped('name'))
            for qunat in quant_ids:
                if qunat.quantity >= 0:
                    qty += qunat.quantity

            if qty:
                lot_id.update({
                    'location_product_qty': round(qty, 2),
                    'real_qty': round(qty, 2),
                    'location_names': location_names,
                })
            else:
                lot_id.update({
                    'location_product_qty': 0,
                    'real_qty': 0,
                    'location_names': location_names,
                })

        return list(filter(lambda lot_id: lot_id['location_product_qty'] != 0, lot_ids))

    # def product_lot_and_serial(self, product_id, picking_type):
    #     lot_ids = super(StockProductionLot, self).product_lot_and_serial(product_id, picking_type)
    #     for lot_id in lot_ids:
    #         lot_id['real_qty'] = lot_id['location_product_qty']
    #     return lot_ids


# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     def _create_move_from_pos_order_lines(self, lines):
#         self.ensure_one()
#         lines_by_product = groupby(sorted(lines, key=lambda l: l.product_id.id),
#                                    key=lambda l: (l.product_id.id, l.uom_id.id))
#         for product, lines in lines_by_product:
#             order_lines = self.env['pos.order.line'].concat(*lines)
#             first_line = order_lines[0]
#             current_move = self.env['stock.move'].create(
#                 self._prepare_stock_move_vals(first_line, order_lines)
#             )
#             confirmed_moves = current_move._action_confirm()
#             for move in confirmed_moves:
#                 if first_line.product_id == move.product_id and first_line.product_id.tracking != 'none':
#                     if self.picking_type_id.use_existing_lots or self.picking_type_id.use_create_lots:
#                         for line in order_lines:
#                             sum_of_lots = 0
#                             for lot in line.pack_lot_ids.filtered(lambda l: l.lot_name):
#                                 if line.product_id.tracking == 'serial':
#                                     qty = 1
#                                 else:
#                                     qty = abs(line.qty)
#
#                                 if line.order_id.amount_total >= 0:
#                                     existing_lot = self.env['stock.production.lot'].search([
#                                         ('company_id', '=', self.company_id.id),
#                                         ('product_id', '=', line.product_id.id),
#                                         ('name', '=', lot.lot_name)
#                                     ])
#                                     available_quantity = move._get_available_quantity(move.location_id,
#                                                                                       lot_id=existing_lot)
#                                     move._update_reserved_quantity(qty, available_quantity, move.location_id,
#                                                                    lot_id=existing_lot, strict=False)
#                                     for ml in move.move_line_ids:
#                                         ml.qty_done = ml.product_qty
#                                 else:
#                                     ml_vals = move._prepare_move_line_vals()
#                                     ml_vals.update({'qty_done': qty})
#                                     if self.picking_type_id.use_existing_lots:
#                                         existing_lot = self.env['stock.production.lot'].search([
#                                             ('company_id', '=', self.company_id.id),
#                                             ('product_id', '=', line.product_id.id),
#                                             ('name', '=', lot.lot_name)
#                                         ])
#                                         if not existing_lot and self.picking_type_id.use_create_lots:
#                                             existing_lot = self.env['stock.production.lot'].create({
#                                                 'company_id': self.company_id.id,
#                                                 'product_id': line.product_id.id,
#                                                 'name': lot.lot_name,
#                                             })
#                                         quant = existing_lot.quant_ids.filtered(
#                                             lambda q: q.quantity > 0.0 and q.location_id.parent_path.startswith(
#                                                 move.location_id.parent_path))[-1:]
#                                         ml_vals.update({
#                                             'lot_id': existing_lot.id,
#                                             'location_id': quant.location_id.id or move.location_id.id
#                                         })
#                                     else:
#                                         ml_vals.update({
#                                             'lot_name': lot.lot_name,
#                                         })
#                                     self.env['stock.move.line'].create(ml_vals)
#                                 sum_of_lots += qty
#
#                             if abs(line.qty) != sum_of_lots:
#                                 difference_qty = abs(line.qty) - sum_of_lots
#                                 ml_vals = current_move._prepare_move_line_vals()
#                                 if line.product_id.tracking == 'serial':
#                                     ml_vals.update({'qty_done': 1})
#                                     for i in range(int(difference_qty)):
#                                         self.env['stock.move.line'].create(ml_vals)
#                                 else:
#                                     ml_vals.update({'qty_done': difference_qty})
#                                     self.env['stock.move.line'].create(ml_vals)
#                     else:
#                         move._action_assign()
#                         for move_line in move.move_line_ids:
#                             move_line.qty_done = move_line.product_uom_qty
#                         if float_compare(move.product_uom_qty, move.quantity_done,
#                                          precision_rounding=move.product_uom.rounding) > 0:
#                             remaining_qty = move.product_uom_qty - move.quantity_done
#                             ml_vals = move._prepare_move_line_vals()
#                             ml_vals.update({'qty_done': remaining_qty})
#                             self.env['stock.move.line'].create(ml_vals)
#
#                 else:
#                     move._action_assign()
#                     for move_line in move.move_line_ids:
#                         move_line.qty_done = move_line.product_uom_qty
#                     if float_compare(move.product_uom_qty, move.quantity_done,
#                                      precision_rounding=move.product_uom.rounding) > 0:
#                         remaining_qty = move.product_uom_qty - move.quantity_done
#                         ml_vals = move._prepare_move_line_vals()
#                         ml_vals.update({'qty_done': remaining_qty})
#                         self.env['stock.move.line'].create(ml_vals)
#                     move.quantity_done = move.product_uom_qty
