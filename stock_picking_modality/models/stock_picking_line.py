# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingLine(models.Model):
    _name = 'stock.picking.line'

    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modalidad',
    )
