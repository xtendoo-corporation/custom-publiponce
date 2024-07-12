# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingModalityDestinyPrice(models.Model):
    _name = 'stock.picking.modality.destiny.price'
    _description = 'Precio de destino por modalidad'

    name = fields.Char(
        compute="_compute_name",
        required=False,
        store=True,
        readonly=False,
    )
    modality_id = fields.Many2one(
        comodel_name='stock.picking.modality',
        string='Modality',
        required=True,
        readonly=False,
    )
    destiny_id = fields.Many2one(
        comodel_name='stock.picking.destiny',
        string='Destiny',
        readonly=False,
        required=True,
    )
    zone_id = fields.Many2one(
        comodel_name='stock.picking.zone',
        string='Zone',
        readonly=False,
        required=True,
    )
    price = fields.Float(
        string='Price',
        readonly=False,
    )

    _sql_constraints = [
        ('unique_destiny_id_modality', 'unique(destiny_id, modality_id, zone_id)',
         'Un destino solo puede tener un precio para una modalidad.')
    ]

    @api.depends("destiny_id", "zone_id", "modality_id")
    def _compute_name(self):
        for record in self:
            record.name = record.destiny_id.name + ", " + record.zone_id.name + ", " + record.modality_id.name

    @api.onchange('destiny_id')
    def _onchange_destiny_id(self):
        if self.destiny_id:
            return {
                'domain': {
                    'zone_id': [('id', '=', self.destiny_id.zone_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'zone_id': []
                }
            }
