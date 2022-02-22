# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    list_price = fields.Float(
        'Sales Price',
        digits='Product Price',
        help="Price at which the product is sold to customers.")


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    #
    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        for ml in self:
            if ml.product_id.tracking == 'lot':
                if ml.expiration_date:
                    ml.expiration_date = ml.expiration_date.replace(hour=2, minute=0, second=0)
                    lot_id = self.env['stock.production.lot'].search([
                        ('company_id', '=', ml.company_id.id),
                        ('product_id', '=', ml.product_id.id),
                        ('expiration_date', '>=', str(ml.expiration_date.date()) + ' 00:00:00'),
                        ('expiration_date', '<=', str(ml.expiration_date.date()) + ' 23:59:59')], limit=1)
                    if not lot_id:
                        lot_vals_dict = {
                            'company_id': ml.move_id.company_id.id,
                            'name': ml.extend_lot_name,
                            'product_id': ml.product_id.id,
                            'expiration_date': ml.expiration_date,
                        }
                        lot_id = self.env['stock.production.lot'].create([lot_vals_dict])[0]
                    lot_id.write(
                        {
                            'list_price': ml.move_id.purchase_line_id.prod_sale_price if ml.move_id.purchase_line_id else 0}
                    )
                    ml._assign_production_lot(lot_id)

                else:
                    lot_id = self.env['stock.production.lot'].search([
                        ('company_id', '=', ml.company_id.id),
                        ('product_id', '=', ml.product_id.id),
                        ('expiration_date', '=', False)], limit=1)
                    if not lot_id:
                        lot_vals_dict = {
                            'company_id': ml.move_id.company_id.id,
                            'name': ml.extend_lot_name,
                            'product_id': ml.product_id.id,
                        }
                        lot_id = self.env['stock.production.lot'].create([lot_vals_dict])[0]
                    lot_id.write(
                        {
                            'list_price': ml.move_id.purchase_line_id.prod_sale_price if ml.move_id.purchase_line_id else 0}
                    )
                    ml._assign_production_lot(lot_id)


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    @api.depends('expiration_date')
    def _set_expiration_date(self):
        super(InventoryLine, self)._set_expiration_date()
        if self.product_tracking == 'lot':
            lot_id = self.env['stock.production.lot'].search([
                ('company_id', '=', self.company_id.id),
                ('product_id', '=', self.product_id.id),
                ('expiration_date', '>=', str(self.expiration_date) + ' 00:00:00'),
                ('expiration_date', '<=', str(self.expiration_date) + ' 23:59:59')
            ], limit=1)

            lot_id.update({'list_price': self.sale_price if self.sale_price else 0})
            self.prod_lot_id = lot_id.id

    @api.onchange('prod_lot_id')
    def _set_sale_price(self):
        self.sale_price = self.prod_lot_id.list_price
