
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move.line"

    stock_move_line_ids = fields.Many2many('stock.move.line', string='Stock Move Line')



class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    def action_create_invoice(self):
        super(PurchaseOrderInherit, self).action_create_invoice()
        for j in self.invoice_ids:
            if len(j.invoice_line_ids[0].stock_move_line_ids) == 0:
                val = j

        for purchase_line in val.invoice_line_ids:
            purchase_line.stock_move_line_ids = purchase_line.purchase_line_id.move_ids.filtered(
                lambda stock_state: stock_state.state == 'done' and stock_state.in_invoice == False).move_line_ids
            for j in purchase_line.purchase_line_id.move_ids.filtered(lambda stock_state: stock_state.state == 'done'):
                j.in_invoice = True
