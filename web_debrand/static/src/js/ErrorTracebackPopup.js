odoo.define('web_debrand.ErrorTracebackPopup', function(require) {
    'use strict';

    const ErrorTracebackPopup = require('point_of_sale.ErrorTracebackPopup');
    const Registries = require('point_of_sale.Registries');

    ErrorTracebackPopup.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: 'Validation with Traceback',
        body: '',
        exitButtonIsShown: false,
        exitButtonText: 'Exit Pos',
        exitButtonTrigger: 'close-pos'
    };

    Registries.Component.add(ErrorTracebackPopup);
    return ErrorTracebackPopup;
});
