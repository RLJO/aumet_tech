# -*- coding: utf-8 -*-

import time
from odoo import api, models
from odoo.tools.misc import formatLang


class ProductVendorReport(models.AbstractModel):
    _name = 'report.aumet_product_vendor_report.shortfall_template'
    _description = 'ShortFall Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': data["data"]}


class PurchaseReport(models.AbstractModel):
    _name = 'report.aumet_product_vendor_report.purchase_vendor_template'
    _description = 'Purchase Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {'doc_ids': data['ids'],
                'doc_model': data['model'],
                'docs': data["data"],
                }


class ProductVendor(models.AbstractModel):
    _name = 'report.aumet_product_vendor_report.vendor_product_template'
    _description = 'Product Vendors Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        prod_ids = data['ids']
        docs = self.env['vendor.product.wizard'].browse(prod_ids)
        return {
            'doc_ids': data['ids'],
            'docs': docs,
            'doc_model': data['model'],
            'data': data,
            'vendors_product': data['data'],
            'time': time,
        }
