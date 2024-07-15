# Copyright 2023 Abraham, Salvador (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingZone(models.Model):
    _name = 'stock.picking.zone'
    _description = 'Zona de entregas'

    name = fields.Char(
        string='Name',
        readonly=False,
        store=True,
    )

    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
    )

