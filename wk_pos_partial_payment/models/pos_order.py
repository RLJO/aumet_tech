# -*- coding: utf-8 -*-

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"

    invoice_remark = fields.Char(string="Invoice Remark")
    form_number = fields.Char(string="Form Number")
    is_partially_paid = fields.Boolean(string="Is Partially Paid")
    wk_order_amount = fields.Float(string="Total")

    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder,self)._order_fields(ui_order)
        fields_return.update({'invoice_remark':ui_order.get('invoice_remark', False)})
        fields_return.update({'form_number':ui_order.get('form_number', False)})
        fields_return.update({'is_partially_paid':ui_order.get('is_partially_paid', False)})
        return fields_return

    @api.model
    def create_from_ui(self, orders, draft=False):
        data = return_data = super(PosOrder, self).create_from_ui(orders,draft)
        if type(data) == dict:
            order_ids = [res.get('id') for res in return_data.get('order_ids')]
        else:
            order_ids = [res.get('id') for res in data]
        order_objs = self.browse(order_ids)
        for order in order_objs:
            if order.account_move:
                order.account_move.partial_payment_remark = order.invoice_remark
                order.account_move.form_number = order.form_number
                if order.is_partially_paid:
                    order.wk_order_amount = order.amount_total
                    order.amount_total = order.amount_paid

        return return_data

    def action_pos_order_paid(self):
        if self.is_partially_paid:
            self.write({'state': 'paid'})
        return super(PosOrder, self).action_pos_order_paid()

    def _prepare_invoice_vals(self):
        vals = super(PosOrder, self)._prepare_invoice_vals()
        partner = self.partner_id.parent_id if self.partner_id.parent_id else self.partner_id
        if self.partner_id and self.partner_id.under_insurance and partner.commission:
            vals['invoice_line_ids'].append((0, None, self._prepare_commission_invoice_line(partner.commission)))
        return vals

    def _prepare_commission_invoice_line(self, commission):
        return {
            'quantity': -1,
            'price_unit': (self.amount_total*commission)/100.0,
            'name': 'Holder Commission',
        }
