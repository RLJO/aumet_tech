from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Inventory(models.Model):
    _inherit = "stock.inventory"

    def _default_picking_type_id(self):
        context = self.env.context
        pick_in = False
        if 'default_page_type' in context:
            if context['default_page_type'] == 'In':
                pick_in = self.env.ref('stock.picking_type_in', raise_if_not_found=False)
                company = self.env.company
                if not pick_in or pick_in.sudo().warehouse_id.company_id.id != company.id:
                    pick_in = self.env['stock.picking.type'].search(
                        [('warehouse_id.company_id', '=', company.id), ('code', '=', 'incoming')],
                        limit=1,
                    )
            elif context['default_page_type'] == 'Out':
                pick_in = self.env.ref('stock.picking_type_out', raise_if_not_found=False)
                company = self.env.company
                if not pick_in or pick_in.sudo().warehouse_id.company_id.id != company.id:
                    pick_in = self.env['stock.picking.type'].search(
                        [('warehouse_id.company_id', '=', company.id), ('code', '=', 'outgoing')],
                        limit=1,
                    )
        return pick_in

    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', readonly=True, check_company=True,
                                      states={'draft': [('readonly', False)]},
                                      default=_default_picking_type_id)
    page_type = fields.Selection([('Out', 'Out'), ('In', 'In')], string='Type',
                                 readonly=True,
                                 states={'draft': [('readonly', False)]}, )
    total_sales = fields.Float('Total Price Sale', compute='_compute_total_sales')
    total_cost = fields.Float('Total Cost', compute='_compute_total_sales')

    def _compute_total_sales(self):
        for inv in self:
            total_sales = 0
            total_cost = 0
            for l in inv.line_ids:
                qty = l.product_qty - l.theoretical_qty
                if l.product_id.uom_id.id != l.product_uom_id.id:
                    qty = l.product_uom_id._compute_quantity(qty, l.product_id.uom_id)
                total_sales += (l.sale_price or l.product_id.lst_price) * abs(qty)
                total_cost += (l.cost or l.product_id.standard_price) * abs(qty)
            inv.total_sales = total_sales
            inv.total_cost = total_cost

    @api.onchange('picking_type_id')
    def on_cahnge_picking_type_id(self):
        if self.picking_type_id and self.page_type == 'In':
            self.op_location_id = self.picking_type_id.default_location_dest_id.id
        elif self.picking_type_id and self.page_type == 'Out':
            self.op_location_id = self.picking_type_id.default_location_src_id.id

    op_location_id = fields.Many2one(
        'stock.location', string='Location',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit'])]")

    @api.onchange('op_location_id')
    def on_cahnge_op_location(self):
        if self.op_location_id:
            self.location_ids = [(6, 0, [self.op_location_id.id])]
        else:
            self.location_ids = [(6, 0, [])]

    @api.model
    def create(self, vals):
        res = super(Inventory, self).create(vals)
        if res.op_location_id:
            res.action_start()
        return res

    def action_start(self):
        self.ensure_one()
        if not self.op_location_id:
            self._action_start()
            self._check_company()
            return self.action_open_inventory_lines()
        self.state = 'confirm'

    def action_validate(self):
        if not self.user_has_groups(
                'aumet_inventory.stock_validate_inventory_adjustment_in_out') and self.page_type == 'In':
            raise UserError(_("You don't have Permission to validate this operation"))
        elif not self.user_has_groups(
                'aumet_inventory.stock_validate_inventory_adjustment_in_out') and self.page_type == 'Out':
            raise UserError(_("You don't have Permission to validate this operation"))

        elif not self.user_has_groups('aumet_inventory.stock_validate_inventory_adjustment') and self.page_type not in [
            'In', 'Out']:
            raise UserError(_("You don't have Permission to validate this operation"))


        if self.page_type == 'In' or (self.page_type != 'Out' and self.op_location_id):
            for l in self.line_ids:
                if l.cost == 0 and l.product_id.standard_price == 0:
                    raise UserError(_('Cost cannot be zero, please update the cost on product itself or in line below '
                                      'for : %s.') % (l.product_id.name,))

        res = super(Inventory, self).action_validate()
        for l in self.line_ids:
            if l.sale_price:
                if l.product_id.lst_price != l.sale_price:
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
            nomenclature_id = self.env['barcode.nomenclature'].search([('is_gs1_nomenclature', '=', True)], limit=1)
            if nomenclature_id.exists():
                inventory['nomenclature_id'] = [nomenclature_id.id]
            elif self.env.company.nomenclature_id:
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
                'op_location_id': default_location_id.id,
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


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    expiration_date = fields.Date('Expiration Date', compute='_lot_expiration_date', inverse='_set_expiration_date')
    qty = fields.Float("Qty")

    @api.onchange('qty')
    def onchange_qty(self):
        if self.inventory_id.page_type == 'In':
            self.product_qty = self.theoretical_qty + self.qty
        elif self.inventory_id.page_type == 'Out':
            self.product_qty = self.theoretical_qty - self.qty

    def _get_virtual_location(self):
        if self.inventory_id.page_type == 'Out':
            return self.product_id.with_company(self.company_id).property_stock_inventory_out
        elif self.inventory_id.page_type == 'In':
            return self.product_id.with_company(self.company_id).property_stock_inventory_in

        return self.product_id.with_company(self.company_id).property_stock_inventory

    @api.depends('prod_lot_id')
    def _lot_expiration_date(self):
        for line in self:
            line.expiration_date = line.prod_lot_id.expiration_date

    @api.depends('expiration_date')
    def _set_expiration_date(self):
        if self.product_tracking == 'lot':
            if not self.expiration_date:
                raise UserError(_('Please make sure the expiry date has been set.'))
            lot_id = self.env['stock.production.lot'].search([
                ('company_id', '=', self.company_id.id),
                ('product_id', '=', self.product_id.id),
                ('expiration_date', '>=', str(self.expiration_date) + ' 00:00:00'),
                ('expiration_date', '<=', str(self.expiration_date) + ' 23:59:59')
            ], limit=1)
            if not lot_id:
                lot_vals_dict = {
                    'company_id': self.company_id.id,
                    'name': self.env['ir.sequence'].next_by_code('stock.lot.serial'),
                    'product_id': self.product_id.id,
                    'expiration_date': self.expiration_date if self.expiration_date else False,
                }
                lot_id = self.env['stock.production.lot'].create(lot_vals_dict)
            self.prod_lot_id = lot_id.id

    product_qty = fields.Float(
        'Counted Quantity',
        readonly=False, states={'confirm': [('readonly', False)]},
        digits='Product Unit of Measure', default=0)
    dummy_id = fields.Char(compute='_compute_dummy_id', inverse='_inverse_dummy_id')
    sale_price = fields.Float("Unit Sale Price", digits=(16, 3))
    cost = fields.Float("Unit Cost", digits=(16, 3))

    @api.onchange('sale_price')
    def onchange_sp(self):
        if not self.product_id.standard_price:
            if self.sale_price:
                self.cost = self.sale_price * 0.793
            else:
                self.cost = 0.0

    def _compute_dummy_id(self):
        self.dummy_id = ''

    def _inverse_dummy_id(self):
        pass

    @api.model
    def create(self, vals):
        return super(InventoryLine, self).create(vals)

    def write(self, vals):
        return super(InventoryLine, self).write(vals)

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

                if line.inventory_id.op_location_id and (line.inventory_id.page_type not in ['Out', 'In']):
                    existings = False

                if existings:
                    raise UserError(
                        _("There is already one inventory adjustment line for this product, (" + line.product_id.name +
                          ") you should rather modify this one instead of creating a new one."))

    @api.onchange('product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'partner_id', 'package_id')
    def _onchange_quantity_context(self):
        super(InventoryLine, self)._onchange_quantity_context()
        self.sale_price = self.product_id.lst_price
        if self.product_id.standard_price:
            self.cost = self.product_id.standard_price
        else:
            self.cost = self.product_id.lst_price * 0.793
        if self.inventory_id.op_location_id.id:
            self.location_id = self.inventory_id.op_location_id.id

    def _get_move_values(self, qty, location_id, location_dest_id, out):
        res = super(InventoryLine, self)._get_move_values(qty, location_id, location_dest_id, out)
        if self.inventory_id.page_type != 'Out':
            res['inventory_adjustment_cost'] = self.cost
        return res
