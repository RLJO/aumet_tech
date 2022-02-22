# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import float_round

import logging
import pytz

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = "pos.order"
    form_number = fields.Char(string="Form Number")
    customer_paid = fields.Float(string="cash")

    insurance_account_move = fields.Many2one('account.move', string='Insurance Invoice', readonly=True, copy=False)

    @api.model
    def _order_fields(self, ui_order):
        fields_return = super(PosOrder, self)._order_fields(ui_order)
        fields_return.update({'form_number': ui_order.get('form_number', False),
                              "customer_paid": ui_order.get('amount_paid', False)})
        return fields_return

    def action_view_invoice(self):
        res = super(PosOrder, self).action_view_invoice()
        if self.insurance_account_move:
            res['view_id'] = self.env.ref('account.view_out_invoice_tree').id
            res['domain'] = [('id', 'in', self.account_move.ids + self.insurance_account_move.ids)]
            res.pop('res_id')
        return res

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrder, self)._prepare_invoice_line(order_line)
        if self.form_number != '' and self.is_partially_paid:
            # Partial Payment. Reduce insurance part from the line
            res['price_unit'] = res['price_unit'] * (self.partner_id.hi_percentage / 100)
        return res

    def _create_invoice(self, move_vals):
        move_id = super(PosOrder, self)._create_invoice(move_vals)
        if self.form_number != '' and self.is_partially_paid:
            #  Partial Payment detected
            move_id.form_number = self.form_number
            move_id.customer_paid = self.customer_paid
            # Create Insurance Invoice
            move_vals = self._prepare_insurance_invoice_vals(move_id)
            new_move = self._create_insurance_invoice(move_vals)
            move_id.write({'insurance_account_move_id': new_move.id})
            self.write({'insurance_account_move': new_move.id})
            new_move.sudo().with_company(self.company_id)._post()
        return move_id

    def _prepare_commission_invoice_line(self, commission):
        res = {
            'quantity': -1,
            'price_unit': (self.amount_total * commission) / 100.0,
            'name': 'Holder Commission',
        }
        IrDefault = self.env['ir.default'].sudo()
        account_id = IrDefault.get('res.config.settings', "insurance_commission_account_id")
        if account_id:
            res['account_id'] = account_id
        return res

    def _create_insurance_invoice(self, move_vals):
        self.ensure_one()
        new_move = self.env['account.move'].sudo().with_company(self.company_id).with_context(
            default_move_type=move_vals['move_type']).create(move_vals)
        message = _(
            "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                      self.id, self.name)
        new_move.message_post(body=message)
        if self.config_id.cash_rounding:
            rounding_applied = float_round(self.amount_paid - self.amount_total,
                                           precision_rounding=new_move.currency_id.rounding)
            rounding_line = new_move.line_ids.filtered(lambda line: line.is_rounding_line)
            if rounding_line and rounding_line.debit > 0:
                rounding_line_difference = rounding_line.debit + rounding_applied
            elif rounding_line and rounding_line.credit > 0:
                rounding_line_difference = -rounding_line.credit + rounding_applied
            else:
                rounding_line_difference = rounding_applied
            if rounding_applied:
                if rounding_applied > 0.0:
                    account_id = new_move.invoice_cash_rounding_id.loss_account_id.id
                else:
                    account_id = new_move.invoice_cash_rounding_id.profit_account_id.id
                if rounding_line:
                    if rounding_line_difference:
                        rounding_line.with_context(check_move_validity=False).write({
                            'debit': rounding_applied < 0.0 and -rounding_applied or 0.0,
                            'credit': rounding_applied > 0.0 and rounding_applied or 0.0,
                            'account_id': account_id,
                            'price_unit': rounding_applied,
                        })

                else:
                    self.env['account.move.line'].with_context(check_move_validity=False).create({
                        'debit': rounding_applied < 0.0 and -rounding_applied or 0.0,
                        'credit': rounding_applied > 0.0 and rounding_applied or 0.0,
                        'quantity': 1.0,
                        'amount_currency': rounding_applied,
                        'partner_id': new_move.partner_id.id,
                        'move_id': new_move.id,
                        'currency_id': new_move.currency_id if new_move.currency_id != new_move.company_id.currency_id else False,
                        'company_id': new_move.company_id.id,
                        'company_currency_id': new_move.company_id.currency_id.id,
                        'is_rounding_line': True,
                        'sequence': 9999,
                        'name': new_move.invoice_cash_rounding_id.name,
                        'account_id': account_id,
                    })
            else:
                if rounding_line:
                    rounding_line.with_context(check_move_validity=False).unlink()
            if rounding_line_difference:
                existing_terms_line = new_move.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type in ('receivable', 'payable'))
                if existing_terms_line.debit > 0:
                    existing_terms_line_new_val = float_round(
                        existing_terms_line.debit + rounding_line_difference,
                        precision_rounding=new_move.currency_id.rounding)
                else:
                    existing_terms_line_new_val = float_round(
                        -existing_terms_line.credit + rounding_line_difference,
                        precision_rounding=new_move.currency_id.rounding)
                existing_terms_line.write({
                    'debit': existing_terms_line_new_val > 0.0 and existing_terms_line_new_val or 0.0,
                    'credit': existing_terms_line_new_val < 0.0 and -existing_terms_line_new_val or 0.0,
                })

                new_move._recompute_payment_terms_lines()
        return new_move

    def _prepare_insurance_invoice_line(self, order_line):
        return {
            'product_id': order_line.product_id.id,
            'quantity': order_line.qty if self.amount_total >= 0 else -order_line.qty,
            'discount': order_line.discount,
            'price_unit': order_line.price_unit - (order_line.price_unit * (self.partner_id.hi_percentage / 100)),
            'name': order_line.product_id.display_name,
            'tax_ids': [(6, 0, order_line.tax_ids_after_fiscal_position.ids)],
            'product_uom_id': order_line.product_uom_id.id,
        }

    def _prepare_insurance_invoice_vals(self, patient_move_id):
        self.ensure_one()
        timezone = pytz.timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
        note = self.note or ''
        terms = ''
        if self.env['ir.config_parameter'].sudo().get_param(
                'account.use_invoice_terms') and self.env.company.invoice_terms:
            terms = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms

        narration = note + '\n' + terms if note else terms

        vals = {
            'payment_reference': self.name,
            'invoice_origin': self.name,
            'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'move_type': 'out_invoice' if self.amount_total >= 0 else 'out_refund',
            'ref': self.name,
            'partner_id': self.partner_id.insurance_company.id,
            'partner_shipping_id': self.partner_id.id,
            'narration': narration,
            # considering partner's sale pricelist's currency
            'currency_id': self.pricelist_id.currency_id.id,
            'invoice_user_id': self.user_id.id,
            'invoice_date': self.date_order.astimezone(timezone).date(),
            'fiscal_position_id': self.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, self._prepare_insurance_invoice_line(line)) for line in self.lines],
            'invoice_cash_rounding_id': self.config_id.rounding_method.id
            if self.config_id.cash_rounding and (not self.config_id.only_round_cash_method or any(
                p.payment_method_id.is_cash_count for p in self.payment_ids))
            else False,
            'partial_payment_remark': self.invoice_remark,
            'form_number': self.form_number,
            'customer_paid': self.customer_paid,
            'patient_account_move_id': patient_move_id.id,
        }
        vals['invoice_line_ids'].append(
            (0, None, self._prepare_commission_invoice_line(self.partner_id.insurance_company.commission)))
        return vals