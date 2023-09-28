# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RatePickingModalityPrice(models.Model):
    _name = 'rate.picking.modality.price'

    rate_id = fields.Many2one(
        comodel_name='rate.picking.destiny',
        string='Rate',
        readonly=False,
    )
    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
        readonly=False,
    )
    price = fields.Float(
        string='Price',
        readonly=False,
    )
