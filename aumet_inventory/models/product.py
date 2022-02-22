from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class Product(models.Model):
    _inherit = "product.template"

    property_stock_inventory_in = fields.Many2one(
        'stock.location', "In - Inventory Location",
        company_dependent=True, check_company=True,
        domain="[('usage', '=', 'inventory'), '|', ('company_id', '=', False), ('company_id', '=', "
               "allowed_company_ids[0])]",
        help="This stock location will be used, instead of the default one, as the source location for stock moves "
             "generated when you do an IN inventory.")

    property_stock_inventory_out = fields.Many2one(
        'stock.location', "Out - Inventory Location",
        company_dependent=True, check_company=True,
        domain="[('usage', '=', 'inventory'), '|', ('company_id', '=', False), ('company_id', '=', "
               "allowed_company_ids[0])]",
        help="This stock location will be used, instead of the default one, as the source location for stock moves "
             "generated when you do an OUT inventory.")

    strength = fields.Char('Strength')
    doesage_form = fields.Char('Dosage Form')
    granular_unit = fields.Char('Granular Unit')
    manufacturer = fields.Char('Manufacture')
    roa = fields.Char('ROA')
    package_type = fields.Char('Package Type')
    package_size = fields.Char('Package Size')

    @api.model
    def default_get(self, fields):
        defaults = super(Product, self).default_get(fields)
        defaults['type'] = 'product'
        defaults['tracking'] = 'lot'
        defaults['use_expiration_date'] = 'True'
        defaults['available_in_pos'] = 'True'
        return defaults

    @api.constrains("standard_price")
    def _check_cost(self):
        for record in self:
            if record.standard_price == 0:
                raise ValidationError(_("Cost can't be zero"))


class ProductProduct(models.Model):
    _inherit = "product.product"

    granular_unit = fields.Char('Granular Unit')
    manufacturer = fields.Char('Manufacture')
    roa = fields.Char('ROA')
    package_type = fields.Char('Package Type')
    package_size = fields.Char('Package Size')
