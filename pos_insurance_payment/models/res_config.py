from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    insurance_commission_account_id = fields.Many2one('account.account', string='Insurance Commission Account')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrDefault = self.env['ir.default'].sudo()
        insurance_commission_account_id = IrDefault.get('res.config.settings', "insurance_commission_account_id")
        res.update({'insurance_commission_account_id': insurance_commission_account_id or False})
        return res

    def set_values(self):
        IrDefault = self.env['ir.default'].sudo()
        IrDefault.set('res.config.settings', "insurance_commission_account_id", self.insurance_commission_account_id.id)
        return super(ResConfigSettings, self).set_values()
