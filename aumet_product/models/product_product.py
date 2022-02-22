# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.osv import expression

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_multi_barcodes = fields.One2many('multi.barcode.products', 'product_multi', string='Extra Barcode')

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        res.product_multi_barcodes.update({
            'template_multi': res.product_tmpl_id.id
        })
        return res

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        self.product_multi_barcodes.update({
            'template_multi': self.product_tmpl_id.id
        })
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            domain = ['|', '|', ('name', operator, name), ('default_code', operator, name), ('barcode', operator, name)]
            product_id = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
            return self.browse(product_id).name_get().extend(
                self.env['multi.barcode.products'].search('multi_barcode', operator, name))
        return super()._name_search(name, args=None, operator='ilike', limit=100, name_get_uid=None)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_multi_barcodes = fields.One2many('multi.barcode.products', 'template_multi', string='Extra Barcode')

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res.template_multi_barcodes.update({
            'product_multi': res.product_variant_id.id
        })
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if self.template_multi_barcodes:
            self.template_multi_barcodes.update({
                'product_multi': self.product_variant_id.id
            })
        return res


class ProductMultiBarcode(models.Model):
    _name = 'multi.barcode.products'
    _description = "multi barcode for product"
    multi_barcode = fields.Char(string="Barcode", help="Provide alternate barcodes for this product")
    product_multi = fields.Many2one('product.product')
    template_multi = fields.Many2one('product.template')

    def get_barcode_val(self, product):
        # returns barcode of record in self and product id
        return self.multi_barcode, product
