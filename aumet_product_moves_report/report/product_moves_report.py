# -*- coding: utf-8 -*-

import time
from odoo import api, models
from odoo.tools.misc import formatLang


class ProductMovesReport(models.AbstractModel):
    _name = 'report.aumet_product_moves_report.product_moves'
    _description = 'Product Moves Report'

    # final_balance = 0
    # final_cost_value = 0
    # comeInParent = 0
    # comeOutParent = 0

    def formatDigits(self, amount, digits=''):
        decimal_rec = self.env['decimal.precision'].search([('name', '=', digits)])
        if decimal_rec:
            digits = decimal_rec[0].digits
        else:
            digits = 2

        return formatLang(self.env, amount, digits=digits)

    def get_moves(self, date1, date2, prod_id, location_id, incl_init_balance=False, sort_type=False, sort_on=False):
        company_id = self.env.user.company_id.id
        stock_obj = self.env['stock.move']
        domain = [('product_id', '=', prod_id), ('state', '=', 'done'), ('company_id', '=', company_id)]
        if date1:
            domain.extend([('date_done', '>=', date1)])
        if date2:
            domain.extend([('date_done', '<=', date2)])
        if location_id:
            domain.extend(['|', ('location_id', '=', location_id[0]), ('location_dest_id', '=', location_id[0])])

        moves = stock_obj.search(domain, order=sort_on + " " + sort_type)

        init_values = self.get_initial_balance(date1, date2, prod_id, location_id, incl_init_balance, sort_type,
                                               sort_on)
        old_balance = init_values['i_balance']
        old_value = init_values['i_value']

        final_balance = 0
        final_cost_value = 0
        comeInParent = 0
        comeOutParent = 0
        comeIn = 0
        comeOut = 0
        amount = 0.0
        stock_move = []
        for move in moves:
            is_adj = False
            old_value += 0 # move.value
            type = ''
            partner_name = ''
            if move.picking_id:
                if move.picking_id.partner_id:
                    partner_name = move.picking_id.partner_id.name

            if move.product_uom.id != move.product_id.uom_id.id:
                amount = move.product_uom._compute_quantity(move.product_qty, move.product_id.uom_id)
            else:
                amount = move.product_qty

            if (move.picking_id.picking_type_id.code == "incoming"):
                move_type = 'Purchase'
                comeIn = amount
                old_balance += comeIn
                comeInParent += comeIn

            elif (move.picking_id.picking_type_id.code == "outgoing"):
                if move.location_dest_id.usage == 'internal':
                    move_type = 'Purchase'
                    comeIn = amount
                    old_balance += comeIn
                    comeInParent += comeIn
                else:
                    move_type = 'Sale'
                    comeOut = amount
                    old_balance -= comeOut
                    comeOutParent += comeOut


            elif (move.picking_id.picking_type_id.code == "internal" and move.location_dest_id.scrap_location):
                move_type = 'Sale'
                comeOut = amount
                old_balance -= comeOut
                comeOutParent += comeOut
            elif (move.picking_id.picking_type_id.code == "internal" and move.location_id.scrap_location):
                move_type = 'Purchase'
                comeIn = amount
                old_balance += comeIn
                comeInParent += comeIn
            elif (move.picking_id.picking_type_id.code == "internal"):
                move_type = "Internal"
                old_balance += 0
                comeInParent += 0

            elif (move.location_dest_id.usage == "inventory"):
                move_type = 'Sale'
                is_adj = True
                comeOut = amount
                old_balance -= comeOut
                comeOutParent += comeOut
            elif (move.location_id.usage == "inventory"):
                move_type = 'Purchase'
                is_adj = True
                comeIn = amount
                old_balance += comeIn
                comeInParent += comeIn

            elif (move.location_dest_id.usage == "internal" and move.location_dest_id.scrap_location):
                move_type = 'Sale'
                comeOut = amount
                old_balance -= comeOut
                comeOutParent += comeOut
            elif (move.location_id.usage == "internal" and move.location_id.scrap_location):
                move_type = 'Purchase'
                comeIn = amount
                old_balance += comeIn
                comeInParent += comeIn

            if location_id:
                if (move.picking_id.picking_type_id.code == "internal" and move.location_dest_id.id == location_id[0]):
                    move_type = "In"
                    comeIn = amount
                    old_balance += comeIn
                    comeInParent += comeIn
                elif (move.picking_id.picking_type_id.code == "internal" and move.location_id.id == location_id[0]):
                    move_type = "Out"
                    comeOut = amount
                    old_balance -= comeOut
                    comeOutParent += comeOut

            if move_type == 'incoming' or move_type == 'Purchase':
                move_type = 'Purchase'
            elif move_type == 'outgoing' or move_type == 'Sale':
                move_type = 'Sale'

            origin = move.origin or move.picking_id.name or 'Inv Adj'

            if not is_adj:
                if move_type == 'Purchase' and not move.purchase_line_id:
                    move_type = 'S.Refund'
                    if move.location_dest_id.usage == 'customer':
                        move_type = 'Sale'
                        old_balance -= amount
                        comeInParent -= amount
                        old_balance -= amount
                        comeOutParent += amount
                    elif move.location_id.usage == 'supplier':
                        move_type = 'Purchase'

                    origin = (move.origin if move.origin else '') + ' ' + (
                        move.picking_id.origin if move.picking_id.origin else '')

                elif move_type == 'Sale' and not move.sale_line_id:
                    move_type = 'P.Refund'
                    if move.location_dest_id.usage == 'customer':
                        move_type = 'Sale'

                    origin = (move.origin if move.origin else '') + ' ' + (
                        move.picking_id.origin if move.picking_id.origin else '')

            lot_numbers = ''
            lot_names = []
            move_lines = self.env['stock.move.line'].search([('move_id', '=', move.id)])
            expiry_date = ''
            for q in move_lines:
                if q.lot_name and q.lot_name not in lot_names:
                    lot_numbers += q.lot_name + '\n'
                    lot_names.append(q.lot_name)
                elif q.lot_id and q.lot_id.name not in lot_names:
                    lot_numbers += q.lot_id.name + '\n'
                    lot_names.append(q.lot_id.name)
                    if hasattr(q.lot_id, 'expiration_date'):
                        expiry_date = q.lot_id.expiration_date if q.lot_id.expiration_date else ''

            cost = move.price_unit
            move_line = {'date': move.date_done, 'origin': origin, 'picking_name': move.picking_id.name or move.name,
                         'type': move_type, 'partner_name': partner_name,
                         'location_name': move.location_id.name, 'des_name': move.location_dest_id.name,
                         'product_qty': move.product_qty, 'balance': old_balance,
                         'location_parent_name': move.location_id.location_id.name,
                         'des_parent_name': move.location_dest_id.location_id.name,
                         'expiry_date': expiry_date, 'cost': cost, 'is_adj': is_adj, 'lot_numbers': lot_numbers,
                         'value': old_value}
            stock_move.append(move_line)

        final_balance = init_values['i_balance'] + comeInParent - comeOutParent
        final_cost_value = old_value
        return stock_move

    def get_initial_balance(self, date1, date2, prod_id, location_id, incl_init_balance, sort_type, sort_on):
        # Exclude initial balance if incl_init_balance = False OR no dates provided.
        if (not incl_init_balance) or (not date1 and not date2):
            return {'i_balance': 0.0}

        company_id = self.env.user.company_id.id
        move_obj = self.env['stock.move']
        res = {'i_cost': 0.0, 'i_value': 0.0, 'i_balance': 0.0}
        domain = [('product_id', '=', prod_id), ('state', '=', 'done'), ('company_id', '=', company_id)]
        if date1:
            domain.extend([('date_done', '<', date1)])
        if location_id:
            domain.extend(['|', ('location_id', '=', location_id[0]), ('location_dest_id', '=', location_id[0])])

        moves = move_obj.search(domain, order=sort_on + " " + sort_type)

        comeIn = 0
        comeOut = 0
        prod_qty = 0.0
        i_value = 0.0
        for move in moves:
            i_value += 0 # move.value
            if move.product_uom.id != move.product_id.uom_id.id:
                prod_qty = move.product_uom._compute_quantity(move.product_qty, move.product_id.uom_id)
            else:
                prod_qty = move.product_qty

            if (move.picking_id.picking_type_id.code == "incoming"):
                comeIn += prod_qty
            elif (move.picking_id.picking_type_id.code == "outgoing"):
                if move.location_dest_id.usage == 'internal':
                    comeIn += prod_qty
                else:
                    comeOut += prod_qty
            elif (move.location_dest_id.usage == "inventory"):
                comeOut += prod_qty
            elif (move.location_id.usage == "inventory"):
                comeIn += prod_qty

            if location_id:
                if (move.picking_id.picking_type_id.code == "internal" and move.location_dest_id.id == location_id[0]):
                    comeIn += move.product_qty
                elif (move.picking_id.picking_type_id.code == "internal" and move.location_id.id == location_id[0]):
                    comeOut += move.product_qty

        res['i_balance'] = comeIn - comeOut
        res['i_value'] = i_value
        if (comeIn - comeOut) != 0:
            res['i_cost'] = i_value / (comeIn - comeOut)
        else:
            res['i_cost'] = i_value
        return res

    # def get_final_totals(self):
    #     return {'f_balance': final_balance, 'f_value': final_cost_value}

    @api.model
    def _get_report_values(self, docids, data=None):
        prod_ids = data['ids']
        docs = self.env['product.product'].browse(prod_ids)
        return {
            'doc_ids': [],
            'docs': docs,
            'doc_model': self.env['product.product'],
            'data': data,
            'time': time,
            'formatLang': self.formatDigits,
            'get_moves': self.get_moves,
            'get_initial_balance': self.get_initial_balance,
            # 'get_final_totals': self.get_final_totals,
        }
