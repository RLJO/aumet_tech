# -*- coding: utf-8 -*-
import re
import datetime
import calendar

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

FNC1_CHAR = '\x1D'


class BarcodeNomenclature(models.Model):
    _inherit = 'barcode.nomenclature'

    is_gs1_nomenclature = fields.Boolean(
        string="Is GS1 Nomenclature",
        help="This Nomenclature use the GS1 specification, only GS1-128 encoding rules is accepted is this kind of nomenclature.")
    gs1_separator_fnc1 = fields.Char(
        string="FNC1 Separator", trim=False,
        help="Alternative regex delimiter for the FNC1 (by default, if not set, it is <GS> ASCII 29 char). The separator must not match the begin/end of any related rules pattern.")

    @api.constrains('gs1_separator_fnc1')
    def _check_pattern(self):
        for nom in self:
            if nom.is_gs1_nomenclature and nom.gs1_separator_fnc1:
                try:
                    re.compile("(?:%s)?" % nom.gs1_separator_fnc1)
                except re.error as error:
                    raise ValidationError(_("The FNC1 Separator Alternative is not a valid Regex: ") + str(error))

    @api.model
    def get_barcode_check_digit(self, numeric_barcode):
        """ Computes and returns the barcode check digit. The used algorithm
        follows the GTIN specifications and can be used by all compatible
        barcode nomenclature, like as EAN-8, EAN-12 (UPC-A) or EAN-13.

        https://www.gs1.org/sites/default/files/docs/barcodes/GS1_General_Specifications.pdf
        https://www.gs1.org/services/how-calculate-check-digit-manually

        :param numeric_barcode: the barcode to verify/recompute the check digit
        :type numeric_barcode: str
        :return: the number corresponding to the right check digit
        :rtype: int
        """
        # Multiply value of each position by
        # N1  N2  N3  N4  N5  N6  N7  N8  N9  N10 N11 N12 N13 N14 N15 N16 N17 N18
        # x3  X1  x3  x1  x3  x1  x3  x1  x3  x1  x3  x1  x3  x1  x3  x1  x3  CHECKSUM
        oddsum = evensum = total = 0
        code = numeric_barcode[-2::-1]  # Remove the check digit and reverse the barcode.
        # The CHECKSUM digit is removed because it will be recomputed and it must not interfer with
        # the computation. Also, the barcode is inverted, so the barcode length doesn't matter.
        # Otherwise, the digits' group (even or odd) could be different according to the barcode length.
        for i, digit in enumerate(code):
            if i % 2 == 0:
                evensum += int(digit)
            else:
                oddsum += int(digit)
        total = evensum * 3 + oddsum
        return (10 - total % 10) % 10

    @api.model
    def check_encoding(self, barcode, encoding):
        """ Checks if the given barcode is correctly encoded.

        :return: True if the barcode string is encoded with the provided encoding.
        :rtype: bool
        """
        if encoding == "any":
            return True
        barcode_sizes = {
            'ean8': 8,
            'ean13': 13,
            'upca': 12,
        }
        barcode_size = barcode_sizes[encoding]
        return len(barcode) == barcode_size and re.match(r"^\d+$", barcode) and self.get_barcode_check_digit(
            barcode) == int(barcode[-1])

    @api.model
    def sanitize_ean(self, ean):
        """ Returns a valid zero padded EAN-13 from an EAN prefix.

        :type ean: str
        """
        ean = ean[0:13].zfill(13)
        return ean[0:-1] + str(self.get_barcode_check_digit(ean))

    def match_pattern(self, barcode, pattern):
        """Checks barcode matches the pattern and retrieves the optional numeric value in barcode.

        :param barcode:
        :type barcode: str
        :param pattern:
        :type pattern: str
        :return: an object containing:
            - value: the numerical value encoded in the barcode (0 if no value encoded)
            - base_code: the barcode in which numerical content is replaced by 0's
            - match: boolean
        :rtype: dict
        """
        match = {
            'value': 0,
            'base_code': barcode,
            'match': False,
        }

        barcode = barcode.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}').replace('.', '\\.')
        numerical_content = re.search("[{][N]*[D]*[}]", pattern)  # look for numerical content in pattern

        if numerical_content:  # the pattern encodes a numerical content
            num_start = numerical_content.start()  # start index of numerical content
            num_end = numerical_content.end()  # end index of numerical content
            value_string = barcode[num_start:num_end - 2]  # numerical content in barcode

            whole_part_match = re.search("[{][N]*[D}]",
                                         numerical_content.group())  # looks for whole part of numerical content
            decimal_part_match = re.search("[{N][D]*[}]", numerical_content.group())  # looks for decimal part
            whole_part = value_string[
                         :whole_part_match.end() - 2]  # retrieve whole part of numerical content in barcode
            decimal_part = "0." + value_string[
                                  decimal_part_match.start():decimal_part_match.end() - 1]  # retrieve decimal part
            if whole_part == '':
                whole_part = '0'
            match['value'] = int(whole_part) + float(decimal_part)

            match['base_code'] = barcode[:num_start] + (num_end - num_start - 2) * "0" + barcode[
                                                                                         num_end - 2:]  # replace numerical content by 0's in barcode
            match['base_code'] = match['base_code'].replace("\\\\", "\\").replace("\\{", "{").replace("\\}",
                                                                                                      "}").replace(
                "\\.", ".")
            pattern = pattern[:num_start] + (num_end - num_start - 2) * "0" + pattern[
                                                                              num_end:]  # replace numerical content by 0's in pattern to match

        match['match'] = re.match(pattern, match['base_code'][:len(pattern)])

        return match

    @api.model
    def gs1_date_to_date(self, gs1_date):
        """ Converts a GS1 date into a datetime.date.

        :param gs1_date: A year formated as yymmdd
        :type gs1_date: str
        :return: converted date
        :rtype: datetime.date
        """
        # See 7.12 Determination of century in dates:
        # https://www.gs1.org/sites/default/files/docs/barcodes/GS1_General_Specifications.pdf
        now = datetime.date.today()
        current_century = now.year // 100
        substract_year = int(gs1_date[0:2]) - (now.year % 100)
        century = (51 <= substract_year <= 99 and current_century - 1) or \
                  (-99 <= substract_year <= -50 and current_century + 1) or \
                  current_century
        year = century * 100 + int(gs1_date[0:2])

        if gs1_date[-2:] == '00':  # Day is not mandatory, when not set -> last day of the month
            date = datetime.datetime.strptime(str(year) + gs1_date[2:4], '%Y%m')
            date = date.replace(day=calendar.monthrange(year, int(gs1_date[2:4]))[1])
        else:
            date = datetime.datetime.strptime(str(year) + gs1_date[2:], '%Y%m%d')
        return date.date()

    def parse_gs1_rule_pattern(self, match, rule):
        result = {
            'rule': rule,
            'ai': match.group(1),
            'string_value': match.group(2),
        }
        if rule.gs1_content_type == 'measure':
            try:
                decimal_position = 0  # Decimal position begins at the end, 0 means no decimal.
                if rule.gs1_decimal_usage:
                    decimal_position = int(match.group(1)[-1])
                if decimal_position > 0:
                    result['value'] = float(
                        match.group(2)[:-decimal_position] + "." + match.group(2)[-decimal_position:])
                else:
                    result['value'] = int(match.group(2))
            except Exception:
                raise ValidationError(_(
                    "There is something wrong with the barcode rule \"%s\" pattern.\n"
                    "If this rule uses decimal, check it can't get sometime else than a digit as last char for the Application Identifier.\n"
                    "Check also the possible matched values can only be digits, otherwise the value can't be casted as a measure.",
                    rule.name))
        elif rule.gs1_content_type == 'identifier':
            # Check digit and remove it of the value
            if match.group(2)[-1] != str(
                    self.get_barcode_check_digit("0" * (18 - len(match.group(2))) + match.group(2))):
                return None
            result['value'] = match.group(2)
        elif rule.gs1_content_type == 'date':
            if len(match.group(2)) != 6:
                return None
            result['value'] = self.gs1_date_to_date(match.group(2))
        else:  # when gs1_content_type == 'alpha':
            result['value'] = match.group(2)
        return result

    def gs1_decompose_extanded(self, barcode):
        """Try to decompose the gs1 extanded barcode into several unit of information using gs1 rules.

        Return a ordered list of dict
        """
        self.ensure_one()
        separator_group = FNC1_CHAR + "?"
        if self.gs1_separator_fnc1:
            separator_group = "(?:%s)?" % self.gs1_separator_fnc1
        results = []
        gs1_rules = self.rule_ids.filtered(lambda r: r.encoding == 'gs1-128')

        def find_next_rule(remaining_barcode):
            for rule in gs1_rules:
                match = re.search("^" + rule.pattern + separator_group, remaining_barcode)
                # If match and contains 2 groups at minimun, the first one need to be the AI and the second the value
                # We can't use regex nammed group because in JS, it is not the same regex syntax (and not compatible in all browser)
                if match and len(match.groups()) >= 2:
                    res = self.parse_gs1_rule_pattern(match, rule)
                    if res:
                        return res, remaining_barcode[match.end():]
            return None

        while len(barcode) > 0:
            res_bar = find_next_rule(barcode)
            # Cannot continue -> Fail to decompose gs1 and return
            if not res_bar or res_bar[1] == barcode:
                return results
            barcode = res_bar[1]
            results.append(res_bar[0])

        return results

    def parse_barcode(self, barcode):
        """ Attempts to interpret and parse a barcode.

        :param barcode:
        :type barcode: str
        :return: A object containing various information about the barcode, like as:
            - code: the barcode
            - type: the barcode's type
            - value: if the id encodes a numerical value, it will be put there
            - base_code: the barcode code with all the encoding parts set to
              zero; the one put on the product in the backend
        :rtype: dict
        """
        if self.is_gs1_nomenclature:
            return self.gs1_decompose_extanded(barcode)
        return super().parse_barcode(barcode)


class BarcodeRule(models.Model):
    _inherit = 'barcode.rule'

    def _default_encoding(self):
        return 'gs1-128' if self.env.context.get('is_gs1') else 'any'

    encoding = fields.Selection(
        selection_add=[('gs1-128', 'GS1-128')], default=_default_encoding,
        ondelete={'gs1-128': 'set default'})
    type = fields.Selection(
        selection_add=[
            ('quantity', 'Quantity'),
            ('location', 'Location'),
            ('location_dest', 'Destination location'),
            ('lot', 'Lot number'),
            ('package', 'Package'),
            ('use_date', 'Best before Date'),
            ('expiration_date', 'Expiration Date'),
            ('package_type', 'Packaging Type'),
            ('packaging_date', 'Packaging Date'),
        ], ondelete={
            'quantity': 'set default',
            'location': 'set default',
            'location_dest': 'set default',
            'lot': 'set default',
            'package': 'set default',
            'use_date': 'set default',
            'expiration_date': 'set default',
            'package_type': 'set default',
            'packaging_date': 'set default',
        })
    is_gs1_nomenclature = fields.Boolean(related="barcode_nomenclature_id.is_gs1_nomenclature")
    gs1_content_type = fields.Selection([
        ('date', 'Date'),
        ('measure', 'Measure'),
        ('identifier', 'Numeric Identifier'),
        ('alpha', 'Alpha-Numeric Name'),
    ], string="GS1 Content Type",
        help="The GS1 content type defines what kind of data the rule will process the barcode as:\
        * Date: the barcode will be converted into a Odoo datetime;\
        * Measure: the barcode's value is related to a specific UoM;\
        * Numeric Identifier: fixed length barcode following a specific encoding;\
        * Alpha-Numeric Name: variable length barcode.")
    gs1_decimal_usage = fields.Boolean('Decimal',
                                       help="If True, use the last digit of AI to dertermine where the first decimal is")
    associated_uom_id = fields.Many2one('uom.uom')

    @api.constrains('pattern')
    def _check_pattern(self):
        gs1_rules = self.filtered(lambda rule: rule.encoding == 'gs1-128')
        for rule in gs1_rules:
            try:
                re.compile(rule.pattern)
            except re.error as error:
                raise ValidationError(_("The rule pattern \"%s\" is not a valid Regex: ", rule.name) + str(error))
            groups = re.findall(r'\([^)]*\)', rule.pattern)
            if len(groups) != 2:
                raise ValidationError(_(
                    "The rule pattern \"%s\" is not valid, it needs two groups:"
                    "\n\t- A first one for the Application Identifier (usually 2 to 4 digits);"
                    "\n\t- A second one to catch the value.",
                    rule.name))

        super(BarcodeRule, (self - gs1_rules))._check_pattern()

