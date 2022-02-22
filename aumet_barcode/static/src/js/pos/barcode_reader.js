odoo.define('aumet_barcode.BarcodeReader', function (require) {
    "use strict";
    const BarcodeReader = require('point_of_sale.BarcodeReader');
    BarcodeReader.include({

        scan: async function (code) {
            if (!code) return;

            const callbacks = Object.keys(this.exclusive_callbacks).length
                ? this.exclusive_callbacks
                : this.action_callbacks;
            let parsed_results = this.barcode_parser.parse_barcode(code);

            if (!Array.isArray(parsed_results)) {
                parsed_results = [parsed_results];
            }
            for (const parsed_result of parsed_results) {
                if (parsed_result.type !== 'product') {
                    continue
                }
                if (callbacks[parsed_result.type]) {
                    for (const cb of callbacks[parsed_result.type]) {
                        await cb(parsed_result);
                    }
                } else if (callbacks.error) {
                    [...callbacks.error].map(cb => cb(parsed_result));
                } else {
                    console.warn('Ignored Barcode Scan:', parsed_result);
                }
            }
        },
    });
    return BarcodeReader;
});