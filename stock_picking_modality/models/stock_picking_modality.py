# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class StockPickingModality(models.Model):
    _name = 'stock.picking.modality'

    name = fields.Char(
        string='Name',
    )
    price = fields.Float(
        string='Price',
    )
    # modality = fields.One2many(
    #     comodel_name='stock.picking.line',
    #     inverse_name='modality_id',
    #     string='Modality',
    # )

