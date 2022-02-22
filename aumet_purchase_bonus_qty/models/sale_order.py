from datetime import datetime, timedelta

from odoo import fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        if res:
            picking_ids = self.picking_ids
            for picking in picking_ids:
                if picking.state != "done":
                    for line in self.order_line:
                        if line.bonus_qty > 0:
                            stock = self.env["stock.move"].search([("picking_id", "=", picking.id),
                                                                   ("product_id", "=", line.product_id.id)])
                            if stock:
                                qty = stock.product_uom_qty + line.bonus_qty
                                stock.update({"product_uom_qty": qty})
                                stock_line = self.env["stock.move.line"].search([("move_id", "=", stock.id),
                                                                                 ("product_id", "=",
                                                                                  line.product_id.id)])
                                if stock_line:
                                    stock_line.update({"product_uom_qty": qty})
        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        move = super(SaleOrder, self)._create_invoices(grouped, final, date)
        if self.order_line:
            invoice_ids = self.invoice_ids
            for invoice in invoice_ids:
                for line in self.order_line:
                    if line.bonus_qty > 0:
                        move_line = self.env["account.move.line"].search([("move_id", "=", invoice.id),
                                                                          ("product_id", "=", line.product_id.id)])
                        if move_line:
                            qty = move_line.quantity - line.bonus_qty
                            move.update({'invoice_line_ids': [(1, move_line.id, {'quantity': qty, }),
                                                              (0, 0, {
                                                                  'display_type': line.display_type,
                                                                  'sequence': line.sequence,
                                                                  'name': line.name,
                                                                  'product_id': line.product_id.id,
                                                                  'product_uom_id': line.product_uom.id,
                                                                  'quantity': line.bonus_qty,
                                                                  'price_unit': 0.0,
                                                                  'tax_ids': [(6, 0, line.tax_id.ids)],
                                                                  'analytic_account_id': line.order_id.analytic_account_id.id,
                                                                  'analytic_tag_ids': [
                                                                      (6, 0, line.analytic_tag_ids.ids)],
                                                                  'sale_line_ids': [(4, line.id)]
                                                              })], })
        return move


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bonus_qty = fields.Float(string='Bonus Qty')
