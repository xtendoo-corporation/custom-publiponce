# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPlanning(TransactionCase):

    # some helpers
    def _create_customer(self):
        return self.env["res.partner"].create(
            {"name": "Test customer", "customer": True}
        )

    def _create_warehouse(self):
        return self.env["stock.warehouse"].create(
            {"name": "Test warehouse", "code": "TWH"}
        )

    def _create_internal_location(self, warehouse):
        return self.env["stock.location"].create(
            {"name": "Internal location", "usage": "internal", "location_id": warehouse.view_location_id.id}
        )

    def _create_transit_location(self, warehouse):
        return self.env["stock.location"].create(
            {"name": "Transit location", "usage": "transit", "location_id": warehouse.view_location_id.id}
        )

    def _create_route(self):
        return self.env["stock.location.route"].create(
            {"name": "Test route", "warehouse_selectable": True}
        )

    def _create_stock_picking_transit_type(self, internal_location, transit_location):
        return self.env["stock.picking.type"].create(
            {"name": "Test picking type", "default_location_src_id": internal_location.id, "default_location_dest_id": transit_location.id, "sequence_code": "TST"}
        )

    def _create_order(self, customer, product):
        return self.env["sale.order"].create(
            {"partner_id": customer.id, "order_line": [(0, 0, {"product_id": product.id})]}
        )

    def _create_product(self, customer):
        return self.env["product.product"].create(
            {"name": "Test product", "type": "product", "seller_ids": [(0, 0, {"partner_id": customer.id})]}
        )

    def test_planning_state(self):
        customer = self._create_customer()
        warehouse = self._create_warehouse()
        internal_location = self._create_internal_location(warehouse)
        transit_location = self._create_transit_location(warehouse)
        stock_picking_transit_type = self._create_stock_picking_transit_type(internal_location, transit_location)

        route = self._create_route()
        product = self._create_product(customer)


