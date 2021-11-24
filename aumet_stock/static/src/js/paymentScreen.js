odoo.define("pos_payment_aumet.pos", function (require) {
    "use strict";

    var core = require('web.core');
    const {Gui} = require('point_of_sale.Gui');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    var models = require("point_of_sale.models");
    var _t = core._t;

    models.load_fields('product.product', ['name', 'type', 'qty_available', 'allow_negative_stock']);
    var _super_paymentScreen = PaymentScreen.prototype;

    const PosValPaymentScreen = PaymentScreen => class extends PaymentScreen {
        async _isOrderValid(isForceValidate) {
            var order = this.env.pos.get_order();
            var res = _super_paymentScreen._isOrderValid.apply(this, arguments);
            if (!res)
                return res;
            const result = await this.rpc({
                model: 'pos.order',
                method: 'check_negative',
                args: [order.export_as_JSON()],
            });
            result.forEach((line) => {
                if (line['negative'] === true) {
                    Gui.showPopup('ErrorPopup', {
                        title: _t('Negative quantity detected!'),
                        body: _.str.sprintf(_t("You cannot validate this stock operation because the " +
                            "stock level of the product '%s' would become negative " +
                            "and negative stock is not allowed for this product "), line.product_name),
                    });
                    res = false;
                }
            });
            return res
        }
    };

    Registries.Component.extend(PaymentScreen, PosValPaymentScreen);
    return PaymentScreen;

});