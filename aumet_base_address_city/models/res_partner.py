from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'
    city_id = fields.Many2one('res.city', string='City', required=True)
