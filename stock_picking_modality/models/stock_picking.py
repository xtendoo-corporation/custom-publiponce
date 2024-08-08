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

    # modality_id = fields.Many2one(
    #     related='stock.move.line',
    #     string='Modality',
    # )
    # destiny_id = fields.Many2one(
    #     related='stock.move.line',
    #     string='Destiny',
    # )
    # zone_id = fields.Many2one(
    #     related='stock.move.line',
    #     string='Zone',
    # )

    # def action_validate(self):
    #     res = super().button_validate()
    #     for line in self.move_ids:
    #         self.env['stock.move.planning'].create({
    #             'stock_move_id': line.id,
    #             'product_id': line.product_id.id,
    #             'product_name': line.product_id.name,
    #             'modality_id': line.modality_id.id if line.modality_id else False,
    #             'destiny_id': line.destiny_id.id if line.destiny_id else False,
    #             'zone_id': line.zone_id.id if line.zone_id else False,
    #             # 'res_partner_id': self.user_id.id if self.user_id else False,
    #             'res_partner_id': False,
    #             'partner_id': self.partner_id.id if self.partner_id else False,
    #             'date_scheduled': self.scheduled_date if self.scheduled_date else False,
    #             'quantity': line.quantity_done,
    #             'is_delivered': False,
    #             'delivery_date': False,
    #         })
    #     return res

        # max_line_qty = max(line.modality_id.line_qty for line in self.move_ids)
        # if max_line_qty > len(self.move_ids):
        #     raise exceptions.UserError("No puede validar debido a la incoherencia de las líneas con su modalidad.")
        # else:
        #     return super().button_validate()


