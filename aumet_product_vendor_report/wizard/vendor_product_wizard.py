from odoo import models, fields


class VendorProductWizard(models.TransientModel):
    _name = "vendor.product.wizard"
    _description = 'Vendors Product Report'

    vendor_id = fields.Many2one('res.partner', 'Vendor')

    def print_report(self):
        data = self.read()[0]
        product_obj = self.env['product.product']
        if self.vendor_id:
            products = product_obj.search([('seller_ids.name', '=', self.vendor_id.id), ('qty_available', '>', 0)])
        else:
            products = product_obj.search([('seller_ids.name', '!=', False), ('qty_available', '>', 0)])

        data = {}
        vendors = {}
        for product in products:
            prod_qty = product.qty_available
            vendor = product.seller_ids[0].name
            vendor_id = vendor.id
            if self.vendor_id.id and vendor_id == self.vendor_id.id:
                if vendor_id not in data:
                    data[vendor_id] = []
                    vendors[vendor_id] = {'name': vendor.name, 'qty': 0}
                data[vendor_id].append({'name': product.name, 'barcode': product.barcode, 'qty': prod_qty})
                vendors[vendor_id]['qty'] += prod_qty
            elif not self.vendor_id.id:
                if vendor_id not in data:
                    data[vendor_id] = []
                    vendors[vendor_id] = {'name': vendor.name, 'qty': 0}

                data[vendor_id].append({'name': product.name, 'barcode': product.barcode, 'qty': prod_qty})
                vendors[vendor_id]['qty'] += prod_qty
        datas = {
            'ids': self.id,
            'model': self._name,
            'data': data,
            'vendors': vendors,
        }
        return self.env.ref('aumet_product_vendor_report.aumet_product_vendors_report_action').report_action(self,
                                                                                                         datas)
