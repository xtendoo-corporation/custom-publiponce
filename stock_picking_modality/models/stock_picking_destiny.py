# Copyright 2023 Abraham, Salvador (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingDestiny(models.Model):
    _name = 'stock.picking.destiny'
    _description = 'Destino de entregas'

    name = fields.Char(
        string='Name',
        readonly=False,
        store=True,
    )

    zone_id = fields.One2many(
        comodel_name='stock.picking.zone',
        inverse_name='destiny_id',
        string='Zone',
        readonly=False,
        required=True,
    )
