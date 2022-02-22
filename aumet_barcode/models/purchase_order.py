# -*- coding: utf-8 -*-
import datetime

from odoo import models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'barcodes.barcode_events_mixin']

    def _get_nomenclature_id(self):
        nomenclature_id = self.env['barcode.nomenclature'].search([('is_gs1_nomenclature', '=', True)], limit=1)
        if nomenclature_id:
            return nomenclature_id
        return self.env['barcode.nomenclature'].search([], limit=1)

    def _get_product_barcode(self, barcode):
        product_id = self.env['product.product'].search(
            ['|', ('barcode', '=', barcode), ('multi_barcode_ids.name', '=', barcode)], limit=1)
        if not product_id:
            raise UserError('Product Barcode %s Does not exists!' % barcode)
        if not product_id.purchase_ok:
            raise UserError('Please make sure to scan a product that can be purchased')
        return product_id

    def _prepare_purchase_order_line_values(self, res_dict):
        product_id = res_dict['product_id']
        expiration_date = res_dict.get('expiration_date', False)
        pol = self.order_line.filtered(
            lambda
                line: line.product_id.id == product_id.id and [
                line.expiration_date.date() if line.expiration_date else False] == [expiration_date])
        if pol:
            return False, pol[0]
        name = product_id.display_name
        if product_id.description_purchase:
            name += '\n' + product_id.description_purchase
        if expiration_date:
            lot = self.env["stock.production.lot"].search([("expiration_date", "=", expiration_date),
                                                           ("product_id", "=", product_id.id)])
            sale_price = lot.list_price
            if sale_price == 0:
                sale_price = product_id.list_price
        else:
            sale_price = product_id.list_price
        result = {
            'name': name,
            'product_qty': 1,
            'display_type': False,
            'product_id': product_id.id,
            'product_uom': product_id.uom_po_id.id,
            'price_unit': product_id.standard_price,
            'expiration_date': expiration_date,
            'date_planned': self.date_planned if self.date_planned else datetime.datetime.now(),
            'taxes_id': [(6, 0, product_id.supplier_taxes_id.ids)],
            'order_id': self.ids[0],
            'prod_sale_price': sale_price,
        }
        return result, False

    def _get_barcode_result(self, barcode):
        result = dict()
        if type(barcode) != list:
            barcode = [barcode]
        for res in barcode:
            rule = res['rule']
            if rule.type == 'product':
                product_id = self._get_product_barcode(res['value'])
                result['product_id'] = product_id
            elif rule.type == 'expiration_date':
                result['expiration_date'] = res['value']
            elif rule.type == 'lot':
                continue
        return result

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        if not self.ids:
            raise UserError('Please save the purchase order before start scanning products.')
        nomenclature_id = self._get_nomenclature_id()
        if not nomenclature_id:
            raise UserError("Undefined nomenclature. Please make sure you have at least one nomenclature defined")
        try:
            barcode_result = nomenclature_id.parse_barcode(barcode)
            if not barcode_result:
                raise UserError('Barcode %s can not be parsed!' % barcode)
        except Exception:
            raise UserError('Barcode %s can not be parsed!' % barcode)
        result = self._get_barcode_result(barcode_result)
        pol_dict, pol = self._prepare_purchase_order_line_values(result)
        if pol:
            pol.product_qty += 1
        else:
            self.write({'order_line': [(0, 0, pol_dict)]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
