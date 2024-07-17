# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockMovePlanningDate(models.Model):
    _name = 'stock.move.planning.date'
    _description = 'Stock Move Planning Date'
    _order = 'sequence'

    name = fields.Date(string='Date', required=True)
    sequence = fields.Integer(string='Sequence')
