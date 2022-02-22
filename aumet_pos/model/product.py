from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange("available_in_pos", "qty_available")
    def _onchange_available(self):
        template_id = self._origin.id
        product = self.env["product.product"].search([("product_tmpl_id", "=", template_id)])
        if product:
            product_id = product.id
            if self.available_in_pos:
                stock_quant_ids = self.env["stock.quant"].search([("product_id", "=", product_id)])
                stock_move_ids = self.env["stock.move"].search([("product_id", "=", product_id)])
                if stock_quant_ids or stock_move_ids or product.qty_available > 0:
                    product.is_available = True
                else:
                    product.is_available = False


class Product(models.Model):
    _inherit = "product.product"

    is_available = fields.Boolean(default=True)

    @api.model
    def _function_available(self):
        records = self.search([])
        for rec in records:
            if rec.available_in_pos:
                stock_quant_ids = rec.env["stock.quant"].search([("product_id", "=", rec.id)])
                stock_move_ids = rec.env["stock.move"].search([("product_id", "=", rec.id)])
                if stock_quant_ids or stock_move_ids or rec.qty_available > 0:
                    rec.is_available = True
                else:
                    rec.is_available = False
