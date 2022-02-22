from odoo import models, fields

class SaleSummaryReportWizard(models.TransientModel):
    _name = 'product.shortfall.report'

    warehouse_id = fields.Many2one("stock.warehouse", string="Location")

    def get_report(self):
        data = {
            'model': self._name,
            'ids': self.ids,
            "locations": []
        }
        products = []
        if self.warehouse_id:
            quants = self.env["stock.quant"].search([("location_id", "=", self.warehouse_id.lot_stock_id.id)])
            for quant in quants:
                vendor = self.env["product.supplierinfo"].search(
                    [("product_tmpl_id", "=", quant.product_id.product_tmpl_id.id), ("sequence", "=", 1)])
                products.append(
                    {"product": quant.product_id.product_tmpl_id.name, "qty": quant.quantity,
                     "reserved": quant.reserved_quantity,
                     "available": quant.available_quantity, "sale_qty": quant.product_id.sales_count,
                     "agent": vendor.name.name, "forecast": quant.product_id.virtual_available})
            data["locations"].append({self.warehouse_id.name: {"products": products}})
        else:
            warehouse_ids = self.env["stock.warehouse"].search([])
            for warehouse_id in warehouse_ids:
                quants = self.env["stock.quant"].search([("location_id", "=", warehouse_id.lot_stock_id.id)])
                for quant in quants:
                    vendor = self.env["product.supplierinfo"].search(
                        [("product_tmpl_id", "=", quant.product_id.product_tmpl_id.id), ("sequence", "=", 1)])
                    products.append(
                        {"product": quant.product_id.product_tmpl_id.name, "qty": quant.quantity,
                         "reserved": quant.reserved_quantity,
                         "available": quant.available_quantity, "sale_qty": quant.product_id.sales_count,
                         "agent": vendor.name.name, "forecast": quant.product_id.virtual_available})
                data["locations"].append({warehouse_id.name: {"products": products}})
        return self.env.ref('aumet_inventory.product_shortfall_report').with_context(landscape=True).report_action(self,
                                                                                                                   data=data)
