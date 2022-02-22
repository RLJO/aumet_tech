# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import http
from odoo.http import request
from odoo.addons.bus.controllers.main import BusController
from odoo.addons.web.controllers.main import Home


class ModuleController(http.Controller):

    @http.route("/aumet/reporting/main", auth="public", type="json", csrf=False, method=['GET'])
    def get_pos_session_summary(self):
        pos_session_data = {}
        try:
            last_session = request.env['pos.session'].sudo().search([('state', 'in', ['closed', 'opened'])],
                                                                    order='create_date desc', limit=1)

            last_purchase_order = request.env['purchase.order'].sudo().search([],
                                                                              order='create_date desc', limit=1)
            last_stock_operation = request.env['stock.inventory'].sudo().search([],
                                                                                order='create_date desc', limit=1)
            last_b2b_order = request.env['sale.order'].sudo().search([],
                                                                     order='create_date desc', limit=1)
            last_pos_order = request.env['pos.order'].sudo().search([],
                                                                    order='create_date desc', limit=1)
            operations = {}

            if last_purchase_order:
                operations.update({last_purchase_order.create_date.timestamp(): last_purchase_order})
            if last_stock_operation:
                operations.update({last_stock_operation.create_date.timestamp(): last_stock_operation})
            if last_b2b_order:
                operations.update({last_b2b_order.create_date.timestamp(): last_b2b_order})
            if last_pos_order:
                operations.update({last_pos_order.create_date.timestamp(): last_pos_order})
            if operations:
                last_operation = max((operation for operation in operations.keys()))

                pos_session_data.update(
                    {'last_operation_date': operations[last_operation].create_date.strftime('%d/%m/%Y %H:%M'),
                     'last_operation_source': operations[last_operation].name})
            else:
                pos_session_data.update(
                    {'last_operation_date': '', 'last_operation_source': ''})

            if last_session:
                order_count = request.env['pos.order'].sudo().search_count(
                    [('session_id', '=', last_session.id)])
                order_total = sum(
                    request.env['pos.order'].sudo().search([('session_id', '=', last_session.id)]).mapped(
                        'amount_total'))
                pos_session_data.update(
                    {'last_session_start_date': last_session.start_at.strftime('%d/%m/%Y %H:%M'),
                     'last_session_status': last_session.state,
                     'last_session_order_count': order_count,
                     'last_session_order_total': order_total})
            return {'response_code': 200, 'data': str(pos_session_data)}
        except Exception as e:
            return {'response_code': 500, 'desc': str(e)}

    @http.route("/aumet/update/modules", auth="user", type="json", csrf=False, method=['GET'])
    def update_modules(self):
        try:
            base_module = request.env["base.module.update"].create({
                "state": "init",
                "updated": True,
                "added": True
            })
            if base_module:
                base_module.update_module()
                return {'response_code': 200, 'desc': 'success'}
            return {'response_code': 400, 'desc': 'does not update any module'}
        except Exception as e:
            return {'response_code': 500, 'desc': str(e)}

    @http.route('/aumet/module/control', auth='user', type='json', csrf=False, method=['GET'])
    def uninstall_parameter_module(self, **kw):
        module_names = kw.get('module_name', False)
        action_to_take = kw.get('action_type', False)
        try:
            module_object = request.env['ir.module.module'].search([('name', 'in', module_names)])
            if action_to_take == 'install':
                module_object.sudo(1).button_immediate_install()
                res = {'response_code': 200, 'desc': 'success'}
            elif action_to_take == 'upgrade':
                module_object.sudo(1).button_immediate_upgrade()
                res = {'response_code': 200, 'desc': 'success'}
            elif action_to_take == 'uninstall':
                module_object.sudo(1).button_immediate_uninstall()
                res = {'response_code': 200, 'desc': 'success'}
            else:
                res = {'response_code': 400, 'desc': 'invalid syntax'}
        except Exception as e:
            res = {'response_code': 500, 'desc': str(e)}
        return res


class Home(Home):

    def _login_redirect(self, uid, redirect=None):
        user_id = request.env['res.users'].sudo().browse(uid)
        if user_id.is_pos_direct_login and user_id.default_pos_id:
            pos_session = request.env['pos.session'].sudo().search(
                [('config_id', '=', user_id.default_pos_id.id), ('state', '=', 'opening_control')])
            if not pos_session:
                if user_id.default_pos_id.cash_control:
                    pos_session.write({'opening_balance': True})
                    pos_session.action_pos_session_open()
                session_id = user_id.default_pos_id.open_session_cb()
            redirect = '/pos/ui?config_id=' + str(user_id.default_pos_id.id)
        return super(Home, self)._login_redirect(uid, redirect=redirect)


class CustomerDisplayController(BusController):

    def _poll(self, dbname, channels, last, options):
        """Add the relevant channels to the BusController polling."""
        if options.get('customer.display'):
            channels = list(channels)
            ticket_channel = (
                request.db,
                'customer.display',
                options.get('customer.display')
            )
            channels.append(ticket_channel)
        return super(CustomerDisplayController, self)._poll(dbname, channels, last, options)


class PosMirrorController(http.Controller):

    @http.route('/web/customer_display', type='http', auth='user')
    def white_board_web(self, **k):
        config_id = False
        pos_sessions = request.env['pos.session'].search([
            ('state', '=', 'opened'),
            ('user_id', '=', request.session.uid),
            ('rescue', '=', False)])
        if pos_sessions:
            config_id = pos_sessions.config_id.id
        session_info = request.env['ir.http'].session_info()
        context = {
            'session_info': session_info,
            'config_id': config_id,
        }
        return request.render('flexipharmacy.index', qcontext=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
