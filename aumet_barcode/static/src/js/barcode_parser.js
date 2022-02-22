odoo.define('aumet_barcode.BarcodeParser', function (require) {
    "use strict";

    const BarcodeParser = require('barcodes.BarcodeParser');
    const FNC1_CHAR = String.fromCharCode(29);
    const {_lt} = require('web.core');
    var rpc = require('web.rpc');

    BarcodeParser.include({
        init: function (attributes) {
            this._super.apply(this, arguments);
            this.nomenclature = attributes.nomenclature;
        },

        load: function () {
            if (!this.nomenclature_id) {
                return this.nomenclature ? Promise.resolve() : Promise.reject();
            }
            var id = this.nomenclature_id[0];
            return rpc.query({
                model: 'barcode.nomenclature',
                method: 'read',
                args: [[id], this._barcodeNomenclatureFields()],
            }).then(nomenclatures => {
                this.nomenclature = nomenclatures[0];
                var args = [
                    [['barcode_nomenclature_id', '=', this.nomenclature.id]],
                    this._barcodeRuleFields(),
                ];
                return rpc.query({
                    model: 'barcode.rule',
                    method: 'search_read',
                    args: args,
                });
            }).then(rules => {
                rules = rules.sort(function (a, b) {
                    return a.sequence - b.sequence;
                });
                this.nomenclature.rules = rules;
            });
        },

        /**
         * This algorithm is identical for all fixed length numeric GS1 data structures.
         *
         * It is also valid for EAN-8, EAN-12 (UPC-A), EAN-13 check digit after sanitizing.
         * https://www.gs1.org/sites/default/files/docs/barcodes/GS1_General_Specifications.pdf
         *
         * @param {String} numericBarcode Need to have a length of 18
         * @returns {number} Check Digit
         */
        get_barcode_check_digit(numericBarcode) {
            let oddsum = 0, evensum = 0, total = 0;
            // Reverses the barcode to be sure each digit will be in the right place
            // regardless the barcode length.
            const code = numericBarcode.split('').reverse();
            // Removes the last barcode digit (should not be took in account for its own computing).
            code.shift();

            // Multiply value of each position by
            // N1  N2  N3  N4  N5  N6  N7  N8  N9  N10 N11 N12 N13 N14 N15 N16 N17 N18
            // x3  X1  x3  x1  x3  x1  x3  x1  x3  x1  x3  x1  x3  x1  x3  x1  x3  CHECK_DIGIT
            for (let i = 0; i < code.length; i++) {
                if (i % 2 === 0) {
                    evensum += parseInt(code[i]);
                } else {
                    oddsum += parseInt(code[i]);
                }
            }
            total = evensum * 3 + oddsum;
            return (10 - total % 10) % 10;
        },

        /**
         * Checks if the barcode string is encoded with the provided encoding.
         *
         * @param {String} barcode
         * @param {String} encoding could be 'any' (no encoding rules), 'ean8', 'upca' or 'ean13'
         * @returns {boolean}
         */
        check_encoding: function (barcode, encoding) {
            if (encoding === 'any') {
                return true;
            }
            const barcodeSizes = {
                ean8: 8,
                ean13: 13,
                upca: 12,
            };
            return barcode.length === barcodeSizes[encoding] && /^\d+$/.test(barcode) &&
                this.get_barcode_check_digit(barcode) === parseInt(barcode[barcode.length - 1]);
        },

        /**
         * Sanitizes a EAN-13 prefix by padding it with chars zero.
         *
         * @param {String} ean
         * @returns {String}
         */
        sanitize_ean: function (ean) {
            ean = ean.substr(0, 13);
            ean = "0".repeat(13 - ean.length) + ean;
            return ean.substr(0, 12) + this.get_barcode_check_digit(ean);
        },

        /**
         * Sanitizes a UPC-A prefix by padding it with chars zero.
         *
         * @param {String} upc
         * @returns {String}
         */
        sanitize_upc: function (upc) {
            return this.sanitize_ean(upc).substr(1, 12);
        },

        // Checks if barcode matches the pattern
        // Additionnaly retrieves the optional numerical content in barcode
        // Returns an object containing:
        // - value: the numerical value encoded in the barcode (0 if no value encoded)
        // - base_code: the barcode in which numerical content is replaced by 0's
        // - match: boolean
        match_pattern: function (barcode, pattern, encoding) {
            var match = {
                value: 0,
                base_code: barcode,
                match: false,
            };
            barcode = barcode.replace("\\", "\\\\").replace("{", '\{').replace("}", "\}").replace(".", "\.");

            var numerical_content = pattern.match(/[{][N]*[D]*[}]/); // look for numerical content in pattern
            var base_pattern = pattern;
            if (numerical_content) { // the pattern encodes a numerical content
                var num_start = numerical_content.index; // start index of numerical content
                var num_length = numerical_content[0].length; // length of numerical content
                var value_string = barcode.substr(num_start, num_length - 2); // numerical content in barcode
                var whole_part_match = numerical_content[0].match("[{][N]*[D}]"); // looks for whole part of numerical content
                var decimal_part_match = numerical_content[0].match("[{N][D]*[}]"); // looks for decimal part
                var whole_part = value_string.substr(0, whole_part_match.index + whole_part_match[0].length - 2); // retrieve whole part of numerical content in barcode
                var decimal_part = "0." + value_string.substr(decimal_part_match.index, decimal_part_match[0].length - 1); // retrieve decimal part
                if (whole_part === '') {
                    whole_part = '0';
                }
                match.value = parseInt(whole_part) + parseFloat(decimal_part);

                // replace numerical content by 0's in barcode and pattern
                match.base_code = barcode.substr(0, num_start);
                base_pattern = pattern.substr(0, num_start);
                for (var i = 0; i < (num_length - 2); i++) {
                    match.base_code += "0";
                    base_pattern += "0";
                }
                match.base_code += barcode.substr(num_start + num_length - 2, barcode.length - 1);
                base_pattern += pattern.substr(num_start + num_length, pattern.length - 1);

                match.base_code = match.base_code
                    .replace("\\\\", "\\")
                    .replace("\{", "{")
                    .replace("\}", "}")
                    .replace("\.", ".");

                var base_code = match.base_code.split('');
                if (encoding === 'ean13') {
                    base_code[12] = '' + this.get_barcode_check_digit(match.base_code);
                } else if (encoding === 'ean8') {
                    base_code[7] = '' + this.get_barcode_check_digit(match.base_code);
                } else if (encoding === 'upca') {
                    base_code[11] = '' + this.get_barcode_check_digit(match.base_code);
                }
                match.base_code = base_code.join('');
            }

            if (base_pattern[0] !== '^') {
                base_pattern = "^" + base_pattern;
            }
            match.match = match.base_code.match(base_pattern);

            return match;
        },

        /**
         * Convert YYMMDD GS1 date into a Date object
         *
         * @param {string} gs1Date YYMMDD string date, length must be 6
         * @returns {Date}
         */
        gs1_date_to_date: function (gs1Date) {
            // See 7.12 Determination of century in dates:
            // https://www.gs1.org/sites/default/files/docs/barcodes/GS1_General_Specifications.pdfDetermination of century
            const now = new Date();
            const substractYear = parseInt(gs1Date.slice(0, 2)) - (now.getFullYear() % 100);
            let century = Math.floor(now.getFullYear() / 100);
            if (51 <= substractYear && substractYear <= 99) {
                century--;
            } else if (-99 <= substractYear && substractYear <= -50) {
                century++;
            }
            const year = century * 100 + parseInt(gs1Date.slice(0, 2));
            const date = new Date(year, parseInt(gs1Date.slice(2, 4) - 1));

            if (gs1Date.slice(-2) === '00') {
                // Day is not mandatory, when not set -> last day of the month
                date.setDate(new Date(year, parseInt(gs1Date.slice(2, 4)), 0).getDate());
            } else {
                date.setDate(parseInt(gs1Date.slice(-2)));
            }
            return date;
        },

        /**
         * Perform interpretation of the barcode value depending ot the rule.gs1_content_type
         *
         * @param {Array} match Result of a regex match with atmost 2 groups (ia and value)
         * @param {Object} rule Matched Barcode Rule
         * @returns {Object|null}
         */
        parse_gs1_rule_pattern: function (match, rule) {
            const result = {
                rule: Object.assign({}, rule),
                ai: match[1],
                string_value: match[2]
            };
            if (rule.gs1_content_type === 'measure') {
                let decimalPosition = 0; // Decimal position begin at the end, 0 means no decimal
                if (rule.gs1_decimal_usage) {
                    decimalPosition = parseInt(match[1][match[1].length - 1]);
                }
                if (decimalPosition > 0) {
                    const integral = match[2].slice(0, match[2].length - decimalPosition);
                    const decimal = match[2].slice(match[2].length - decimalPosition);
                    result.value = parseFloat(integral + "." + decimal);
                } else {
                    result.value = parseInt(match[2]);
                }
            } else if (rule.gs1_content_type === 'identifier') {
                if (parseInt(match[2][match[2].length - 1]) !== this.get_barcode_check_digit("0".repeat(18 - match[2].length) + match[2])) {
                    // throw new Error(_lt("Invalid barcode: the check digit is incorrect"));
                    // return {error: _lt("Invalid barcode: the check digit is incorrect")};
                    return false;
                }
                result.value = match[2];
            } else if (rule.gs1_content_type === 'date') {
                if (match[2].length !== 6) {
                    // throw new Error(_lt("Invalid barcode: can't be formated as date"));
                    // return {error: _lt("Invalid barcode: can't be formated as date")};
                    return false;
                }
                result.value = this.gs1_date_to_date(match[2]);
            } else {
                result.value = match[2];
            }
            return result;
        },

        /**
         * Try to decompose the gs1 extanded barcode into several unit of information using gs1 rules.
         *
         * @param {string} barcode
         * @returns {Array} Array of object
         */
        gs1_decompose_extanded: function (barcode) {
            const results = [];
            const rules = this.nomenclature.rules.filter(rule => rule.encoding === 'gs1-128');
            let separatorReg = FNC1_CHAR + "?";
            if (this.nomenclature.gs1_separator_fnc1 && this.nomenclature.gs1_separator_fnc1.trim()) {
                separatorReg = `(?:${this.nomenclature.gs1_separator_fnc1})?`;
            }

            while (barcode.length > 0) {
                const barcodeLength = barcode.length;
                for (const rule of rules) {
                    const match = barcode.match("^" + rule.pattern + separatorReg);
                    if (match && match.length >= 3) {
                        var default_res = {
                            encoding: '',
                            type: 'error',
                            code: match[0],
                            base_code: match[0],
                            value: 0,
                        };
                        const res = this.parse_gs1_rule_pattern(match, rule);
                        if (res) {
                            res.type = rule.type;
                            res.base_code = res.value;
                            res.code = res.value;
                            barcode = barcode.slice(match.index + match[0].length);
                            results.push(res);
                            if (barcode.length === 0) {
                                return results; // Barcode completly parsed, no need to keep looping.
                            }
                        } else {
                            if (results.length === 0) {
                                results.push(default_res)
                                console.log('This barcode can\'t be parsed by any barcode rules.')
                                return results;
                            } else {
                                return results;
                            }
                            // throw new Error(_lt("This barcode can't be parsed by any barcode rules."));
                        }
                    }
                }
                if (barcodeLength === barcode.length) {
                    console.log('This barcode can\'t be parsed by any barcode rules.')
                    // throw new Error(_lt("This barcode can't be partially or fully parsed."));
                }
            }

            return results;
        },

        /**
         * @override
         * @returns {Object|Array|null} If nomenclature is GS1, returns an array or null
         */
        parse_barcode: function (barcode) {
            if (this.nomenclature && this.nomenclature.is_gs1_nomenclature) {
                return this.gs1_decompose_extanded(barcode);
            }
            return this._super(...arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        _barcodeNomenclatureFields: function () {
            const fieldNames = [
                'name',
                'rule_ids',
                'upc_ean_conv',
            ];
            fieldNames.push('is_gs1_nomenclature', 'gs1_separator_fnc1');
            return fieldNames;
        },

        _barcodeRuleFields: function () {
            const fieldNames = [
                'name',
                'sequence',
                'type',
                'encoding',
                'pattern',
                'alias',
            ];
            fieldNames.push('gs1_content_type', 'gs1_decimal_usage', 'associated_uom_id');
            return fieldNames;
        },
    });

    return BarcodeParser;
});