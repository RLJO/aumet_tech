from odoo import models


class AvailablePOS(models.Model):
    _inherit = "stock.move.line"

    # #  add available in the pos
    # def _action_done(self):
    #     super(AvailablePOS, self)._action_done()
    #     for ml in self:
    #         if ml.product_id.type == 'product':
    #             # available pos
    #             location_id = ml.location_id
    #             if location_id.usage in ['customer', 'supplier', 'inventory']:
    #                 location_dest_id = ml.location_dest_id
    #                 if location_dest_id.usage == "internal":
    #                     product_tmpl_id = ml.product_id.product_tmpl_id
    #                     self.env.cr.execute(
    #                         f"update product_template set available_in_pos=true where id={product_tmpl_id.id}")
    #                     self.env.cr.commit()
