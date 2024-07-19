# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        for line in self.order_line:
            self.env['stock.move.planning'].create({
                'product_id': line.product_id.id,
                'product_name': line.product_id.name,
                'res_partner_id': False,
                'order_id': self.id,
                'partner_id': self.partner_id.id if self.partner_id else False,
                'date_scheduled': self.date_order if self.date_order else False,
                'quantity': line.product_uom_qty,
                'is_delivered': False,
                'delivery_date': False,
            })
            print("*"*80)
            print(line.product_id)
            print(line.product_uom_qty)
        return res

    def action_view_plannings(self):
        self.ensure_one()
        action = self.env.ref('stock_picking_modality.action_stock_move_planning').read()[0]
        action['domain'] = [('order_id', '=', self.id)]
        # action['domain'] = [('product_id', 'in', self.order_line.mapped('product_id').ids)]
        return action
