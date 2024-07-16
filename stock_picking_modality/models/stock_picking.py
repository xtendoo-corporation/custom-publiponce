# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_validate(self):
        res = super().button_validate()
        for line in self.move_ids:
            self.env['stock.move.planning'].create({
                'stock_move_id': line.id,
                'product_id': line.product_id.id,
                'product_name': line.product_id.name,
                'modality_id': line.modality_id.id if line.modality_id else False,
                'destiny_id': line.destiny_id.id if line.destiny_id else False,
                'zone_id': line.zone_id.id if line.zone_id else False,
                'res_partner_id': self.user_id.id if self.user_id else False,
                'date_scheduled': self.scheduled_date if self.scheduled_date else False,
                'quantity': line.quantity_done,
                'is_delivered': False,
                'delivery_date': False,
            })
            print("*"*80)
            print(line.product_id)
            print(line.quantity_done)
        return res

        # max_line_qty = max(line.modality_id.line_qty for line in self.move_ids)
        # if max_line_qty > len(self.move_ids):
        #     raise exceptions.UserError("No puede validar debido a la incoherencia de las líneas con su modalidad.")
        # else:
        #     return super().button_validate()


