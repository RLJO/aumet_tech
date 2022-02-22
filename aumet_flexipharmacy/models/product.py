# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends('active_ingredient_ids')
    def _compute_alternate_product_ids(self):
        product_product = self.env['product.product']
        for product_id in self:
            if product_id.active_ingredient_ids:
                _products = product_product.search(
                    [('active_ingredient_ids', '!=', False), ('product_tmpl_id', '!=', product_id.id)])
                _alternate_product_ids = _products.filtered(
                    lambda product: len(
                        list(set(product_id.active_ingredient_ids) & set(product.active_ingredient_ids))) > 0)

                product_id.write({'alternate_product_ids': _alternate_product_ids.mapped('id')})
            else:
                product_id.write({'alternate_product_ids': []})

    @api.depends('active_ingredient_ids')
    def _get_ingredient_search_string(self):
        for rec in self:
            name_search_string = ''
            for ingredient in rec.active_ingredient_ids:
                name_search_string += '|' + ingredient.name
            rec.ingredient_ids_name = name_search_string
        return name_search_string

    ingredient_ids_name = fields.Char(compute="_get_ingredient_search_string", string="Ingredient name", store="True")
    alternate_product_ids = fields.Many2many(compute='_compute_alternate_product_ids',store=True)
