# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPlanning(TransactionCase):

    # some helpers
    def _create_customer(self):
        return self.env["res.partner"].create(
            {"name": "Test customer", "is_company": True}
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

    def _create_route(self, internal_location, transit_location, stock_picking_transit_type,
                      stock_picking_customers_type):
        if not self.env['ir.model'].search([('model', '=', 'stock.route')]):
            raise ValueError(
                "Model 'stock.route' is not available. Ensure the required module is installed and loaded.")

        route = self.env["stock.route"].create(
            {"name": "Test route", "warehouse_selectable": True, "product_selectable": True, "sale_selectable": True}
        )

        self.env["stock.rule"].create({
            "name": "Buy",
            "location_src_id": self.env.ref('stock.stock_location_suppliers').id,
            "location_dest_id": internal_location.id,
            "picking_type_id": self.env.ref('stock.picking_type_in').id,
            "route_id": route.id,
            "action": "buy",
            "procure_method": "make_to_order",
            "warehouse_id": stock_picking_transit_type.warehouse_id.id,
        })

        self.env["stock.rule"].create({
            "name": "Internal to Transit",
            "location_src_id": internal_location.id,
            "location_dest_id": transit_location.id,
            "picking_type_id": stock_picking_transit_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
            "warehouse_id": stock_picking_transit_type.warehouse_id.id,
        })

        self.env["stock.rule"].create({
            "name": "Transit to Customers",
            "location_src_id": transit_location.id,
            "location_dest_id": self.env.ref('stock.stock_location_customers').id,
            "picking_type_id": stock_picking_customers_type.id,
            "route_id": route.id,
            "action": "pull_push",
            "procure_method": "mts_else_mto",
            "warehouse_id": stock_picking_customers_type.warehouse_id.id,
        })

        return route

    def _create_stock_picking_transit_type(self, internal_location, transit_location):
        return self.env["stock.picking.type"].create(
            {"name": "Test picking type transit", "default_location_src_id": internal_location.id,
             "default_location_dest_id": transit_location.id, "sequence_code": "TST",
             "reservation_method": "at_confirm", "company_id": self.env.company.id,
             "code": "internal", "create_backorder": "always", "show_operations": False}
        )

    def _create_stock_picking_customers_type(self, transit_location):
        customers_location = self.env.ref('stock.stock_location_customers')
        return self.env["stock.picking.type"].create(
            {"name": "Test picking type customers", "default_location_src_id": transit_location.id,
             "default_location_dest_id": customers_location.id, "sequence_code": "TSC",
             "reservation_method": "at_confirm", "company_id": self.env.company.id,
             "code": "internal", "create_backorder": "always", "show_operations": False
             }
        )

    def _create_stock_rule(self, name, location_src, location_dest, picking_type):
        return self.env["stock.rule"].create({
            "name": name,
            "location_id": location_src.id,
            "location_src_id": location_src.id,
            "location_dest_id": location_dest.id,
            "picking_type_id": picking_type.id,
            "action": "pull_push",
            "procure_method": "make_to_order",
            "supply_method": "mts_else_mto",
            "move_type": "direct",
            "warehouse_id": picking_type.warehouse_id.id,
        })

    def _create_order(self, customer, product):
        return self.env["sale.order"].create(
            {"partner_id": customer.id, "order_line": [(0, 0, {"product_id": product.id})]}
        )

    def _create_product(self, customer, route):
        product = self.env["product.product"].create(
            {"name": "Test product", "type": "consu", "seller_ids": [(0, 0, {"partner_id": customer.id})],
             "detailed_type": "consu", "purchase_ok": True}
        )
        product.write({'route_ids': [(4, route.id)]})
        print(f"Product created: {product.name} (ID: {product.id}) with route: {route.name} (ID: {route.id})")
        return product

    def _create_stock_picking_modality(self, name, line_qty):
        return self.env['stock.picking.modality'].create({
            'name': name,
            'line_qty': line_qty,
        })

    def _create_stock_picking_destiny(self, name):
        return self.env['stock.picking.destiny'].create({
            'name': name,
        })

    def _create_stock_picking_zone(self, name, destiny_id):
        return self.env['stock.picking.zone'].create({
            'name': name,
            'destiny_id': destiny_id.id,
        })

    def _create_stock_picking_modality_destiny_price(self, modality_id, destiny_id, zone_id, price):
        return self.env['stock.picking.modality.destiny.price'].create({
            'modality_id': modality_id.id,
            'destiny_id': destiny_id.id,
            'zone_id': zone_id.id,
            'price': price,
        })

    def _create_order_with_line(self, customer, product, route, modality, destiny, zone, quantity, fee):

        product.write({'route_ids': [(4, route.id)]})

        return self.env['sale.order'].create({
            'partner_id': customer.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'route_id': route.id,
                'modality_id': modality.id,
                'destiny_id': destiny.id,
                'zone_id': zone.id,
                'product_uom_qty': quantity,
                'price_unit': fee.price,
            })]
        })

    def _confirm_purchase_order(self, order):
        purchase_order = self.env['purchase.order'].search([
            ('origin', '=', order.name),
        ], limit=1)
        print(f"Purchase order created: {purchase_order.name} (ID: {purchase_order.id})")

        # Check product and warehouse configurations
        for line in purchase_order.order_line:
            product = line.product_id
            print(f"Product: {product.name} (ID: {product.id})")
            for route in product.route_ids:
                print(f"Route: {route.name} (ID: {route.id})")
                for rule in route.rule_ids:
                    print(f"Rule: {rule.name} (ID: {rule.id})")
                    print(f"  Location Source: {rule.location_src_id.name} (ID: {rule.location_src_id.id})")
                    print(f"  Location Destination: {rule.location_dest_id.name} (ID: {rule.location_dest_id.id})")
                    print(f"  Picking Type: {rule.picking_type_id.name} (ID: {rule.picking_type_id.id})")

        purchase_order.button_confirm()
        print(f"Purchase order confirmed: {purchase_order.name} (ID: {purchase_order.id})")

        picking = purchase_order.picking_ids
        print(f"Picking created: {picking.name} (ID: {picking.id})")
        picking.action_confirm()
        print(f"Picking confirmed: {picking.name} (ID: {picking.id})")
        picking.action_assign()
        print(f"Picking assigned: {picking.name} (ID: {picking.id})")

        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
            print(f"Move {move.id} quantity done set to {move.quantity_done}")

        picking.button_validate()
        print(f"Picking validated: {picking.name} (ID: {picking.id})")

    def _confirm_assigned_picking(self, order):
        pickings = self.env['stock.picking'].search([('origin', '=', order.name)])
        print(f"All pickings related to order {order.name}: {[picking.id for picking in pickings]}")
        for picking in pickings:
            print(f"Picking ID: {picking.id}")
            print(f"Picking Name: {picking.name}")
            print(f"Picking State: {picking.state}")
            print(f"Picking Origin: {picking.origin}")
            print(f"Picking Partner: {picking.partner_id.name}")
        picking = order.picking_ids.filtered(lambda p: p.state == 'assigned')
        if not picking:
            raise ValueError("No assigned picking found for the order.")

        picking.action_confirm()

        # Ensure there are move lines to assign
        if not picking.move_ids_without_package:
            raise ValueError("Nothing to check the availability for.")

        picking.action_assign()
        for move in picking.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        picking.button_validate()

    def test_planning_state(self):
        customer = self._create_customer()
        print(f"Customer created: {customer.name} (ID: {customer.id})")

        warehouse = self._create_warehouse()
        print(f"Warehouse created: {warehouse.name} (ID: {warehouse.id})")

        internal_location = self._create_internal_location(warehouse)
        print(f"Internal location created: {internal_location.name} (ID: {internal_location.id})")

        transit_location = self._create_transit_location(warehouse)
        print(f"Transit location created: {transit_location.name} (ID: {transit_location.id})")

        stock_picking_transit_type = self._create_stock_picking_transit_type(internal_location, transit_location)
        print(
            f"Stock picking transit type created: {stock_picking_transit_type.name} (ID: {stock_picking_transit_type.id})")

        stock_picking_customers_type = self._create_stock_picking_customers_type(transit_location)
        print(
            f"Stock picking customers type created: {stock_picking_customers_type.name} (ID: {stock_picking_customers_type.id})")

        route = self._create_route(internal_location, transit_location, stock_picking_transit_type,
                                   stock_picking_customers_type)
        print(f"Route created: {route.name} (ID: {route.id})")

        product = self._create_product(customer, route)
        print(f"Product created: {product.name} (ID: {product.id})")

        modality = self._create_stock_picking_modality('Test modality', 1)
        print(f"Modality created: {modality.name} (ID: {modality.id})")

        destiny = self._create_stock_picking_destiny('Test destiny')
        print(f"Destiny created: {destiny.name} (ID: {destiny.id})")

        zone = self._create_stock_picking_zone('Test zone', destiny)
        print(f"Zone created: {zone.name} (ID: {zone.id})")

        destiny.write({'zone_id': [(4, zone.id)]})
        print(f"Zone {zone.name} (ID: {zone.id}) added to Destiny {destiny.name} (ID: {destiny.id})")

        fee = self._create_stock_picking_modality_destiny_price(modality, destiny, zone, 10)
        print(f"Fee created: {fee.name} (ID: {fee.id}) - Price: {fee.price}")

        order = self._create_order_with_line(customer, product, route, modality, destiny, zone, 33, fee)
        print(f"Order created: {order.name} (ID: {order.id})")

        order.action_confirm()
        print(f"Order confirmed: {order.name} (ID: {order.id})")

        self._confirm_purchase_order(order)
        print(f"Purchase order created and confirmed for order: {order.name} (ID: {order.id})")

        self._confirm_assigned_picking(order)
        print(f"First assigned picking confirmed for order: {order.name} (ID: {order.id})")

        self._confirm_assigned_picking(order)
        print(f"Second assigned picking confirmed for order: {order.name} (ID: {order.id})")



