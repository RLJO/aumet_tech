# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    # @api.model
    # def _default_loc(self):
    #     if self.inventory_id:
    #         return self.inventory_id.location_ids[0].id
    #     return 8

    product_qty = fields.Float(
        'Counted Quantity',
        readonly=False, states={'confirm': [('readonly', False)]},
        digits='Product Unit of Measure', default=0)
    dummy_id = fields.Char(compute='_compute_dummy_id', inverse='_inverse_dummy_id')
    sale_price = fields.Float("Sale Price")
    # default_location_id = fields.Many2one('stock.location', default=_default_loc)

    location_id = fields.Many2one(
        'stock.location', 'Location', check_company=True,
        domain=lambda self: self._domain_location_id(),
        index=True, required=True, default=8)

    def _compute_dummy_id(self):
        self.dummy_id = ''

    def _inverse_dummy_id(self):
        pass

    @api.model
    def create(self, vals):
        return super(StockInventoryLine, self).create(vals)

    def write(self, vals):
        return super(StockInventoryLine, self).write(vals)

    def _check_no_duplicate_line(self):
        ctx = (self.env.context)
        if not ctx.get('pass', False):
            for line in self:
                domain = [
                    ('id', '!=', line.id),
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.location_id.id),
                    ('partner_id', '=', line.partner_id.id),
                    ('package_id', '=', line.package_id.id),
                    ('prod_lot_id', '=', line.prod_lot_id.id),
                    ('inventory_id', '=', line.inventory_id.id)]
                existings = self.search(domain)
                if ctx.get('form_view_ref', '') == 'stock_barcode.stock_inventory_line_barcode':
                    existings = False

                if existings:
                    raise UserError(_("There is already one inventory adjustment line for this product,"
                                      " you should rather modify this one instead of creating a new one."))

    @api.onchange('product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'partner_id', 'package_id')
    def _onchange_quantity_context(self):
        super(StockInventoryLine, self)._onchange_quantity_context()
        self.sale_price = self.product_id.lst_price

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def action_validate(self):
        res = super(StockInventory, self).action_validate()
        for l in self.line_ids:
            if l.sale_price:
                l.product_id.lst_price = l.sale_price
        return res

    def action_client_action(self):
        """ Open the mobile view specialized in handling barcodes on mobile devices.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.client',
            'tag': 'stock_barcode_inventory_client_action',
            'target': 'fullscreen',
            'params': {
                'model': 'stock.inventory',
                'inventory_id': self.id,
            }
        }

    def get_barcode_view_state(self):
        """ Return the initial state of the barcode view as a dict.
        """
        inventories = self.read([
            'line_ids',
            'location_ids',
            'name',
            'state',
            'company_id',
        ])
        for inventory in inventories:
            inventory['line_ids'] = self.env['stock.inventory.line'].browse(inventory.pop('line_ids')).read([
                'product_id',
                'location_id',
                'product_qty',
                'theoretical_qty',
                'product_uom_id',
                'prod_lot_id',
                'package_id',
                'dummy_id',
                'expiration_date',
                'sale_price',
            ])

            # Prefetch data
            location_ids = list(set([line_id["location_id"][0] for line_id in inventory['line_ids']]))
            product_ids = list(set([line_id["product_id"][0] for line_id in inventory['line_ids']]))

            parent_path_per_location_id = {}
            for res in self.env['stock.location'].search_read([('id', 'in', location_ids)], ['parent_path']):
                parent_path_per_location_id[res.pop("id")] = res

            tracking_and_barcode_per_product_id = {}
            for res in self.env['product.product'].with_context(active_test=False).search_read(
                    [('id', 'in', product_ids)], ['tracking', 'barcode']):
                tracking_and_barcode_per_product_id[res.pop("id")] = res

            for line_id in inventory['line_ids']:
                id, name = line_id.pop('product_id')
                line_id['product_id'] = {"id": id, "display_name": name, **tracking_and_barcode_per_product_id[id]}
                id, name = line_id.pop('location_id')
                line_id['location_id'] = {"id": id, "display_name": name, **parent_path_per_location_id[id]}
            inventory['location_ids'] = self.env['stock.location'].browse(inventory.pop('location_ids')).read([
                'id',
                'display_name',
                'parent_path',
            ])
            inventory['group_stock_multi_locations'] = self.env.user.has_group('stock.group_stock_multi_locations')
            inventory['group_tracking_owner'] = self.env.user.has_group('stock.group_tracking_owner')
            inventory['group_tracking_lot'] = self.env.user.has_group('stock.group_tracking_lot')
            inventory['group_production_lot'] = self.env.user.has_group('stock.group_production_lot')
            inventory['group_uom'] = self.env.user.has_group('uom.group_uom')
            inventory['actionReportInventory'] = self.env.ref('stock.action_report_inventory').id
            if self.env.company.nomenclature_id:
                inventory['nomenclature_id'] = [self.env.company.nomenclature_id.id]
            if not inventory['location_ids'] and not inventory['line_ids']:
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.company.id)], limit=1)
                inventory['location_ids'] = warehouse.lot_stock_id.read(['id', 'display_name', 'parent_path'])
        return inventories

    @api.model
    def open_new_inventory(self):
        company_user = self.env.company
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
        if warehouse:
            default_location_id = warehouse.lot_stock_id
        else:
            raise UserError(_('You must define a warehouse for the company: %s.') % (company_user.name,))

        action = self.env['ir.actions.client']._for_xml_id('stock_barcode.stock_barcode_inventory_client_action')
        if self.env.ref('stock.warehouse0', raise_if_not_found=False):
            new_inv = self.env['stock.inventory'].create({
                'start_empty': True,
                'name': fields.Date.context_today(self),
                'location_ids': [(4, default_location_id.id, None)],
            })
            new_inv.action_start()
            action['res_id'] = new_inv.id

            params = {
                'model': 'stock.inventory',
                'inventory_id': new_inv.id,
            }
            action['context'] = {'active_id': new_inv.id}
            action = dict(action, params=params)

        return action
