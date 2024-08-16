# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if 'sale_id' in vals:
            sale_order = self.env['sale.order'].browse(vals['sale_id'])
            sale_order.update_stock_transfers_with_order_line()
            for move in res.move_lines:
                move.sale_line_id = sale_order.order_line.filtered(lambda l: l.product_id == move.product_id).id
        return res

    def write(self, vals):
        res = super(StockPicking, self).write(vals)
        if 'state' in vals and vals['state'] == 'done' and self.sale_id:
            self.sale_id.update_stock_transfers_with_order_line()
            for move in self.move_lines:
                move.sale_line_id = self.sale_id.order_line.filtered(lambda l: l.product_id == move.product_id).id
        return res
