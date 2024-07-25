# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_resource = fields.Boolean(
        string='Is Resource',
        default=False,
    )
    color = fields.Integer(
        string='Color Index',
    )
