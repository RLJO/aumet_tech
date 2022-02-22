# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    date_done = fields.Date('Done Date', readonly=True)

    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        res.write({'date_done': fields.Datetime.now()})
        return res

    @api.model
    def _set_date_done(self):
        self._cr.execute(
            "update stock_move  set date_done=cast(write_date as date) where date_done is null and state='done'")
