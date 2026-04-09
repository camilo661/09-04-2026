"""
order_manager.py - Manages orders using a list and integrates with FleetManager.
"""

from backend.order import Order
from backend.fleet_manager import FleetManager


class OrderManager:
    """
    Manages the lifecycle of transport orders.
    Coordinates with FleetManager to assign vehicles.
    """

    def __init__(self, fleet_manager: FleetManager):
        self.fleet_manager = fleet_manager
        self.orders: dict[int, Order] = {}
        self._next_id = 1

    def create_order(self, user_name: str, neighborhood: str,
                     address: str, destination: str) -> dict:
        """
        Create a new transport order.
        Automatically determines sector and finds nearest vehicle.
        """
        sector = self.fleet_manager.get_sector_for_neighborhood(neighborhood)
        if not sector:
            # Default to Centro if sector not found
            sector = "Centro"

        order = Order(
            order_id=self._next_id,
            user_name=user_name,
            neighborhood=neighborhood,
            address=address,
            destination=destination,
            sector=sector,
        )
        self._next_id += 1
        self.orders[order.order_id] = order

        # Attempt to assign vehicle immediately
        vehicle = self.fleet_manager.assign_vehicle_to_order(order)

        result = order.to_dict()
        result["vehicle"] = vehicle.to_dict() if vehicle else None
        result["message"] = (
            f"Vehículo asignado. Llegará en {order.estimated_time} min."
            if vehicle
            else "No hay vehículos disponibles en este momento."
        )
        return result

    def complete_order(self, order_id: int) -> dict:
        """Mark an order as completed."""
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Orden no encontrada"}
        if order.assigned_vehicle_id:
            self.fleet_manager.complete_order(order.assigned_vehicle_id)
        order.complete()
        return order.to_dict()

    def cancel_order(self, order_id: int) -> dict:
        """Cancel a pending or assigned order."""
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Orden no encontrada"}
        if order.assigned_vehicle_id:
            self.fleet_manager.complete_order(order.assigned_vehicle_id)
        order.cancel()
        return order.to_dict()

    def get_order(self, order_id: int) -> dict:
        """Get a specific order."""
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Orden no encontrada"}
        return order.to_dict()

    def get_all_orders(self) -> list[dict]:
        """Get all orders sorted by id descending."""
        return [o.to_dict() for o in sorted(
            self.orders.values(), key=lambda x: x.order_id, reverse=True
        )]

    def get_active_orders(self) -> list[dict]:
        """Get only active (pending/assigned) orders."""
        return [
            o.to_dict() for o in self.orders.values()
            if o.status in (Order.STATUS_PENDING, Order.STATUS_ASSIGNED)
        ]
