from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class ProductVendorWizard(models.TransientModel):
    _name = "shortfall.wizard"
    _description = 'ShortFall Report'

    from_date = fields.Date(string="From Date", default=datetime.now())
    to_date = fields.Date(string="To Date", default=datetime.now())

    @api.onchange("to_date")
    def onchange_to_date(self):
        date = datetime.date(datetime.now())
        if self.to_date > date:
            self.to_date = date

    def print_report(self):
        product_list = []
        self._cr.execute(f"""select line.product_id,line.name,sum(line.product_qty) as sold_qty
                                from stock_inventory as st
                                right join (select line.inventory_id,line.product_id,line.product_qty,p.name
                                            from stock_inventory_line as line
                                            left join(select p.id,pt.name 
                                                    from product_product as p join product_template  as pt
                                                    on p.product_tmpl_id =pt.id ) as p
                                            on p.id =line.product_id) as line
                                on line.inventory_id = st.id
                                where st.page_type='Out' and st.date::date >='{self.from_date}' AND st.date::date <='{self.to_date}'
                                GROUP BY (line.product_id,line.name)
                                UNION all 
                                select line.product_id,line.name,sum(line.product_uom_qty) as sold_qty
                                from sale_order as so
                                right join (select line.order_id,line.product_id,line.product_uom_qty,p.name
                                            from sale_order_line as line
                                            left join (select p.id,pt.name 
                                            from product_product as p join product_template  as pt
                                            on p.product_tmpl_id =pt.id ) as p
                                on p.id =line.product_id) as line
                                on line.order_id = so.id
                                where so.state='sale' and so.date_order::date >='{self.from_date}' AND so.date_order::date <='{self.to_date}'
                                GROUP BY (line.product_id,line.name)
                                UNION all 
                                select line.product_id,line.name,sum(line.qty) as sold_qty
                                from pos_order as po
                                right join (select line.order_id,line.product_id,line.qty,p.name
                                from pos_order_line as line
                                left join (select p.id,pt.name from product_product as p join product_template  as pt
                                on p.product_tmpl_id =pt.id ) as p
                                on p.id =line.product_id) as line
                                on line.order_id = po.id
                                where (po.state='paid' or po.state='done' or po.state='invoiced') and po.date_order::date >='{self.from_date}' AND po.date_order::date <='{self.to_date}'
                                GROUP BY (line.product_id,line.name)""")
        products = self._cr.fetchall()
        for product in products:
            product_id = product[0]
            product_obj = self.env["product.product"].search([("id", "=", product_id)])
            if product_obj.qty_available > 0 or product[2] > 0:
                product_data = dict()
                product_data["name"] = product[1]
                product_data["vendor"] = ""
                vendor = self.env["product.supplierinfo"].search(
                    [("product_tmpl_id", "=", product_obj.product_tmpl_id.id)])
                if vendor:
                    product_data["vendor"] = vendor[0].name.name
                product_data["sold"] = round(product[2], 3)
                product_data["qty"] = round(product_obj.qty_available, 3)
                product_data["expiry"] = ""

                self._cr.execute(f"""select array_agg(DISTINCT lot.id) as lot_id
                                        from product_product as p
                                        right join(select id,product_id from stock_production_lot) as lot
                                        on lot.product_id = p.id
                                        where p.id={product_id}
                                        GROUP BY (p.id)""")
                lots_data = []
                product_data["lots"] = []
                lots = self._cr.fetchone()
                if lots:
                    for lot in lots[0]:
                        lot_obj = self.env["stock.production.lot"].search([("id", "=", lot)])
                        expiration_date = ""
                        if lot_obj.expiration_date:
                            expiration_date = datetime.date(lot_obj.expiration_date)
                        lots_data.append({"qty": round(lot_obj.remaining_qty, 3), "expiry": expiration_date})
                    product_data["lots"] = sorted(lots_data, key=lambda d: d['qty'])
                product_list.append(product_data)
        if product_list:
            datas = {
                'ids': self.id,
                'model': self._name,
                'data': sorted(product_list, key=lambda d: d['qty']), "from_date": self.from_date,
                "to_date": self.to_date}
            return self.env.ref('aumet_product_vendor_report.aumet_shortfall_report_action').report_action(self, datas)
        else:
            raise UserError(_(f"You don't have any sold product from {self.from_date} to {self.to_date}"))
