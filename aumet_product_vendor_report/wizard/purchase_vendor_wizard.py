from odoo import models, fields, api
from datetime import datetime


class PurchaseVendorWizard(models.TransientModel):
    _name = "purchase.vendor.wizard"
    _description = 'Purchase Vendor Report'

    vendor_id = fields.Many2one('res.partner', 'Vendor', required=True)
    from_date = fields.Date("From Date", default=datetime.now())
    to_date = fields.Date("To Date", default=datetime.now())

    @api.onchange("to_date")
    def onchange_to_date(self):
        date = datetime.date(datetime.now())
        if self.to_date > date:
            self.to_date = date

    def _filter(self):
        data = []
        purchases = []
        vendor_id = self.vendor_id.id
        vendor_name = self.vendor_id.name
        if self.from_date and self.to_date:
            purchase_order = self.env["purchase.order"].search(
                [("partner_id", "=", vendor_id), ('date_order', '>=', self.from_date),
                 ('date_order', '<=', self.to_date)])
        else:
            purchase_order = self.env["purchase.order"].search([("partner_id", "=", vendor_id)])
        for order in purchase_order:
            product_list = []
            purchase_line = self.env["purchase.order.line"].search([("order_id", "=", order.id)])
            for line in purchase_line:
                product = dict()
                product["name"] = line.product_id.product_tmpl_id.name
                product["available_qty"] = round(line.product_id.qty_available, 3)
                qty = line.product_qty + line.product_bonus_qty
                product["qty"] = round(qty, 3)
                expiration_date = line.expiration_date
                product["expiry"] = ""
                if expiration_date:
                    product["expiry"] = datetime.date(expiration_date)
                if product not in product_list:
                    product_list.append(product)
            date = ""
            if order.date_approve:
                date = datetime.date(order.date_approve)
            purchases.append({"name": order.name, "date": date,
                              "lines": sorted(product_list, key=lambda d: d['name'])})
        data.append({"vendor": vendor_name,"purchase": purchases})
        return data

    def print_report(self):
        data = self._filter()
        datas = {
            'ids': self.id,
            'model': self._name,
            'data': data,
            "from_date": self.from_date, "to_date": self.to_date}
        return self.env.ref('aumet_product_vendor_report.aumet_purchase_vendor_report_action').report_action(
            self, data=datas)
