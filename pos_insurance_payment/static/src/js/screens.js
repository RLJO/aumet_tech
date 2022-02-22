odoo.define('pos_insurance_payment.screens', function (require) {
    "use strict";
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const {useListener} = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    const PosResPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async validateOrder(isForceValidate) {
                var self = this;
                var order = self.env.pos.get_order();
                if (!self.env.pos.config.partial_payment) {
                    super.validateOrder(isForceValidate);
                    await this._finalizeValidation();
                } else {
                    order.invoice_remark = $('#partial_payment_description').val();
                    order.form_number = $('#form_number').val();
                    var deactivate_insurance = $('#deactivate_insurance')[0].checked;
                    if (!deactivate_insurance && !order.form_number) {
                        this.showPopup('ErrorPopup', {
                            'title': _t('Form Number Required'),
                            'body': _t('Please make sure to add the form number'),
                        });
                        return false;
                    }
                    if (!order.selected_paymentline) {
                        this.showPopup('ErrorPopup', {
                            'title': _t('Payment Line'),
                            'body': _t('You need to select payment line to validate this order'),
                        });
                        return false;
                    }
                    if (order.get_orderlines().length === 0) {
                        this.showPopup('ErrorPopup', {
                            'title': _t('Empty Order'),
                            'body': _t('There must be at least one product in your order before it can be validated'),
                        });
                        return false;
                    } else {
                        if (!order.is_paid() && !order.is_to_invoice()) {
                            self.showPopup('WkPPAlertPopUp', {
                                'title': _t('Cannot Validate This Order!!!'),
                                'body': _t("You need to set Invoice for validating Partial Payments."),
                            });
                            return;
                        }
                        if (this.currentOrder.is_to_invoice() && !this.currentOrder.get_client()) {
                            self.showPopup('WkPPAlertPopUp', {
                                'title': _t('Select the Customer'),
                                'body': _t("You need to select the customer before you can invoice an order."),
                            });
                            return false;
                        }
                        if (order.is_to_invoice()) {
                            if (order.get_client() != null && order.get_due() > 0) {
                                if (order.get_client().prevent_partial_payment) {
                                    self.showPopup('WkPPAlertPopUp', {
                                        'title': _t('Cannot Validate This Order!!!'),
                                        'body': _t("Customer's Payment Term does not allow Partial Payments."),
                                    });
                                    return false;
                                }
                            }
                            order.is_partially_paid = true;

                            if ($('#partial_payment_description').val() == '') {
                                $("#partial_payment_description").css("background-color", "burlywood");
                                setTimeout(function () {
                                    $("#partial_payment_description").css("background-color", "");
                                }, 100);
                                setTimeout(function () {
                                    $("#partial_payment_description").css("background-color", "burlywood");
                                }, 200);
                                setTimeout(function () {
                                    $("#partial_payment_description").css("background-color", "");
                                }, 300);
                                setTimeout(function () {
                                    $("#partial_payment_description").css("background-color", "burlywood");
                                }, 400);
                                setTimeout(function () {
                                    $("#partial_payment_description").css("background-color", "");
                                }, 500);
                                return;
                            }

                        }
                    }
                    if (await this._isOrderValid(isForceValidate)) {
                        // remove pending payments before finalizing the validation
                        for (let line of this.paymentLines) {
                            if (!line.is_done()) this.currentOrder.remove_paymentline(line);
                        }
                        await this._finalizeValidation();
                    }
                }

            }

        }
    Registries.Component.extend(PaymentScreen, PosResPaymentScreen);

    return PaymentScreen;

});