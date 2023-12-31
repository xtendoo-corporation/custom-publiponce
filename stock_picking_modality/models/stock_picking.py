# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
    )

    def action_validate(self):
        max_line_qty = max(line.modality_id.line_qty for line in self.move_ids)
        if max_line_qty > len(self.move_ids):
            raise exceptions.UserError("No puede validar debido a la incoherencia de las líneas con su modalidad.")
        else:
            return super().button_validate()
