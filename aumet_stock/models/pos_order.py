# -*- coding: utf-8 -*-

from itertools import groupby
from odoo import api, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def check_negative(self, order):
        res = []
        for product_id, product_line_ids in groupby(order['lines'], key=lambda line: line[2]['product_id']):
            product = self.env['product.product'].browse(product_id)
            if product.type in ['consu', 'service']:
                continue

            if product.tracking == 'none':
                negative = self._check_tracking_none_negative(product, product_line_ids)
                res.append({'product_id': product_id, 'product_name': product.name, 'negative': negative})
            elif product.tracking == 'lot':
                negative = self._check_tracking_lot_negative(product, product_line_ids)
                res.append({'product_id': product_id, 'product_name': product.name, 'negative': negative})
        return res

    def _check_tracking_none_negative(self, product, product_line_ids):
        product_line_ids = list(product_line_ids)
        uom_id = product_line_ids[0][2]['uom_id'][0]
        uom = self.env['uom.uom'].browse(uom_id)
        if uom.id != product.uom_id.id:
            qty = sum(
                uom._compute_quantity(l[2]['qty'], product.uom_id, raise_if_failure=False) for l in product_line_ids)
        else:
            qty = sum(l[2]['qty'] for l in product_line_ids)
        negative = qty > product.qty_available
        return negative

    def _check_tracking_lot_negative(self, product, product_line_ids):
        negative = False
        for lot_name, product_lot_line_ids in groupby(product_line_ids,
                                                      key=lambda line: line[2]['pack_lot_ids'][0][2]['lot_name']):
            product_lot_line_ids = list(product_lot_line_ids)
            lot = self.env['stock.production.lot'].search([('name', '=', lot_name)])
            uom_id = product_lot_line_ids[0][2]['uom_id'][0]
            uom = self.env['uom.uom'].browse(uom_id)
            if uom.id != product.uom_id.id:
                qty = sum(
                    uom._compute_quantity(l[2]['qty'], product.uom_id, raise_if_failure=False) for l in
                    product_lot_line_ids)
            else:
                qty = sum(l[2]['qty'] for l in product_lot_line_ids)
            negative = qty > lot.remaining_qty
        return negative
