# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RatePickingModalityPrice(models.Model):
    _name = 'rate.picking.modality.price'

    rate_id = fields.Many2one(
        comodel_name='rate.picking.destiny',
        string='Rate',
        readonly=False,
        required=True,
    )
    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
        required=True,
        readonly=False,
    )
    price = fields.Float(
        string='Price',
        readonly=False,
    )
    rate_name = fields.Char(
        string='Rate Name',
        compute='get_rate_name',
        store=True,
        readonly=False,
    )

    _sql_constraints = [
        ('unique_rate_modality', 'unique(rate_name, modality_id)',
         'Un destino solo puede tener un precio para una modalidad.')
    ]

    @api.depends('rate_id')
    def get_rate_name(self):
        for record in self:
            record.rate_name = record.rate_id.name
