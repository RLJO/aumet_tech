# -*- coding: utf-8 -*-
from odoo import models, fields, _, api
from odoo.exceptions import UserError
import time


class ProductMovesWizard(models.TransientModel):
    _name = "product.move.wizard"
    _description = 'Product Moves Wizard Report'

    @api.model
    def _get_product_var(self):
        if self._context and 'active_model' in self._context and self._context['active_model'] == 'product.product':
            return self._context['active_id']

        if self._context and 'active_model' in self._context and self._context['active_model'] == 'product.template':
            varients = self.env['product.product'].search([('product_tmpl_id', '=', self._context['active_id'])])
            if len(varients) == 1:
                return varients

    @api.model
    def _get_product_tmpl(self):
        if self._context and 'active_model' in self._context and self._context['active_model'] == 'product.product':
            return self.env['product.product'].browse(self._context['active_id']).product_tmpl_id.id

        if self._context and 'active_model' in self._context and self._context['active_model'] == 'product.template':
            return self._context['active_id']

    def _set_cost_privileges(self):

        if self.env.ref('wh_enhancement_privileges.group_allow_product_cost', False):
            if self.env.user.has_group('wh_enhancement_privileges.group_allow_product_cost'):
                return True
            else:
                return False
        return True

    product_id = fields.Many2one('product.product', 'Product Variant', required=True, default=_get_product_var)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', default=_get_product_tmpl)
    date1 = fields.Date('From', default=lambda *a: time.strftime('%Y-%m-01'), required=True)
    date2 = fields.Date('To', default=lambda *a: time.strftime('%Y-%m-%d'), required=True)
    sort_on = fields.Selection([('date', 'Date')]
                               , 'Sort On', required=True, default='date')
    sort_type = fields.Selection([('desc', 'Descending'),
                                  ('asc', 'Ascending'), ]
                                 , 'Sort Type', required=True, default='asc')
    incl_init_balance = fields.Boolean("Include Initial Balance", default=True)
    location_id = fields.Many2one('stock.location', 'Location')
    orientation = fields.Selection([('landscape', 'Landscape'), ('Portrait', 'Portrait')], string="Orientation",
                                   default='Portrait')

    show_partner = fields.Boolean("Show Partner", default=True)
    show_lot = fields.Boolean("Show Lot/Serial")
    show_expiry_date = fields.Boolean("Show Expiry Date")
    show_origin = fields.Boolean("Show Origin", default=True)
    show_locations = fields.Boolean("Show Src/Dest Location", default=True)
    cost_privileges = fields.Boolean("Cost Privileges", default=_set_cost_privileges)
    show_cost_value = fields.Boolean("Show Cost/Value")

    def print_report(self):
        data = self.read()[0]
        # Check if date2 provided without date1, then show error message
        if data.get('date2', False) and not data.get('date1', False):
            raise UserError(_('Please provide From Date.'))

        datas = {
            'ids': self.product_id.id,
            'model': 'product.product',
            'form': data,
        }

        records = self.env[datas['model']].browse(datas.get('ids', []))
        return self.env.ref('aumet_product_moves_report.aumet_product_moves_report_action').with_context(landscape=True).report_action(records, data=datas)
