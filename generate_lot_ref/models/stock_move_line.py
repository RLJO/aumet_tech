from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    lot_ref = fields.Char(string="Pharmacy Barcode")
