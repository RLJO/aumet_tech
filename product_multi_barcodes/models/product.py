# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    multi_barcode_ids = fields.One2many(comodel_name='multi.barcodes',
                                        inverse_name='product_id', string='Barcode')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super(ProductTemplate, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if isinstance(result, list):
            multi_barcode_id = self.env['multi.barcodes'].search(
                [('name', '=', name)])
            args = [] if args is None else args
            product_ids = list(self._search(
                [('multi_barcode_ids', 'in', multi_barcode_id.ids)] + args, limit=limit, access_rights_uid=name_get_uid))
            return result+product_ids
        return result


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        result = super(Product, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)
        if isinstance(result, list):
            multi_barcode_id = self.env['multi.barcodes'].search(
                [('name', '=', name)])
            args = [] if args is None else args
            product_ids = list(self._search(
                [('multi_barcode_ids', 'in', multi_barcode_id.ids)] + args, limit=limit, access_rights_uid=name_get_uid))
            return result+product_ids
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
