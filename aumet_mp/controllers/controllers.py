import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AumetOdooAPIs(http.Controller):
    @http.route('/distributors')
    def index(self, *args, **kwargs):
        request.cr.execute("select id,name from aumet_marketplace_distributor")
        data = request.cr.fetchall()
        fields = ["id", "name"]
        items = []
        for i in data:
            items.append(zip(i, fields))

        return http.request.make_response(json.dumps(data), headers={"Content-Type": "application/json"})

    @http.route('/product-locations')
    def index(self, *args, **kwargs):
        request.cr.execute("""SELECT datname FROM pg_database WHERE datistemplate = false;""")
        databases = request.cr.fetchall()
        result = []
        for database in databases:

            request.cr.execute("""
            select  pt.id,pt.name,sml.location_id,sml.location_dest_id ,locs.quantity,
            locs.posx,locs.posy  from product_template pt 
            inner join stock_move_line sml on sml.product_id = pt.id
            inner join (
                select sq.quantity as quantity, sl.posx as posx ,sl.posx as posy,sl.location_id as loc 
                from stock_quant sq inner join stock_location sl on sl.location_id = sq.location_id
                    ) locs 
                        on sml.location_dest_id=locs.loc order by (sml.date)
                """)

            data = request.cr.fetchall()
            fields = ["id", "name", "location_id", "location_dest_id", "quantity", "posx", "posy"]
            items = []
            for i in data:
                items.append(dict(zip(fields, i)))
            database_result = {"database_name": database, "products": items}
            result.append(database_result)

        return http.request.make_response(json.dumps(result), headers={"Content-Type": "application/json"})
