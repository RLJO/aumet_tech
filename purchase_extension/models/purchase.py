from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def fast_track(self):
        if self.state != "purchase":
            self.button_confirm()

        picking_ids = self.mapped('picking_ids')
        for picking_id in picking_ids:

            picking_id.action_confirm()

            for pack in picking_id.move_line_ids:
                if pack.product_qty > 0:
                    pack.write({'qty_done': pack.product_qty})
                else:
                    pack.unlink()
            picking_id.button_validate()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    is_expiration_required = fields.Boolean('is_expiration_required', defualt=False)
    expiration_date = fields.Datetime('Expiration Date', copy=True)
    price_unit = fields.Float(string='Cost', required=True, digits='Product Price')

    @api.onchange('expiration_date')
    def expiration_date_strp_time(self):
        if self.expiration_date:
            self.expiration_date = self.expiration_date.replace(hour=00, minute=59, second=59)

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(PurchaseOrderLine, self).onchange_product_id()
        if self.product_id.tracking == 'lot':
            self.is_expiration_required = True


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    extend_lot_name = fields.Char(
        'Lot/Serial Number', default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'), )
    expiration_date = fields.Datetime('Expiration Date',
                                      related='move_id.purchase_line_id.expiration_date', copy=False)

    # def _create_and_assign_production_lot(self):
    #     """ Creates and assign new production lots for move lines."""
    #     lot_vals = []
    #     for ml in self:
    #         if ml.expiration_date:
    #             ml.expiration_date = ml.expiration_date.replace(hour=2, minute=0, second=0)
    #             lot_id = self.env['stock.production.lot'].search([
    #                 ('company_id', '=', ml.company_id.id),
    #                 ('product_id', '=', ml.product_id.id),
    #                 ('expiration_date', '>=', str(ml.expiration_date.date()) + ' 00:00:00'),
    #                 ('expiration_date', '<=', str(ml.expiration_date.date()) + ' 23:59:59')], limit=1)
    #             if not lot_id:
    #                 lot_vals_dict = {
    #                     'company_id': ml.move_id.company_id.id,
    #                     'name': ml.extend_lot_name,
    #                     'product_id': ml.product_id.id,
    #                     'expiration_date': ml.expiration_date
    #                 }
    #                 lot_id = self.env['stock.production.lot'].create([lot_vals_dict])[0]
    #             ml._assign_production_lot(lot_id)
    #
    #         else:
    #             lot_id = self.env['stock.production.lot'].search([
    #                 ('company_id', '=', ml.company_id.id),
    #                 ('product_id', '=', ml.product_id.id),
    #                 ('expiration_date', '=', False)], limit=1)
    #             if not lot_id:
    #                 lot_vals_dict = {
    #                     'company_id': ml.move_id.company_id.id,
    #                     'name': ml.extend_lot_name,
    #                     'product_id': ml.product_id.id,
    #                 }
    #                 lot_id = self.env['stock.production.lot'].create([lot_vals_dict])[0]
    #             ml._assign_production_lot(lot_id)


class Picking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(
                float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(
                float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line
                in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(
                        lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if line.extend_lot_name:
                        line.lot_name = line.extend_lot_name
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(
                    products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(
                    pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _(
                    '\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(
                    pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        return True
