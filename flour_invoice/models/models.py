
from odoo import fields, models, api, _

from odoo.exceptions import ValidationError



class stockPickingInherit(models.Model):
    _inherit = "stock.move.line"
    tare_deduction = fields.Float(string="Tare Deduction")
    addition_deduction = fields.Float(string="Addition Deduction")
    in_invoice_line = fields.Boolean('In Invoice Line')



class stockPickingInherit(models.Model):
    _inherit = "mrp.production"

    def button_mark_done(self):
        for move_product in self.move_byproduct_ids:
            if len(move_product.move_line_ids):
                for move_line in move_product.move_line_ids:
                    if move_line.lot_id.id:
                        print('Lot found')
                    else:
                        raise ValidationError(_('Missing Lot/Serial number'))
                        return False
                    print("hell")
            else:
                raise ValidationError(_('Missing Lot/Serial number'))
                return False
        return super().button_mark_done()
