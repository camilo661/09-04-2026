"""
vehicle.py - Vehicle model representing a taxi/public transport unit
"""


class Vehicle:
    """
    Represents a public transport vehicle operating in Pasto city.
    """

    STATUS_AVAILABLE = "disponible"
    STATUS_BUSY = "ocupado"
    STATUS_EN_ROUTE = "en_camino"

    def __init__(self, vehicle_id: int, driver_name: str, plate: str,
                 sector: str, latitude: float, longitude: float):
        self.vehicle_id = vehicle_id
        self.driver_name = driver_name
        self.plate = plate
        self.sector = sector
        self.latitude = latitude
        self.longitude = longitude
        self.status = self.STATUS_AVAILABLE
        self.current_order_id = None

    def assign_order(self, order_id: int):
        """Assign an order to this vehicle."""
        self.current_order_id = order_id
        self.status = self.STATUS_EN_ROUTE

    def complete_order(self):
        """Mark current order as completed."""
        self.current_order_id = None
        self.status = self.STATUS_AVAILABLE

    def to_dict(self) -> dict:
        """Serialize vehicle to dictionary."""
        return {
            "vehicle_id": self.vehicle_id,
            "driver_name": self.driver_name,
            "plate": self.plate,
            "sector": self.sector,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status,
            "current_order_id": self.current_order_id,
        }
