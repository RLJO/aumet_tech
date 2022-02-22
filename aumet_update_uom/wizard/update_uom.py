# -*- coding: utf-8 -*-
import base64
from io import BytesIO
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from xlrd import open_workbook

from odoo.tools.misc import xlwt
from odoo.exceptions import Warning, UserError
from odoo import models, fields, api, _
from itertools import groupby
import concurrent.futures as multi_process


class UpadteUOM(models.TransientModel):
    _name = "update.uom"
    _description = "Update UOM"

    file = fields.Binary('Upload file to update UOM')
    update_all = fields.Boolean("Update all UOM multi Price for all product")

    def fix_orphan_categ(self):
        self._cr.execute("""
                    SELECT C.id AS category_id, count(U.id) AS uom_count
                    FROM uom_category C
                    LEFT JOIN uom_uom U ON C.id = U.category_id AND uom_type = 'reference' AND U.active = 't'
                    GROUP BY C.id
                """)
        for uom_data in self._cr.dictfetchall():
            if uom_data['uom_count'] == 0:
                self.env['uom.uom'].create({'name': self.env['uom.category'].browse(uom_data['category_id']).name,
                                            'category_id': uom_data['category_id'], 'uom_type': 'reference'})

    # def fix_orphan_categ_cron(self):
    #     env.cr.execute("""
    #                         SELECT C.id AS category_id, count(U.id) AS uom_count
    #                         FROM uom_category C
    #                         LEFT JOIN uom_uom U ON C.id = U.category_id AND uom_type = 'reference' AND U.active = 't'
    #                         GROUP BY C.id
    #                     """)
    #     for uom_data in env.cr.dictfetchall():
    #         if uom_data['uom_count'] == 0:
    #             env['uom.uom'].create({'name': env['uom.category'].browse(uom_data['category_id']).name,
    #                                    'category_id': uom_data['category_id'], 'uom_type': 'reference'})

    def submit(self):
        if self.file:
            # self.fix_orphan_categ()
            wb = open_workbook(file_contents=base64.decodestring(self.file))
            for s in wb.sheets():
                first_row = []  # Header
                for col in range(s.ncols):
                    first_row.append(s.cell_value(0, col))
                for row in range(1, s.nrows):
                    elm = {}
                    for col in range(s.ncols):
                        if isinstance(s.cell_value(row, col), float):
                            elm[first_row[col]] = s.cell_value(row, col)
                        else:
                            if not isinstance(s.cell_value(row, col), str):
                                elm[first_row[col]] = str(int(s.cell_value(row, col)))
                            else:
                                elm[first_row[col]] = s.cell_value(row, col)
                    uom_id = self.env['uom.uom'].search([('name', '=', elm['uom_id'].strip())], limit=1)
                    if uom_id:
                        uom_id = uom_id.id
                    else:
                        category_id = self.env['uom.category'].create({
                            'name': elm['uom_id'],
                            'is_pos_groupable': True
                        })

                        uom_id = self.env['uom.uom'].create({
                            'name': elm['uom_id'],
                            'category_id': category_id.id,
                            'uom_type': 'reference'

                        })
                        uom_id = uom_id.id
                    fetch_product = self.env["product.product"].search([("barcode", "=", elm['barcode'])])
                    if fetch_product:
                        product_id = fetch_product.id
                        product_tmpl_id = fetch_product.product_tmpl_id.id

                        # product
                        self._cr.execute(f"""update product_template set uom_id={uom_id},uom_po_id={uom_id}
                                                where id={product_tmpl_id} 
                                                """)

                        self._cr.execute(f"""update product_replenish set product_uom_id={uom_id}
                                                where product_id={product_id} 
                                                """)
                        # sale
                        self._cr.execute(f"""update sale_order_template_line set product_uom_id={uom_id}
                                                where product_id ={product_id}  
                                                """)

                        self._cr.execute(f"""update sale_order_line set product_uom={uom_id}
                                                where product_id={product_id}  
                                                """)

                        self._cr.execute(f"""update sale_order_template_option set uom_id={uom_id}
                                                where product_id={product_id}  
                                                """)

                        self._cr.execute(f"""update sale_order_option set uom_id={uom_id}
                                                where product_id={product_id}  
                                               """)
                        # pos
                        self._cr.execute(f"""update pos_order_line set uom_id={uom_id}
                                                where product_id ={product_id}
                                                """)

                        # purchase
                        self._cr.execute(f"""update purchase_order_line set product_uom={uom_id}
                                                where product_id ={product_id}
                                               """)
                        # stock
                        self._cr.execute(f"""update stock_scrap set product_uom_id={uom_id} 
                                            where product_id = {product_id} 
                                            """)

                        self._cr.execute(f"""update stock_move set product_uom={uom_id}
                                                where product_id ={product_id}
                                                """)

                        self._cr.execute(f"""update stock_move_line set product_uom_id={uom_id}
                                             where product_id ={product_id}
                                             """)

                        self._cr.execute(f"""update stock_inventory_line set product_uom_id={uom_id}
                                                where product_id ={product_id}
                                               """)

                        self._cr.execute(f"""update stock_production_lot set product_uom_id={uom_id} 
                                                where product_id = {product_id}
                                            """)
                        # account
                        self._cr.execute(f"""update account_move_line set product_uom_id={uom_id}
                                               where product_id ={product_id}
                                              """)
                        self._cr.execute(f"""update account_analytic_line set product_uom_id={uom_id}
                                             where product_id ={product_id}
                                           """)
                        if not self.update_all:
                            fetch_product.product_tmpl_id.update_list_uom()

        if self.update_all:
            products = self.env["product.template"].search([])
            with multi_process.ThreadPoolExecutor() as exec:
                exec.map(lambda product: product.update_list_uom(), products)
