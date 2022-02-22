# -*- coding: utf-8 -*-
from odoo import models, api


class ClaimReportAbs(models.AbstractModel):
    _name = 'report.pos_insurance_payment.claim_report_template'
    _description = 'Claim Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'data': data,
            'doc_model': 'claim.report',
        }
