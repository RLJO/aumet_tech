# -*- coding: utf-8 -*-
import datetime

from odoo import models
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'barcodes.barcode_events_mixin']

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

    def _prepare_inventory_line_values(self, res_dict):
        product_id = res_dict['product_id']
        expiration_date = res_dict.get('expiration_date', False)
        inventory_line = self.line_ids.filtered(
            lambda
                line: line.product_id.id == product_id.id and [
                line.expiration_date if line.expiration_date else False] == [expiration_date])
        if inventory_line:
            return False, inventory_line[0]
        lot_id = self.env['stock.production.lot'].search([
            ('company_id', '=', self.company_id.id),
            ('product_id', '=', product_id.id),
            ('expiration_date', '=', expiration_date)
        ], limit=1)
        sale_price = lot_id.list_price
        if sale_price == 0:
            sale_price = product_id.list_price
        else:
            sale_price = product_id.list_price
        result = {
            'product_id': product_id.id,
            'product_uom_id': product_id.uom_po_id.id,
            'cost': product_id.standard_price,
            'sale_price': sale_price,
            'expiration_date': expiration_date,
        }
        if self.op_location_id:
            result['location_id'] = self.op_location_id
        if lot_id:
            result['prod_lot_id'] = lot_id.id
            result['theoretical_qty'] = product_id.get_theoretical_quantity(
                product_id.id,
                location_id=self.op_location_id.id,
                lot_id=lot_id.id,
            )
            result['product_qty'] = result['theoretical_qty']

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
                result['lot'] = res['value']
        return result

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        if not self.ids:
            raise UserError('Please save the Inventory Adjustment before start scanning products.')
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
        inventory_line_dict, inventory_line = self._prepare_inventory_line_values(result)
        if inventory_line:
            if self.page_type == 'In':
                inventory_line.qty += 1
                inventory_line.product_qty += 1
            elif self.page_type == 'Out':
                inventory_line.qty += 1
                inventory_line.product_qty -= 1
            else:
                inventory_line.product_qty += 1

        else:
            self.write({'line_ids': [(0, 0, inventory_line_dict)]})
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
