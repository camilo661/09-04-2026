"""
order.py - Order model representing a transport request from a user
"""

from datetime import datetime


class Order:
    """
    Represents a transport order placed by a user in Pasto city.
    """

    STATUS_PENDING = "pendiente"
    STATUS_ASSIGNED = "asignado"
    STATUS_COMPLETED = "completado"
    STATUS_CANCELLED = "cancelado"

    def __init__(self, order_id: int, user_name: str, neighborhood: str,
                 address: str, destination: str, sector: str):
        self.order_id = order_id
        self.user_name = user_name
        self.neighborhood = neighborhood
        self.address = address
        self.destination = destination
        self.sector = sector
        self.status = self.STATUS_PENDING
        self.assigned_vehicle_id = None
        self.created_at = datetime.now().strftime("%H:%M:%S")
        self.estimated_time = None

    def assign_vehicle(self, vehicle_id: int, estimated_time: int):
        """Assign a vehicle to this order."""
        self.assigned_vehicle_id = vehicle_id
        self.estimated_time = estimated_time
        self.status = self.STATUS_ASSIGNED

    def complete(self):
        """Mark order as completed."""
        self.status = self.STATUS_COMPLETED

    def cancel(self):
        """Cancel this order."""
        self.status = self.STATUS_CANCELLED

    def to_dict(self) -> dict:
        """Serialize order to dictionary."""
        return {
            "order_id": self.order_id,
            "user_name": self.user_name,
            "neighborhood": self.neighborhood,
            "address": self.address,
            "destination": self.destination,
            "sector": self.sector,
            "status": self.status,
            "assigned_vehicle_id": self.assigned_vehicle_id,
            "created_at": self.created_at,
            "estimated_time": self.estimated_time,
        }
