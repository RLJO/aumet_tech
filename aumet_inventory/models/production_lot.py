from datetime import datetime, timedelta
from odoo import api, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    def name_get(self):
        if 'show_as_date' in self.env.context:
            res = []
            for record in self:
                if record.expiration_date:
                    d = datetime.strptime(str(record.expiration_date), '%Y-%m-%d %H:%M:%S').date()
                    name = str(d)
                else:
                    name = record.name
                res.append((record.id, name))
            return res
        return super(ProductionLot, self).name_get()

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductionLot, self).create(vals_list)
        for r in res:
            if r.expiration_date:
                r.alert_date = r.expiration_date - timedelta(days=30)
        return res
