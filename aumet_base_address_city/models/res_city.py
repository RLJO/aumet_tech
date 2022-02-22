# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class City(models.Model):
    _inherit = 'res.city'

    province_id = fields.Many2one('aumet_base_address_city_province', string='Provinces', required=True, index=True)


class Province(models.Model):
    _name = 'aumet_base_address_city_province'
    _description = 'Province'
    _order = 'name'
    name = fields.Char("Name", required=True, translate=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)


class District(models.Model):
    _name = 'aumet_base_address_city_district'
    _description = 'District'
    _order = 'name'

    name = fields.Char("Name", required=True, translate=True)
    city_id = fields.Many2one('res.city', string='City', required=True, index=True)

