# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('active_ingredient_ids')
    def _compute_alternate_product_ids(self):
        self.alternate_product_ids = []
        if self.id:
            self._cr.execute("""   select id from product_product where  product_product.product_tmpl_id in (SELECT DISTINCT product_template_id
                                    FROM
                                      (
                                        SELECT product_template_id,ARRAY_AGG(active_ingredient_id ORDER BY product_template_id) active_ingredient_id
                                        FROM active_ingredient_product_template_rel
                                        GROUP BY product_template_id
                                      ) q
                                      WHERE active_ingredient_id=(
                                            SELECT ARRAY_AGG(active_ingredient_id ORDER BY product_template_id) active_ingredient_id
                                            FROM active_ingredient_product_template_rel
                                            WHERE product_template_id in %s
                                          ) and product_template_id not in %s)""",
                             [tuple(self.ids), tuple(self.ids)])
            res = self._cr.fetchall()

            if res:
                self.alternate_product_ids = [item[0] for item in res]

    alternate_product_ids = fields.Many2many('product.product', string="Alternative Product", store=False,
                                             compute=_compute_alternate_product_ids)
