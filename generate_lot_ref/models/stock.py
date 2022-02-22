from odoo import models, fields
from random import randint


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_ref = fields.Char(related="lot_id.ref", string="Reference Number")


class Picking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(Picking, self).button_validate()
        if res:
            for move in self.move_lines:
                for line in move.move_line_ids:
                    if line.lot_id:
                        ref = self.env['ir.sequence'].next_by_code('stock.production.lot.ref.sequence')
                        line.lot_id.update({"ref": ref})
                        # update the product multi-barcode table
                        product_id = line.product_id.product_tmpl_id.id
                        self.env["multi.barcodes"].create({"name": ref, "product_id": product_id})
        return res
