# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMovePlanningStage(models.Model):
    _name = 'stock.move.planning.stage'
    _description = 'Stock Move Planning Stage'
    _order = 'sequence'

    stage_name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=1,
    )
    fold = fields.Boolean(
        string='Folded in Kanban View',
    )
