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


class UpdateProductUOM(models.TransientModel):
    _name = "product.update.uom"
    _description = "Update UOM"

    product = fields.Many2one('product.template', string='Product')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure ')

    def submit(self):
        uom_id = self.uom_id.id
        fetch_product_template = self.product
        if fetch_product_template:
            product_temp_id = fetch_product_template.id
            product_id = self.env["product.product"].search([("barcode", "=", fetch_product_template.barcode)]).id
            self._cr.execute(f"""update product_template set uom_id={uom_id},uom_po_id={uom_id}
                                                          where id={product_temp_id} 
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
            fetch_product_template.update_list_uom()
