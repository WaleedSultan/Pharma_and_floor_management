import math
from collections import defaultdict

from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.tools.misc import formatLang
from datetime import date
import math

class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one('sale.order', compute='_get_invoice_sale')

    def _get_invoice_sale(self):
        for move_id in self:
            sale_id = self.env['sale.order'].search([('name', '=', move_id.invoice_origin)], limit=1).id
            move_id.sale_order_id = sale_id

    def _get_invoiced_lot_values(self):
        """ Get and prepare data to show a table of invoiced lot on the invoice's report. """
        self.ensure_one()

        res = super(AccountMove, self)._get_invoiced_lot_values()

        res = []
        if self.state == 'draft' or not self.invoice_date or self.move_type not in ('out_invoice', 'out_refund'):
            return res

        current_invoice_amls = self.invoice_line_ids.filtered(
            lambda aml: not aml.display_type and aml.product_id and aml.product_id.type in (
            'consu', 'product') and aml.quantity)
        all_invoices_amls = current_invoice_amls.sale_line_ids.invoice_lines.filtered(
            lambda aml: aml.move_id.state == 'posted').sorted(lambda aml: (aml.date, aml.move_name, aml.id))
        index = all_invoices_amls.ids.index(current_invoice_amls[:1].id) if current_invoice_amls[
                                                                            :1] in all_invoices_amls else 0
        previous_amls = all_invoices_amls[:index]

        previous_qties_invoiced = previous_amls._get_invoiced_qty_per_product()
        invoiced_qties = current_invoice_amls._get_invoiced_qty_per_product()
        invoiced_products = invoiced_qties.keys()

        qties_per_lot = defaultdict(float)
        previous_qties_delivered = defaultdict(float)
        stock_move_lines = current_invoice_amls.sale_line_ids.move_ids.move_line_ids.filtered(
            lambda sml: sml.state == 'done' and sml.lot_id).sorted(lambda sml: (sml.date, sml.id))
        for sml in stock_move_lines:
            if sml.product_id not in invoiced_products or 'customer' not in {sml.location_id.usage,
                                                                             sml.location_dest_id.usage}:
                continue
            product = sml.product_id
            product_uom = product.uom_id
            qty_done = sml.product_uom_id._compute_quantity(sml.qty_done, product_uom)

            if sml.location_id.usage == 'customer':
                returned_qty = min(qties_per_lot[sml.lot_id], qty_done)
                qties_per_lot[sml.lot_id] -= returned_qty
                qty_done = returned_qty - qty_done

            previous_qty_invoiced = previous_qties_invoiced[product]
            previous_qty_delivered = previous_qties_delivered[product]
            # If we return more than currently delivered (i.e., qty_done < 0), we remove the surplus
            # from the previously delivered (and qty_done becomes zero). If it's a delivery, we first
            # try to reach the previous_qty_invoiced
            if float_compare(qty_done, 0, precision_rounding=product_uom.rounding) < 0 or \
                    float_compare(previous_qty_delivered, previous_qty_invoiced,
                                  precision_rounding=product_uom.rounding) < 0:
                previously_done = qty_done if sml.location_id.usage == 'customer' else min(
                    previous_qty_invoiced - previous_qty_delivered, qty_done)
                previous_qties_delivered[product] += previously_done
                qty_done -= previously_done

            qties_per_lot[sml.lot_id] += qty_done

        for lot, qty in qties_per_lot.items():
            # access the lot as a superuser in order to avoid an error
            # when a user prints an invoice without having the stock access
            lot = lot.sudo()
            if float_is_zero(invoiced_qties[lot.product_id], precision_rounding=lot.product_uom_id.rounding) \
                    or float_compare(qty, 0, precision_rounding=lot.product_uom_id.rounding) <= 0:
                continue
            invoiced_lot_qty = min(qty, invoiced_qties[lot.product_id])
            invoiced_qties[lot.product_id] -= invoiced_lot_qty
            res.append({
                'product_id': lot.product_id.id,
                'expiry_date': lot.expiration_date.date() if lot.expiration_date else False,
                'product_name': lot.product_id.display_name,
                'quantity': formatLang(self.env, invoiced_lot_qty, dp='Product Unit of Measure'),
                'uom_name': lot.product_uom_id.name,
                'lot_name': lot.name,
                # The lot id is needed by localizations to inherit the method and add custom fields on the invoice's report.
                'lot_id': lot.id,
            })

        return res

    def action_print_report(self):
        data = {
            'model': 'account.move',
            'form': self.read()[0]
        }
        return self.env.ref('invoice_pharma.account_invoices_pharma').report_action(self, data=data)


class accountReportAb(models.AbstractModel):
    _name = 'report.invoice_pharma.report_invoice'

    def _get_report_values(self, docids, data=None):
        if docids:
            docs = self.env['account.move'].search([('id', '=', docids[0])])
        else:
            docs = self.env['account.move'].search([('id', '=', data['form']['id'])])
        invoice_line_ids = {}
        validation_date = True
        line_total = 0
        coupons = docs.sale_order_id.coupon_ids
        for sale_line in docs.invoice_line_ids.sorted(key=(lambda line: (line.product_id))):
            discount=0.0
            if not sale_line.is_discount_line:
                print(sale_line.name)
                line_total = sale_line.price_subtotal
                for product in coupons:
                    if sale_line.product_id.id in product.discount_specific_product_ids.ids:
                        print("Hey its the discount product check it ")
                        if product.reward_type == 'discount':
                            discount = product.discount_percentage
                            print(discount)
                            try:
                                discount = int(discount)
                            except:
                                discount = float(discount)
                            line_total = sale_line.price_subtotal - (sale_line.price_subtotal * (discount / 100))
                        # elif product.reward_type == "product":
                        #     print("testttt")
                        else:
                            discount = 0.0

                batch_ids = sale_line.move_id._get_invoiced_lot_values()
                batch_values = []
                for batch in batch_ids:
                    if batch['product_id'] == sale_line.product_id.id:
                        batch_values = [batch['lot_name'], batch['lot_id'], batch['expiry_date']]
                if len(batch_values) == 0:
                    batch_values = ['', '', '']
                # if sale_line.account_move_discount_line_id:
                #     print("helll")
                #     print("helll")
                #     print("helll")
                #     print("helll")
                if sale_line.product_id.manufacturer.name in invoice_line_ids.keys():
                     invoice_line_ids[sale_line.product_id.manufacturer.name].append({
                        'name': sale_line.product_id.name,
                        'pack': sale_line.name,
                        'batch': batch_values,
                        'quantity': sale_line.quantity,
                        'unit_price': sale_line.price_unit,
                        'tax': sale_line.tax_ids.amount or 0.0,
                        'discount': sale_line.discount or 0.0,
                        'Promotion_Discount': discount,
                        'subtotal': round(line_total,2),
                        'Free_product': 0,
                        'manufacturer_total': round(invoice_line_ids[sale_line.product_id.manufacturer.name][
                                                  len(invoice_line_ids[sale_line.product_id.manufacturer.name]) - 1][
                                                  'manufacturer_total'] + line_total,2),
                        'manufacturer_count': invoice_line_ids[sale_line.product_id.manufacturer.name][
                                                  len(invoice_line_ids[sale_line.product_id.manufacturer.name]) - 1][
                                                  'manufacturer_count'] + 1,
                        "manu_total_qty": invoice_line_ids[sale_line.product_id.manufacturer.name][
                                                  len(invoice_line_ids[sale_line.product_id.manufacturer.name]) - 1][
                                                  'manu_total_qty'] + sale_line.quantity,
                        "count_free":0
                    })
                else:
                    invoice_line_ids[sale_line.product_id.manufacturer.name] = [{
                        'name': sale_line.product_id.name,
                        'pack': sale_line.name,
                        'batch': batch_values,
                        'quantity': sale_line.quantity,
                        'unit_price': sale_line.price_unit,
                        'tax': sale_line.tax_ids.amount or 0.0,
                        'discount': sale_line.discount or 0.0,
                        'Promotion_Discount': discount or 0,
                        'subtotal': round(line_total, 2),
                        'Free_product': 0,
                        'manufacturer_total': round(line_total,2),
                        'manufacturer_count': 1,
                        "manu_total_qty": sale_line.quantity,
                        "count_free": 0

                    }]
            else:
                keys = invoice_line_ids.copy()
                try:
                    if 'Free Product' in sale_line.product_id.name:
                        for product in keys:
                            for product_name in keys[product]:
                                print(product_name['name'])
                                if product_name['name'] in sale_line.product_id.name:
                                    product_name['Free_product'] = product_name['Free_product'] + sale_line.quantity
                                    product_name['subtotal'] = product_name['subtotal'] - abs(sale_line.price_subtotal)
                                    invoice_line_ids[product][-1]["count_free"] = invoice_line_ids[product][-1]["count_free"] + sale_line.quantity
                                    product_name["quantity"] = product_name["quantity"] - sale_line.quantity
                                    invoice_line_ids[product][-1]["manu_total_qty"] = invoice_line_ids[product][-1]["manu_total_qty"] - sale_line.quantity
                                    invoice_line_ids[product][-1]["manufacturer_total"] = round(invoice_line_ids[product][-1]["manufacturer_total"] - abs(sale_line.price_subtotal), 2)
                                    try:
                                        invoice_line_ids.pop(sale_line.product_id.name)
                                    except:
                                        print("just kidding")
                                elif 'Free Product' in product_name['name']:
                                    invoice_line_ids[sale_line.product_id.name] = [{
                                    'name': sale_line.product_id.name,
                                    'pack': "",
                                    'batch': ['', '', ''],
                                    'quantity': 0.0,
                                    'unit_price': 0.0,
                                    'tax': 0.0,
                                    'discount': 0.0,
                                    'Promotion_Discount': 0,
                                    'subtotal': 0.0,
                                    'Free_product': sale_line.quantity,
                                    'manufacturer_total': 0.0,
                                    'manufacturer_count': 0.0,
                                        "count_free": 0

                                }]
                                    print("not the product")
                                    pass

                        print("Free Product")
                        pass
                except:
                    print("This is the error")
            # except:
            # #     print("This is the real error terror")
            # else:
        if docs.partner_id.license_expiry:
            if docs.partner_id.license_expiry > date.today():
                validation_date = True
            else:
                validation_date = False

        return {
            'data': invoice_line_ids,
            'validation': validation_date,
            'docs': docs,
        }


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_move_discount_line_id = fields.Many2one('account.move.line', compute='_get_move_order_discount_line',
                                                    store=False)
    is_discount_line = fields.Boolean('Discount Line', compute='_get_move_order_discount_line', store=False)

    @api.depends('product_id')
    def _get_move_order_discount_line(self):
        # for line in self:
        #     line.is_discount_line = False
        #     line.account_move_discount_line_id = False
        #     for current_line in line.move_id.invoice_line_ids:
        #         if line.product_id != current_line.product_id and current_line.product_id and line.product_id \
        #                 and current_line.product_id.name[len(current_line.product_id.name) - len(line.product_id.name):] == line.product_id.name and len(current_line.product_id.name) - len(line.product_id.name) !=0:
        #             line.account_move_discount_line_id = current_line.id
        #             line.is_discount_line = False
        #
        #         elif line.product_id != current_line.product_id and current_line.product_id and line.product_id \
        #                 and current_line.product_id.name == line.product_id.name[len(line.product_id.name) - len(current_line.product_id.name):] and len(current_line.product_id.name) - len(line.product_id.name) !=0 :
        #             line.is_discount_line = True
        #             line.account_move_discount_line_id = False
        for line in self.move_id.invoice_line_ids:
            line.is_discount_line = False
            line.account_move_discount_line_id = False

            if "Discount" in line.name or 'Free Product' in line.name:
                line.is_discount_line = True

# try:
            #     if not sale_line.is_discount_line and not 'Free Product' in sale_line.product_id.name:
            #         line_total = sale_line.price_subtotal
            #         try:
            #             if sale_line.account_move_discount_line_id.name:
            #                 discount = sale_line.account_move_discount_line_id.product_id.name[:2]
            #                 if '.' in discount:
            #                     discount = discount[:1]
            #
            #                 if discount.isdigit():
            #                     line_total = sale_line.price_subtotal - (sale_line.price_subtotal * (int(discount) / 100))
            #                 else:
            #                     discount = 0.0
            #             else:
            #                 discount = 0.0
            #             batch_ids = sale_line.move_id._get_invoiced_lot_values()
            #             batch_values = []
            #             for batch in batch_ids:
            #                 if batch['product_id'] == sale_line.product_id.id:
            #                     batch_values = [batch['lot_name'], batch['lot_id'], batch['expiry_date']]
            #             if len(batch_values) == 0:
            #                 batch_values = ['', '', '']
            #         except:
            #             batch_values = ['', '', '']
            #             print("Nothing Found")