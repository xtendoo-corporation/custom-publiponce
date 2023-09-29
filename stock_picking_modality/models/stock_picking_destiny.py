# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingDestiny(models.Model):
    _name = 'stock.picking.destiny'

    name = fields.Char(
        string='Name',
        readonly=False,
        store=True,
    )
    # modality_price_ids = fields.One2many(
    #     comodel_name='rate.picking.modality.price',
    #     inverse_name='rate_id',
    #     string='Modalities and Prices',
    #     readonly=False,
    # )
