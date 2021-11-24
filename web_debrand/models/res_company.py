# Copyright 2015 Therp BV <http://therp.nl>
# Copyright 2016 Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _, exceptions


class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.depends('favicon')
    def get_favicon(self):
        self.favicon_url = \
            'data:image/png;base64,' + str(self.favicon.decode('UTF-8'))
        # python 3.x has sequence of bytes object,
        #  so we should decode it, else we get data starting with 'b'

    @api.depends('company_logo')
    def get_company_logo(self):
        self.company_logo_url = \
            ('data:image/png;base64,' +
             str(self.company_logo.decode('utf-8')))

    company_logo = fields.Binary("Logo", attachment=True,
                                 help="This field holds"
                                      " the image used "
                                      "for the Company Logo")
    company_name = fields.Char("Company Name", help="Branding Name")
    company_website = fields.Char("Company URL")
    favicon_url = fields.Char("Url", compute='get_favicon')
    company_logo_url = fields.Char("Url", compute='get_company_logo')

    # Sample Error Dialogue
    def error(self):
        raise exceptions.ValidationError(
            "This is a test Error message. You dont need to save the config after pop wizard.")

    # Sample Warning Dialogue
    def warning(self):
        raise exceptions.UserError("This is a test Error message. You don't need to save the config after pop wizard.")


