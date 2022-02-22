import base64
from io import BytesIO
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlwt
from odoo.exceptions import UserError
from odoo import models, fields, api, _


class ProductExpiryReport(models.Model):
    _name = "product.expiry.report"
    _description = "Product Expiry Report"

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    location_ids = fields.Many2many('stock.location', string="Location")
    vendor_id = fields.Many2one("res.partner", "Vendor", domain=[("supplier_rank", ">", 0)])

    @api.onchange("warehouse_id")
    def _onchange_warehouse(self):
        if self.warehouse_id:
            main_location = self.warehouse_id.view_location_id.id
            locations = self.env["stock.location"].search([("location_id", "=", main_location)])
            list_location = [location.id for location in locations]
            return {'domain': {'location_ids': [('usage', '=', 'internal'), ("id", "in", list_location)]}}
        return {'domain': {'location_ids': [('usage', '=', 'internal')]}}

    def print_pdf_report(self):
        return self.print_product_expiry_report('pdf')

    def print_xls_report(self):
        module_installed = self.env['ir.module.module'].search([('name', '=', 'product_expiry'),
                                                                ('state', '=', 'installed')])
        if not module_installed:
            raise UserError(_('Please enable "Expiration Dates" from Inventory-->Settings-->Traceability'))
        else:
            return self.print_product_expiry_report('xls')

    def set_data(self, locations):
        location_data = []
        for location in locations:
            if self.vendor_id:
                self._cr.execute(f"""select q.product_id,sup.name as vendor, array_agg(DISTINCT lot.id) as lot_id
                                     from stock_quant as q
                                     right join (select id,product_id 
			                                     from stock_production_lot 
			                                     where expiration_date::date>='{self.from_date}' AND
			                                           expiration_date::date<='{self.to_date}') as lot
                                     on lot.product_id =q.product_id
                                     right join (select sup.name,p.id as product_id 
                                                 from product_supplierinfo as sup 
		                                         left join (select id,product_tmpl_id 
		                                                    from product_product) as p
		                                         on p.product_tmpl_id =sup.product_tmpl_id
		                                         where sup.name ={self.vendor_id.id}) as sup
		                             on sup.product_id = q.product_id
                                     where q.location_id={location.id}
                                     GROUP BY (q.product_id,sup.name)""")
            else:
                self._cr.execute(f"""select q.product_id,sup.name as vendor, array_agg(DISTINCT lot.id) as lot_id
                                    from stock_quant as q
                                    right join (select  id,product_id 
                			                    from stock_production_lot 
                			                    where expiration_date::date>='{self.from_date}' AND
                			                          expiration_date::date<='{self.to_date}') as lot
                                    on lot.product_id =q.product_id
                                    left join (select sup.name,p.id as product_id 
                                               from product_supplierinfo as sup 
                		                        left join (select id,product_tmpl_id 
                		                                    from product_product) as p
                		                        on p.product_tmpl_id =sup.product_tmpl_id) as sup
                		            on sup.product_id = q.product_id
                                    where q.location_id={location.id}
                                    GROUP BY (q.product_id,sup.name)""")
            quants = self._cr.fetchall()
            product_data = []
            for quant in quants:
                product_id = quant[0]
                product_odj = self.env["product.product"].search([("id", "=", product_id)])
                if product_odj.qty_available > 0:
                    vendor_id = quant[1]
                    vendor_name =""
                    if vendor_id:
                        vendor =self.env["res.partner"].search([("id", '=', vendor_id)])
                        vendor_name =vendor.name
                    lots = quant[2]
                    lot_data = []
                    for lot in lots:
                        lot_obj = self.env["stock.production.lot"].search([("product_id", "=", product_id),
                                                                           ("id", "=", lot)])
                        if lot_obj.remaining_qty > 0:
                            expiry_date = lot_obj.expiration_date
                            remaining_day = 0
                            if expiry_date:
                                expiry_date = datetime.date(lot_obj.expiration_date)
                                remaining_day = (lot_obj.expiration_date - datetime.now()).days
                            lot_data.append({"name": lot_obj.name,
                                                "remaining_qty": round(lot_obj.remaining_qty, 3),
                                                "available_qty": round(lot_obj.product_qty, 3),
                                                 "remaining_day": remaining_day,
                                                 "expiry_date": expiry_date})
                        if lot_data:
                            product_data.append({"name": product_odj.display_name, "vendor": vendor_name,
                                                    "available_qty": round(product_odj.qty_available, 3),
                                                     "remaining_qty": "", "remaining_day": "", "expiry_date": "",
                                                     "lots": lot_data})
            location_data.append({"location": location.name, "products": product_data})
        return location_data

    def print_product_expiry_report(self, report_type):
        data = []
        locations = self.location_ids
        if self.warehouse_id:
            if not locations:
                main_location = self.warehouse_id.view_location_id.id
                locations = self.env["stock.location"].search([("location_id", "=", main_location)])
            location_data = self.set_data(locations)
            data.append({"warehouse": self.warehouse_id.name, "locations": location_data})
        ##################################################################
        else:
            warehouses = self.env["stock.warehouse"].search([])
            for warehouse in warehouses:
                main_location = warehouse.view_location_id.id
                locations = self.env["stock.location"].search([("location_id", "=", main_location)])
                location_data = self.set_data(locations)
                data.append({"warehouse": warehouse.name, "locations": location_data})
        if report_type == 'pdf':
            datas = {
                'ids': self.id,
                'model': self._name,
                'data': data,
                'from_date': self.from_date,
                "to_date": self.to_date
            }
            return self.env.ref('flexipharmacy.product_expiry_report').report_action(self, data=datas)
        elif report_type == 'xls':
            return self.print_xls_product_report(data)

    #
    #     def print_product_expiry_report(self, report_type):
    #         # if self.num_expiry_days <= 0:
    #         # raise UserError('Number Of Expiry Days should be greater then 0')
    #         # if
    #         query = False
    #         location_ids = self.location_ids.ids or self.env['stock.location'].search([('usage', '=', 'internal')]).ids
    #         category_ids = self.category_ids.ids or self.env['product.category'].search([]).ids
    #         if self.from_date and self.to_date:
    #             query = '''SELECT
    #                             sq.location_id,
    #                             sl.usage,
    #                             spl.product_id,
    #                             spl.id,
    #                             spl.expiration_date,
    #                             spl.name,
    #                             pc.name as product_category,
    #                             pp.default_code,
    #                             pt.name as product_name
    #                         FROM stock_production_lot spl
    #                             LEFT JOIN stock_quant sq on sq.lot_id = spl.id
    #                             LEFT JOIN stock_location sl on sq.location_id = sl.id
    #                             LEFT JOIN product_product pp on spl.product_id = pp.id
    #                             LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
    #                             LEFT JOIN product_category pc on pt.categ_id = pc.id
    #                         WHERE spl.expiration_date <= '%s' AND
    #                               spl.expiration_date >= '%s' AND
    #                               pc.id IN %s order by pp.default_code
    #                 ''' % (self.to_date, self.from_date, "(%s)" % ','.join(map(str, category_ids)))
    #         else:
    #             query = '''SELECT
    #                             sq.location_id,
    #                             sl.usage,
    #                             spl.product_id,
    #                             spl.id,
    #                             spl.expiration_date,
    #                             spl.name,
    #                             pc.name as product_category,
    #                             pp.default_code,pt.name as product_name
    #                         FROM stock_production_lot spl
    #                             LEFT JOIN stock_quant sq on sq.lot_id = spl.id
    #                             LEFT JOIN stock_location sl on sq.location_id = sl.id
    #                             LEFT JOIN product_product pp on spl.product_id = pp.id
    #                             LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
    #                             LEFT JOIN product_category pc on pt.categ_id = pc.id
    #                         WHERE
    #                             pc.id IN %s order by pp.default_code''' % ("(%s)" % ','.join(map(str, category_ids)))
    #
    #         self.env.cr.execute(query)
    #         res1 = self.env.cr.dictfetchall()
    #
    #         temp_res = []
    #         for each in res1:
    #             if each.get('usage') in ['internal', None]:
    #                 temp_res.append(each)
    #         if self.from_date and self.to_date:
    #             query = '''SELECT
    #                             sq.location_id,
    #                             sl.usage,
    #                             spl.product_id,
    #                             spl.id,
    #                             spl.expiration_date,
    #                             spl.name,
    #                             pc.name as product_category,
    #                             pp.default_code,pp.id as product_id,
    #                             pt.name as product_name
    #                         FROM stock_quant sq
    #                             LEFT JOIN stock_location sl on sq.location_id = sl.id
    #                             LEFT JOIN stock_production_lot spl on sq.lot_id = spl.id
    #                             LEFT JOIN product_product pp on spl.product_id = pp.id
    #                             LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
    #                             LEFT JOIN product_category pc on pt.categ_id = pc.id
    #                         WHERE spl.expiration_date <= '%s' AND
    #                               spl.expiration_date >= '%s' AND
    #                               pc.id IN %s AND
    #                               sq.location_id IN %s order by pp.default_code''' % (
    #                 self.to_date, self.from_date, "(%s)" % ','.join(map(str, category_ids)),
    #                 "(%s)" % ','.join(map(str, location_ids)))
    #         else:
    #             query = '''SELECT
    #                             sq.location_id,
    #                             sl.usage,
    #                             spl.product_id,
    #                             spl.id,
    #                             spl.expiration_date,
    #                             spl.name,
    #                             pc.name as product_category,
    #                             pp.default_code,pp.id as product_id,
    #                             pt.name as product_name
    #                         FROM stock_quant sq
    #                             LEFT JOIN stock_location sl on sq.location_id = sl.id
    #                             LEFT JOIN stock_production_lot spl on sq.lot_id = spl.id
    #                             LEFT JOIN product_product pp on spl.product_id = pp.id
    #                             LEFT JOIN product_template pt on pp.product_tmpl_id  = pt.id
    #                             LEFT JOIN product_category pc on pt.categ_id = pc.id
    #                         WHERE  pc.id IN %s AND
    #                             sq.location_id IN %s order by pp.default_code''' % (
    #                 "(%s)" % ','.join(map(str, category_ids)), "(%s)" % ','.join(map(str, location_ids)))
    #         self.env.cr.execute(query)
    #         res = self.env.cr.dictfetchall()
    #         if not self.location_ids:
    #             res = res + temp_res
    #             res = [dict(item) for item in {tuple(each.items()) for each in res}]
    #         vals = {}
    #         if len(res) == 0:
    #             raise UserError(_('No such record found for product expiry.'))
    #         else:
    #             if self.group_by == 'category':
    #                 vals = {}
    #                 for each in res:
    #                     if not each.get('location_id'):
    #                         location_name = "--"
    #                     else:
    #                         location_name = self.env['stock.location'].browse(
    #                             each.get('location_id')).display_name
    #                     if each['product_category'] not in vals:
    #                         vals[each.get('product_category')] = [
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'location_name': location_name,
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, }]
    #                     else:
    #                         vals[each.get('product_category')].append(
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'location_name': location_name,
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, })
    #             if self.group_by == 'product':
    #                 vals = {}
    #                 for each in res:
    #                     if not each.get('product_id'):
    #                         location_name = "--"
    #                     else:
    #                         location_name = self.env['product.product'].browse(
    #                             each.get('product_id')).display_name
    #                     if location_name not in vals:
    #                         vals[location_name] = [
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'product_category': each.get('product_category'),
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, }]
    #                     else:
    #                         vals[location_name].append(
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'product_category': each.get('product_category'),
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, })
    #             if self.group_by == 'warehouse':
    #                 vals = {}
    #                 for each in res:
    #                     if not each.get('location_id'):
    #                         location_name = "--"
    #                     else:
    #                         location_id = each.get('location_id')
    #                         wh_location_name = location_name = self.env['stock.location'].browse(each.get('location_id'))
    #                         location_name = wh_location_name.get_warehouse().name
    #                     if location_name not in vals:
    #                         vals[location_name] = [
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'product_category': each.get('product_category'),
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, }]
    #                     else:
    #                         vals[location_name].append(
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'product_category': each.get('product_category'),
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, })
    #             if self.group_by == 'location':
    #                 vals = {}
    #                 for each in res:
    #                     if not each.get('location_id'):
    #                         location_name = "--"
    #                     else:
    #                         location_name = self.env['stock.location'].browse(each.get('location_id')).display_name
    #                     if location_name not in vals:
    #                         vals[location_name] = [
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'product_category': each.get('product_category'),
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, }]
    #                     else:
    #                         vals[location_name].append(
    #                             {'name': each.get('name'),
    #                              'product_id': each.get('product_name'),
    #                              'product_category': each.get('product_category'),
    #                              'default_code': each.get('default_code') or '--------',
    #                              'expiration_date': each.get('expiration_date'),
    #                              'remaining_days': relativedelta(each.get('expiration_date'), date.today()).days,
    #                              'available_qty': self.env['stock.production.lot'].browse(
    #                                  each.get('id')).product_qty if each.get('id') else False, })
    #         vals.update(
    #             {'group_by': self.group_by, 'today_date': date.today(), 'from_date': self.from_date,
    #              'to_date': self.to_date})
    #         vals_new = {}
    #         vals_new.update({'stock': vals})
    #         if report_type == 'pdf':
    #             return self.env.ref('flexipharmacy.product_expiry_report').report_action(self, data=vals_new)
    #         elif report_type == 'xls':
    #             return self.print_xls_product_report(vals)
    #
    def print_xls_product_report(self, vals):
        style_pc = xlwt.XFStyle()
        bold = xlwt.easyxf("font: bold on; pattern: pattern solid ,fore_colour white;")
        table_row = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
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

        worksheet = workbook.add_sheet('Stock Expiry Report')
        for num in range(0, 7):
            worksheet.col(num).width = 5600
        worksheet.write_merge(1, 2, 0, 6, 'Product Expiry Report', style=style_pc)
        worksheet.write(4, 0, "From Date", bold)
        worksheet.write(4, 1, str(self.from_date))
        worksheet.write(4, 4, "To Date", bold)
        worksheet.write(4, 5, str(self.to_date))
        row_index = 6
        for val in vals:
            worksheet.write(row_index, 1, 'Warehouse :- ' + val['warehouse'], bold)
            for loc in val["locations"]:
                worksheet.write(row_index, 2, 'Location :- ' + loc["location"], bold)
                row_index += 1
                if loc["products"]:
                    worksheet.write(row_index, 0, 'Product', bold)
                    worksheet.write(row_index, 1, 'Vendor', bold)
                    worksheet.write(row_index, 2, 'Available Quantity', bold)
                    worksheet.write(row_index, 3, 'Remaining Quantity', bold)
                    worksheet.write(row_index, 4, 'Remaining Day', bold)
                    worksheet.write(row_index, 5, 'Expiration Date', bold)
                    row_index += 1
                    for prod in loc["products"]:
                        worksheet.write(row_index, 0, prod['name'], table_row)
                        worksheet.write(row_index, 1, prod['vendor'], table_row)
                        worksheet.write(row_index, 2, prod['available_qty'], table_row)
                        worksheet.write(row_index, 3, prod['remaining_qty'], table_row)
                        worksheet.write(row_index, 4, prod['remaining_day'], table_row)
                        worksheet.write(row_index, 5, prod['expiry_date'], table_row)
                        row_index += 1
                        for lot in prod["lots"]:
                            worksheet.write(row_index, 0, "")
                            worksheet.write(row_index, 1, "")
                            worksheet.write(row_index, 2, lot['available_qty'])
                            worksheet.write(row_index, 3, lot['remaining_qty'])
                            worksheet.write(row_index, 4, lot['remaining_day'])
                            worksheet.write(row_index, 5,
                                            lot['expiry_date'].strftime('%d/%m/%Y') if lot["expiry_date"] else "")
                            row_index += 1
        file_data = BytesIO()
        workbook.save(file_data)
        report_id = self.env['report.download.wizard'].create({
            'data': base64.encodestring(file_data.getvalue()),
            'name': 'Product Expiry Report.xls'})
        return {
            'name': 'Download Excel Report',
            'view_mode': 'form',
            'res_model': 'report.download.wizard',
            'target': 'new',
            'res_id': report_id.id,
            'type': 'ir.actions.act_window'
        }
