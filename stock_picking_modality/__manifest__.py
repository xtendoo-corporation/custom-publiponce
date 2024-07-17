# Copyright 2023 Salvador, Abraham (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Modality",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Salvador, Abraham (https://xtendoo.es)",
    "category": "Stock",
    "depends":
        [
            "stock",
            "contacts"
        ],
    "data":
        [
            "security/ir.model.access.csv",
            "views/picking_form_view.xml",
            "views/stock_move_view.xml",
            "views/stock_move_line_view.xml",
            "views/stock_picking_destiny_view.xml",
            "views/stock_picking_modality_view.xml",
            "views/stock_picking_modality_destiny_price_view.xml",
            "views/stock_picking_zone_view.xml",
            "views/res_partner_view.xml",
            "views/stock_move_planning_view.xml",
        ],
    'installable': True,
    'active': False,
}
