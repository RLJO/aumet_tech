from odoo import models, api


class POSSession(models.Model):
    _inherit = 'pos.session'

    def _validate_session(self):
        res = super(POSSession, self)._validate_session()
        for l in self.sudo():
            style_css = '''
                .tb1 {
                    border-collapse: collapse;
                    width:100%;
                }
                .tb1 td {
                    padding: 6px 12px;
                }
                .tb1 th {
                    text-align: left;
                    padding: 6px 12px;background: #EDEDEE;color: balck;
                    border-left: 1px solid #dfdfdf;
                    border-bottom: 2px solid #ddd;
                }
                .tb1 tbody tr:nth-child(2n) {
                    background:#EFEEF7;
                    border-top: 1px solid #ddd;
                }
                '''
            mail = self.company_id.email
            subject = 'POS Session Summary - ' + str(l.name)
            table = '<!DOCTYPE html><html><head><style>' + str(style_css) + '</style></head><body>'
            table += '<div style="direction:ltr"></br><h2 style="font-size:17px">' + str(l.name) + ':</h2> </br> '
            table += '<p>POS session closed summary: </p>'
            table += '<table class="tb1"> ' + \
                     ' <tr><td>Open By: ' + str(l.create_uid.name) + '</td> </tr>' + \
                     ' <tr><td>Closed By: ' + str(self.user_id.name) + '</td> </tr>' + \
                     ' <tr><td>Transactions: ' + str(l.cash_real_transaction) + '</td> </tr>' + \
                     ' <tr><td>Expected: ' + str(l.cash_real_expected) + '</td> </tr>' + \
                     ' <tr><td>Actual In Cash: ' + str(l.cash_register_balance_end_real) + '</td> </tr>' + \
                     ' <tr><td>Difference: ' + str(l.cash_real_difference) + '</td> </tr>'
            table += '</table></br></br></div></body></html>'

            if table and mail:
                post_values = {
                    'subject': subject,
                    'body_html': table,
                    'parent_id': False,
                    'email_to': mail,
                    'attachment_ids': [],
                    'auto_delete': False,
                    'model': 'pos.session',
                    'res_id': l.id,
                    'notification': True,
                    'message_type': 'comment'
                }
                m = self.env['mail.mail'].sudo().create(post_values)
                m.send()
        return res
