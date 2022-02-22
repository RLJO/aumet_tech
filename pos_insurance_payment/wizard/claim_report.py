# -*- coding: utf-8 -*-
import base64
from io import BytesIO
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt
from odoo.exceptions import Warning, UserError
from odoo import models, fields, api, _
from itertools import groupby


class ClaimReport(models.TransientModel):
    _name = "claim.report"
    _description = "Claim Report"

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    partner_ids = fields.Many2many('res.partner')

    def print_pdf_report(self):
        return self.print_claim_report('pdf')

    def print_xls_report(self):
        return self.print_claim_report('xls')

    def print_claim_report(self, report_type):
        vals = {'pages': {}, 'companies': {}, 'from_date': self.from_date, 'to_date': self.to_date}
        partner_ids = self.partner_ids.ids
        domain = [('state', '=', 'posted'), ('payment_state', 'in', ['partial', 'not_paid']),
                  ('invoice_date', '>=', self.from_date), ('invoice_date', '<=', self.to_date),
                  ('move_type', '=', 'out_invoice')]
        if partner_ids:
            domain.append(('partner_id', 'in', partner_ids))

        invoices = self.env['account.move'].search(domain, order='invoice_date')
        for invoice in invoices:
            company_id = invoice.partner_id.id
            if company_id not in vals['pages']:
                vals['pages'][company_id] = []
                vals['companies'][company_id] = invoice.partner_id.name

            inv_data = {
                'name': invoice.name,
                'approval_number': invoice.partial_payment_remark,
                'form_number': invoice.form_number,
                'card_number': invoice.partner_shipping_id.member_number,
                'hi_percentage': invoice.partner_shipping_id.hi_percentage,
                'date': invoice.invoice_date,
                'invoice_untaxed_amount': round(invoice.amount_untaxed +
                                                (
                                                        invoice.patient_account_move_id and invoice.patient_account_move_id.amount_untaxed or 0),
                                                2),
                'invoice_amount': round(invoice.amount_total, 3),
                'cont_amount': round(invoice.customer_paid, 3),
                'req_amount': round(invoice.amount_residual, 3)
            }

            vals['pages'][company_id].append(inv_data)

        if report_type == 'pdf':
            return self.env.ref('pos_insurance_payment.claim_report').with_context(landscape=True).report_action(self,
                                                                                                                 data=vals)
        elif report_type == 'xls':
            return self.print_xls_product_report(vals)

    def print_xls_product_report(self, vals):
        style_pc = xlwt.XFStyle()
        bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        style_pc.alignment = alignment
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        font = xlwt.Font()
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.THIN
        font.bold = True
        font.height = 500
        style_pc.font = font
        style_pc.alignment = alignment
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['gray25']
        style_pc.pattern = pattern
        workbook = xlwt.Workbook()
        file_data = BytesIO()
        sheets = vals['pages']

        for company in sheets:
            worksheet = workbook.add_sheet(vals['companies'][company])
            worksheet.write_merge(1, 2, 0, 6, vals['companies'][company], style=style_pc)
            worksheet.write(4, 0, "From Date", bold)
            worksheet.write(4, 1, str(vals.get('from_date')))
            worksheet.write(4, 4, "To Date", bold)
            worksheet.write(4, 5, str(vals.get('to_date')))

            worksheet.write(6, 0, "#", bold)
            worksheet.write(6, 1, "Invoice", bold)
            worksheet.write(6, 2, "Date", bold)
            worksheet.write(6, 3, "Card Number", bold)
            worksheet.write(6, 4, "Customer Coverage %", bold)
            worksheet.write(6, 5, "Insurance Form Number", bold)
            worksheet.write(6, 6, "Approval Number", bold)
            worksheet.write(6, 7, "Untaxed Amount", bold)
            worksheet.write(6, 8, "Total Amount", bold)
            worksheet.write(6, 9, "Company Part", bold)
            worksheet.write(6, 10, "Patient Contribution Part", bold)
            worksheet.write(6, 11, "Required Amount", bold)
            row_index = 7
            count = 1
            req_amount_sum = 0
            for invoice in vals['pages'][company]:
                worksheet.write(row_index, 0, str(count))
                worksheet.write(row_index, 1, str(invoice['name'] or ''))
                worksheet.write(row_index, 2, str(invoice['date']))
                worksheet.write(row_index, 3, str(invoice['card_number'] or ''))
                worksheet.write(row_index, 4, str(invoice['hi_percentage']))
                worksheet.write(row_index, 5, str(invoice['form_number'] or ''))
                worksheet.write(row_index, 6, str(invoice['approval_number'] or ''))
                worksheet.write(row_index, 7, str(invoice['invoice_untaxed_amount']))
                worksheet.write(row_index, 8, str(invoice['invoice_amount'] + invoice['cont_amount']))
                worksheet.write(row_index, 9, str(invoice['invoice_amount']))
                worksheet.write(row_index, 10, str(invoice['cont_amount']))
                worksheet.write(row_index, 11, str(invoice['req_amount']), bold)
                req_amount_sum += invoice['req_amount']
                row_index += 1
                count += 1
            worksheet.write(row_index, 10, 'Total', bold)
            worksheet.write(row_index, 11, str(req_amount_sum), bold)
        if not sheets:
            worksheet = workbook.add_sheet('Report')

        workbook.save(file_data)
        report_id = self.env['report.download.wizard'].create({
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'Claim Report.xls'
        })
        return {
            'name': 'Download Excel Report',
            'view_mode': 'form',
            'res_model': 'report.download.wizard',
            'target': 'new',
            'res_id': report_id.id,
            'type': 'ir.actions.act_window'
        }
