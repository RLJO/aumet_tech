from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_validate(self):
        res = super(StockInventory, self).action_validate()
        if res:
            for line in self.line_ids:
                if line.prod_lot_id:
                    ref = line.lot_ref
                    if not ref:
                        ref = self.env['ir.sequence'].next_by_code('stock.production.lot.ref.sequence')
                    line.prod_lot_id.update({"ref": ref})


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    lot_ref = fields.Char('Pharmacy Barcode', compute='_compute_lot_ref')

    @api.depends('prod_lot_id')
    def _compute_lot_ref(self):
        for line in self:
            line.lot_ref = line.prod_lot_id.ref

    # @api.depends('lot_ref')
    # def _set_lot_ref(self):
    #     if not self.lot_ref:
    #         ref = self.env['ir.sequence'].next_by_code('stock.production.lot.ref.sequence')
    #     else:
    #         ref = self.lot_ref
    #     lot_id = self.env['stock.production.lot'].search([
    #         ('company_id', '=', self.company_id.id),
    #         ('product_id', '=', self.product_id.id),
    #         ('ref', '=', ref),
    #     ], limit=1)
    #     if not lot_id:
    #         lot_vals_dict = {
    #             'company_id': self.company_id.id,
    #             'name': self.env['ir.sequence'].next_by_code('stock.lot.serial'),
    #             'product_id': self.product_id.id,
    #             'ref': ref,
    #         }
    #         lot_id = self.env['stock.production.lot'].create(lot_vals_dict)
    #     self.prod_lot_id = lot_id.id
