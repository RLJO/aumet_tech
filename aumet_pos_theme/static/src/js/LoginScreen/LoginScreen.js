odoo.define('aumet_pos_theme.LoginScreen', function (require) {
    'use strict';

    const LoginScreen = require('pos_hr.LoginScreen');
    const Registries = require('point_of_sale.Registries');
    const rentalUseSelectEmployee = require('aumet_pos_theme.useSelectEmployee');

    const AsplRetLoginScreenInh = (LoginScreen) =>
        class extends LoginScreen {
            constructor() {
                super(...arguments);
                this.barcodeCashierAction = this._barcodeCashierAction;
                const {selectEmployee, askPin} = rentalUseSelectEmployee();
                this.selectEmployee = selectEmployee;
                this.askPin = askPin;
            }
        }

    Registries.Component.extend(LoginScreen, AsplRetLoginScreenInh);

    return LoginScreen;
});
