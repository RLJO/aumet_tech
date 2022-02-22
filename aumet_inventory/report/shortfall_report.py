# # -*- coding: utf-8 -*-
from odoo import models, api



class ReportShortReportView(models.AbstractModel):
    _name = 'report.aumet_inventory.product_shortfall_report_view'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': data,
        }
