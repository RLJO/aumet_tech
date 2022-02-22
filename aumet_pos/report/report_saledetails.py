from datetime import timedelta

from odoo import models, api, fields, _
from odoo.osv.expression import AND
import pytz


class ReportSaleDetails(models.AbstractModel):
    _inherit = "report.point_of_sale.report_saledetails"

    @api.model
    def get_sale_details(self, date_start=None, date_stop=None, config_ids=False, session_ids=False):
        domain = [('state', 'in', ['paid', 'invoiced', 'done'])]
        if (session_ids):
            domain = AND([domain, [('session_id', 'in', session_ids)]])
        else:
            if date_start:
                date_start = fields.Datetime.from_string(date_start)
            else:
                # start by default today 00:00:00
                user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                today = user_tz.localize(fields.Datetime.from_string(fields.Date.context_today(self)))
                date_start = today.astimezone(pytz.timezone('UTC'))

            if date_stop:
                date_stop = fields.Datetime.from_string(date_stop)
                # avoid a date_stop smaller than date_start
                if (date_stop < date_start):
                    date_stop = date_start + timedelta(days=1, seconds=-1)
            else:
                # stop by default today 23:59:59
                date_stop = date_start + timedelta(days=1, seconds=-1)

            domain = AND([domain,
                          [('date_order', '>=', fields.Datetime.to_string(date_start)),
                           ('date_order', '<=', fields.Datetime.to_string(date_stop))]
                          ])

            if config_ids:
                domain = AND([domain, [('config_id', 'in', config_ids)]])

        orders = self.env['pos.order'].search(domain)
        ##################################################
        # MONEY IN/MONEY OUT
        money_in = []
        money_out = []
        sessions = self.env["pos.session"].search([('config_id', 'in', config_ids),
                                                   ('start_at', '>=', fields.Datetime.to_string(date_start))
                                                   ])
        if sessions:
            for session in sessions:
                statement = self.env["account.bank.statement"].search(
                    [("pos_session_id", "=", session.id), ('date', '>=', fields.Datetime.to_string(date_start)),
                     ('date', '<=', fields.Datetime.to_string(date_stop))])
                if statement:
                    lines = statement.line_ids
                    for line in lines:
                        if line.payment_ref not in [statement.name,'Cash difference observed during the counting (Loss)']:
                            if line.amount < 0:
                                money_out.append({"reason": line.payment_ref, "amount": line.amount})
                            else:
                                money_in.append({"reason": line.payment_ref, "amount": line.amount})
        ##################################################
        user_currency = self.env.company.currency_id
        total = 0.0
        products_sold = {}
        taxes = {}
        credits = []
        insurances = []
        for order in orders:
            if order.partner_id:
                if order.partner_id.total_credit != 0:
                    credits.append({"name": order.partner_id.name, "amount": order.partner_id.total_credit})
            if order.insurance_account_move:
                insurance_account_move = order.insurance_account_move
                if insurance_account_move.partner_id:
                    if insurance_account_move.partner_id.total_credit != 0:
                        insurances.append({"name": insurance_account_move.partner_id.name,
                                           "amount": insurance_account_move.partner_id.total_credit})
            if user_currency != order.pricelist_id.currency_id:
                total += order.pricelist_id.currency_id._convert(
                    order.amount_total, user_currency, order.company_id, order.date_order or fields.Date.today())
            else:
                total += order.amount_total
            currency = order.session_id.currency_id
            for line in order.lines:
                key = (line.product_id, line.price_unit, line.discount)
                products_sold.setdefault(key, 0.0)
                products_sold[key] += line.qty

                if line.tax_ids_after_fiscal_position:
                    line_taxes = line.tax_ids_after_fiscal_position.sudo().compute_all(
                        line.price_unit * (1 - (line.discount or 0.0) / 100.0), currency, line.qty,
                        product=line.product_id, partner=line.order_id.partner_id or False)
                    for tax in line_taxes['taxes']:
                        taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount': 0.0, 'base_amount': 0.0})
                        taxes[tax['id']]['tax_amount'] += tax['amount']
                        taxes[tax['id']]['base_amount'] += tax['base']
                else:
                    taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount': 0.0, 'base_amount': 0.0})
                    taxes[0]['base_amount'] += line.price_subtotal_incl
        payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
        if payment_ids:
            self.env.cr.execute("""
                       SELECT method.name, sum(amount) total
                       FROM pos_payment AS payment,
                            pos_payment_method AS method
                       WHERE payment.payment_method_id = method.id
                           AND payment.id IN %s
                       GROUP BY method.name
                   """, (tuple(payment_ids),))
            payments = self.env.cr.dictfetchall()
        else:
            payments = []

        return {
            'currency_precision': user_currency.decimal_places,
            'total_paid': user_currency.round(total),
            'payments': payments,
            'company_name': self.env.company.name,
            'taxes': list(taxes.values()),
            'insurances': insurances,
            'credits': credits,
            "money_in": money_in, "money_out": money_out,
            'products': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'price_unit': price_unit,
                'discount': discount,
                'uom': product.uom_id.name
            } for (product, price_unit, discount), qty in products_sold.items()], key=lambda l: l['product_name'])
        }
