from odoo import models, api


class MultiUOM(models.Model):
    _inherit = 'product.template'

    @api.onchange("uom_id")
    def update_list_uom(self):
        product_id = self._origin.id
        product_uom = self.env["uom.uom"].search([("id", "=", self.uom_id.id)])
        if product_id:
            self.env.cr.execute(
                f"""delete from product_multi_uom_price where product_id={product_id}""")
            self.env.cr.commit()
        fetch_uom_category = self.env["uom.uom"].search(
            [("category_id", "=", product_uom.category_id.id)])
        for uom in fetch_uom_category:
            uom_type = uom.uom_type
            if uom.id != self.uom_id.id:
                if uom_type == "smaller" or uom_type == "bigger":
                    unit_price = self.list_price / uom.factor
                else:
                    unit_price = self.list_price
                if product_id:
                    self.env.cr.execute(f"""insert into product_multi_uom_price (uom_id,product_id,price)
                                    values ({uom.id},{product_id},{unit_price})""")
                    self.env.cr.commit()
