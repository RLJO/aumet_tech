/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

odoo.define('pos_insurance_payment.models', function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var SuperOrder = models.Order.prototype;
    const {patch} = require('web.utils');
    const ClientDetailsEdit = require('point_of_sale.ClientDetailsEdit');

    models.load_fields('res.partner', ['insurance_company', 'is_company', 'hi_percentage', 'member_number', 'under_insurance', 'total_credit', 'is_insurance']);

    patch(ClientDetailsEdit, 'pos_insurance_payment', {
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
            this.form_number = '';
        },
        export_as_JSON: function () {
            var order_json = SuperOrder.export_as_JSON.call(this);
            order_json.form_number = this.form_number;
            return order_json;
        },
        add_paymentline: function (payment_method) {
            var newPaymentline = SuperOrder.add_paymentline.call(this, payment_method);
            var client = this.get('client');
            var deactivate_insurance = $('#deactivate_insurance').is(":checked")

            if (client && client.hi_percentage >= 0 && !deactivate_insurance) {
                if (client.insurance_company) {
                    var new_amount = parseFloat((this.get_total_with_tax() * parseInt(client.hi_percentage)) / 100.0);
                    newPaymentline.set_amount(new_amount);
                    if (this.pos.config.cash_rounding) {
                        this.selected_paymentline.set_amount(0);
                        this.selected_paymentline.set_amount(new_amount);
                    }
                } else {
                    alert("Insurance Company not set for this client")
                }
            }
            return newPaymentline;
        },
    });
});
