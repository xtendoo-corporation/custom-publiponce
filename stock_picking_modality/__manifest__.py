# Copyright 2023 Jaime Millan (https://xtendoo.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Stock Picking Modality",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Jaime Millan (https://xtendoo.es)",
    "category": "Stock",
    "depends":
        [
            "stock",
        ],
    "data":
        [
            "security/ir.model.access.csv",
            "views/stock_picking_modality_view.xml",
            "views/view_picking_form.xml",
            "views/view_stock_move.xml",
            # "views/view_stock_move_line.xml",
            "views/rate_picking_destiny_view.xml",
            "views/rate_picking_modality_price_view.xml",
        ],
    'installable': True,
    'active': False,
}
