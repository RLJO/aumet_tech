/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('wk_pos_partial_payment.models', function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var SuperOrder = models.Order.prototype;
    const {patch} = require('web.utils');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');

    models.load_fields('res.partner', ['property_payment_term_id', 'prevent_partial_payment',
        'parent_id', 'is_company', 'hi_percentage', 'member_number', 'under_insurance']);

    patch(ClientDetailsEdit, 'wk_pos_partial_payment', {
        captureChange(event) {
            this._super(event);
            if (event.target.type === 'checkbox') {
                this.changes[event.target.name] = event.currentTarget.checked;
            }
        }
    });

    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            SuperOrder.initialize.call(this, attributes, options);
            this.invoice_remark = '';
            this.form_number = '';
            this.is_partially_paid = false;
        },
        export_as_JSON: function () {
            var order_json = SuperOrder.export_as_JSON.call(this);
            order_json.invoice_remark = this.invoice_remark;
            order_json.form_number = this.form_number;
            order_json.is_partially_paid = this.is_partially_paid;
            return order_json;
        },
        add_paymentline: function (payment_method) {
            var newPaymentline = SuperOrder.add_paymentline.call(this, payment_method);
            var client = this.get('client');

            var deactivate_insurance = $('#deactivate_insurance').is(":checked")
            // if (deactivate_insurance) {
            //     $('.partial-payment-remark').hide();
            // }
            if (client && client.hi_percentage > 0 && !deactivate_insurance) {
                var new_amount = parseFloat((this.get_total_with_tax() * parseInt(client.hi_percentage)) / 100.0);
                newPaymentline.set_amount(new_amount);
                if (this.pos.config.cash_rounding) {
                    this.selected_paymentline.set_amount(0);
                    this.selected_paymentline.set_amount(new_amount);
                }
            }
            return newPaymentline;
        },
    });
});
