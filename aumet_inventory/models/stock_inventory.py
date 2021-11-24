from odoo import api, fields, models


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    expiration_date = fields.Date('Expiration Date', compute='_lot_expiration_date', inverse='_set_expiration_date')

    @api.depends('prod_lot_id')
    def _lot_expiration_date(self):
        for line in self:
            line.expiration_date = line.prod_lot_id.expiration_date

    @api.depends('expiration_date')
    def _set_expiration_date(self):
        lot_id = self.env['stock.production.lot'].search([
            ('company_id', '=', self.company_id.id),
            ('product_id', '=', self.product_id.id),
            ('expiration_date', '=', self.expiration_date)
        ], limit=1)
        if not lot_id:
            lot_vals_dict = {
                'company_id': self.company_id.id,
                'name': self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                'product_id': self.product_id.id,
                'expiration_date': self.expiration_date if self.expiration_date else False,
            }
            lot_id = self.env['stock.production.lot'].create(lot_vals_dict)
        self.prod_lot_id = lot_id.id
