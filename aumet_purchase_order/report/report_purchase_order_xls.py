from odoo import models
from odoo.tools import format_datetime


class PurchaseOrderXlsx(models.AbstractModel):
    _name = 'report.aumet_purchase_order.purchase_order_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        order_format = workbook.add_format(
            {'bg_color': '#1FBBA6', 'align': 'center', 'font_size': 14,
             'font_color': 'white', 'bold': True, 'border': 1})
        header_format = workbook.add_format(
            {'align': 'center', 'font_size': 12, 'bold': True, 'border': 1})
        Vendor_format = workbook.add_format(
            {'align': 'center', 'font_size': 12,
             'font_color': '#1FBBA6', 'border': 1})

        table_format = workbook.add_format(
            {'align': 'center', 'font_size': 12,
             'bg_color': '#1FBBA6', 'font_color': 'white', 'border': 1})
        row_format = workbook.add_format(
            {'align': 'center', 'font_size': 12,
             'border': 1})
        for obj in lines:
            report_name = obj.name
            sheet = workbook.add_worksheet(report_name[:31])
            sheet.merge_range('A1:I1', '')
            sheet.merge_range('A1:B4', '')
            sheet.merge_range('A1:I1', '')
            sheet.merge_range('H1:I4', ' ')
            sheet.merge_range('A4:I4', '')

            sheet.merge_range('C2:E3', 'Purchase   Order :', order_format)
            sheet.merge_range('F2:G3', report_name, order_format)
            sheet.merge_range('A5:B5', 'Vendor', header_format)
            sheet.merge_range('C5:E5', obj.partner_id.name, Vendor_format)
            sheet.merge_range('A6:B6', 'Vendor Reference', header_format)
            sheet.merge_range('C6:E6', obj.partner_ref or " ", Vendor_format)
            sheet.merge_range('F5:G5', 'Order Deadline', header_format)
            sheet.merge_range('H5:J5', format_datetime(
                self.env, obj.date_order, dt_format=False) if obj.date_order else '',
                              Vendor_format)
            sheet.merge_range('F6:G6', 'Receipt Date', header_format)
            sheet.merge_range('H6:J6', format_datetime(
                self.env, obj.date_planned, dt_format=False)
            if obj.date_planned else '',
                              Vendor_format)

            data = {}
            for order in obj.order_line:
                if len(order.taxes_id) > 1:
                    key = "Multi Taxes"
                else:
                    key = order.taxes_id.name if order.taxes_id else 'UnTaxes'

                if key in data:
                    data[key].append(order)
                else:
                    data[key] = [order]

            row = 7
            for item in data:
                sheet.merge_range('A{row}:B{row}'.format(row=(row + 1)), item, table_format)
                row += 1
                sheet.write(row, 0, 'S NO', table_format)
                sheet.merge_range('B{row}:D{row}'.format(row=(row + 1)), 'PRODUCT', table_format)
                sheet.write(row, 4, 'QTY', table_format)
                sheet.write(row, 5, 'PRICE', table_format)
                sheet.write(row, 6, 'TAXES', table_format)
                sheet.merge_range('H{row}:J{row}'.format(row=(row + 1)), 'SUBTOTAL', table_format)
                row += 1
                index = 1
                for order in data[item]:
                    sheet.write(row, 0, index, row_format)
                    sheet.merge_range('B{row}:D{row}'.format(row=(row + 1)), order.product_id.name, row_format)
                    sheet.write(row, 4, order.product_qty, row_format)
                    sheet.write(row, 5, "{:.3f}".format(order.price_unit), row_format)
                    sheet.write(row, 6, ''.join([str(int(tax.amount)) + '% ' for tax in order.taxes_id]), row_format)
                    sheet.merge_range('H{row}:J{row}'.format(row=(row + 1)), "{:.3f}".format(order.price_subtotal),
                                      row_format)

                    row += 1
                    index += 1
                row += 2
            sheet.merge_range('F{row}:G{row}'.format(row=(row + 1)), 'Untaxed Amount', table_format)
            sheet.merge_range('H{row}:J{row}'.format(row=(row + 1)), "{:.3f}".format(obj.amount_untaxed), row_format)
            row += 1
            sheet.merge_range('F{row}:G{row}'.format(row=(row + 1)), 'Taxes', table_format)
            sheet.merge_range('H{row}:J{row}'.format(row=(row + 1)), "{:.3f}".format(obj.amount_tax), row_format)
            row += 1
            sheet.merge_range('F{row}:G{row}'.format(row=(row + 1)), 'Total', table_format)
            sheet.merge_range('H{row}:J{row}'.format(row=(row + 1)), "{:.3f}".format(obj.amount_total), row_format)
