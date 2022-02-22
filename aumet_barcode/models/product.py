# -*- coding: utf-8 -*-
import datetime

from odoo import models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'barcodes.barcode_events_mixin']

    def on_barcode_scanned(self, barcode):
        self.product_tmpl_id.on_barcode_scanned(barcode)


class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'barcodes.barcode_events_mixin']

    def _get_nomenclature_id(self):
        nomenclature_id = self.env['barcode.nomenclature'].search([('is_gs1_nomenclature', '=', True)], limit=1)
        if nomenclature_id:
            return nomenclature_id
        return self.env['barcode.nomenclature'].search([], limit=1)

    def _get_barcode_result(self, barcode):
        if type(barcode) != list:
            barcode = [barcode]
        for res in barcode:
            rule = res['rule']
            if rule.type == 'product':
                return res['value']
            else:
                continue
        return None

    def _get_multi_barcode_vals(self, product_barcode):
        if self.env['multi.barcodes'].search([('name', '=', product_barcode)]).exists():
            raise UserError('Barcode %s Already exists for another product!' % product_barcode)
        vals = dict(product_id=self.ids[0], name=product_barcode)
        return vals

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        if not self.ids:
            raise UserError('Please save the product before start scanning barcode.')
        nomenclature_id = self._get_nomenclature_id()
        if not nomenclature_id:
            raise UserError("Undefined nomenclature. Please make sure you have at least one nomenclature defined")
        try:
            barcode_result = nomenclature_id.parse_barcode(barcode)
            if not barcode_result:
                raise UserError('Barcode %s can not be parsed!' % barcode)
        except Exception:
            raise UserError('Barcode %s can not be parsed!' % barcode)
        product_barcode = self._get_barcode_result(barcode_result)
        multi_barcode_vals = self._get_multi_barcode_vals(product_barcode)
        self.write({'multi_barcode_ids': [(0, 0, multi_barcode_vals)]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
