# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class Company(models.Model):
    _inherit = 'res.company'

    city_id = fields.Many2one('res.city', string='City', required=True)
    province_id = fields.Many2one('aumet_base_address_city_province', string='Province', required=True)
    district_id = fields.Many2one('aumet_base_address_city_district', string='District', required=True)
    name_sdr = fields.Char('SDR', required=True)
    customer_success = fields.Char('Customer Success', required=True)



