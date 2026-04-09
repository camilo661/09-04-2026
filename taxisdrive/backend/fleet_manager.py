"""
fleet_manager.py - Manages the vehicle fleet using a DoublyLinkedList.
Seeds 10 simulated vehicles across Pasto city sectors.
"""

import math
import random
from backend.doubly_linked_list import DoublyLinkedList
from backend.vehicle import Vehicle

# Pasto city sectors with approximate coordinates
PASTO_SECTORS = {
    "Centro": (1.2136, -77.2811),
    "Lorenzo": (1.2200, -77.2750),
    "Torobajo": (1.2080, -77.2900),
    "Chambú": (1.2250, -77.2700),
    "Corazón de Jesús": (1.2050, -77.2780),
    "San Ignacio": (1.2170, -77.2840),
    "Aranda": (1.2300, -77.2650),
    "La Minga": (1.2020, -77.2950),
    "Jamondino": (1.1980, -77.2870),
    "Riveras de Mijitayo": (1.2350, -77.2720),
}

PASTO_NEIGHBORHOODS = {
    "Centro": ["Centro Histórico", "Plaza de Nariño", "San Juan de Dios"],
    "Lorenzo": ["San Lorenzo", "El Tejar", "Villa del Norte"],
    "Torobajo": ["Torobajo", "La Estrella", "El Rosario"],
    "Chambú": ["Chambú", "Los Pinos", "El Bosque"],
    "Corazón de Jesús": ["Corazón de Jesús", "El Calvario", "San Felipe"],
    "San Ignacio": ["San Ignacio", "La Merced", "Santa Bárbara"],
    "Aranda": ["Aranda", "Villa Lucía", "Los Álamos"],
    "La Minga": ["La Minga", "El Lago", "Villa del Sol"],
    "Jamondino": ["Jamondino", "San Martin", "El Porvenir"],
    "Riveras de Mijitayo": ["Riveras de Mijitayo", "El Mirador", "Las Palmas"],
}

DRIVER_NAMES = [
    "Carlos Muñoz", "Pedro Enríquez", "Luis Guerrero", "Andrés Coral",
    "Fabián Narváez", "José Bastidas", "Miguel Benavides", "Hernán Chávez",
    "Ricardo Delgado", "Iván Rosero",
]

PLATES = [
    "ABC123", "DEF456", "GHI789", "JKL012", "MNO345",
    "PQR678", "STU901", "VWX234", "YZA567", "BCD890",
]


class FleetManager:
    """
    Manages the entire vehicle fleet using a Doubly Linked List.
    Provides methods for vehicle assignment and fleet monitoring.
    """

    def __init__(self):
        self.fleet = DoublyLinkedList()
        self._seed_vehicles()

    def _seed_vehicles(self):
        """Initialize 10 simulated vehicles across Pasto sectors."""
        sectors = list(PASTO_SECTORS.keys())
        for i in range(10):
            sector = sectors[i % len(sectors)]
            base_lat, base_lon = PASTO_SECTORS[sector]
            # Add slight random offset to simulate real positions
            lat = base_lat + random.uniform(-0.005, 0.005)
            lon = base_lon + random.uniform(-0.005, 0.005)
            vehicle = Vehicle(
                vehicle_id=i + 1,
                driver_name=DRIVER_NAMES[i],
                plate=PLATES[i],
                sector=sector,
                latitude=round(lat, 6),
                longitude=round(lon, 6),
            )
            self.fleet.append(vehicle)

    def get_sector_for_neighborhood(self, neighborhood: str) -> str | None:
        """Find which sector a neighborhood belongs to."""
        for sector, neighborhoods in PASTO_NEIGHBORHOODS.items():
            for nb in neighborhoods:
                if neighborhood.lower() in nb.lower():
                    return sector
        return None

    def get_all_sectors(self) -> list[str]:
        """Return all available sectors."""
        return list(PASTO_SECTORS.keys())

    def get_neighborhoods(self) -> dict:
        """Return all neighborhoods grouped by sector."""
        return PASTO_NEIGHBORHOODS

    def get_sector_coordinates(self, sector: str) -> tuple | None:
        """Get lat/lon for a sector."""
        return PASTO_SECTORS.get(sector)

    def find_best_vehicle(self, sector: str, neighborhood: str) -> Vehicle | None:
        """Find the nearest available vehicle for the given sector/neighborhood."""
        coords = PASTO_SECTORS.get(sector)
        if not coords:
            return None
        lat, lon = coords
        return self.fleet.find_nearest_available(lat, lon, sector)

    def estimate_time(self, vehicle: Vehicle, sector: str) -> int:
        """Estimate arrival time in minutes based on distance."""
        target = PASTO_SECTORS.get(sector)
        if not target:
            return 10
        dist = math.sqrt(
            (vehicle.latitude - target[0]) ** 2 +
            (vehicle.longitude - target[1]) ** 2
        )
        # Rough conversion: 0.01 degree ≈ 1 km, avg speed 20 km/h
        minutes = int((dist / 0.01) * 3) + 2
        return max(2, min(minutes, 25))

    def assign_vehicle_to_order(self, order) -> Vehicle | None:
        """Find and assign the best vehicle for an order."""
        vehicle = self.find_best_vehicle(order.sector, order.neighborhood)
        if vehicle:
            estimated = self.estimate_time(vehicle, order.sector)
            vehicle.assign_order(order.order_id)
            order.assign_vehicle(vehicle.vehicle_id, estimated)
        return vehicle

    def complete_order(self, vehicle_id: int):
        """Release vehicle after order completion."""
        node = self.fleet.find_by_id(vehicle_id)
        if node:
            node.vehicle.complete_order()

    def get_fleet_data(self) -> list[dict]:
        """Get serialized fleet data."""
        return [v.to_dict() for v in self.fleet.get_all_vehicles()]

    def get_fleet_stats(self) -> dict:
        """Get fleet statistics."""
        return self.fleet.get_stats()

    def simulate_vehicle_movement(self):
        """Simulate slight movement of all vehicles."""
        current = self.fleet.head
        while current:
            v = current.vehicle
            v.latitude += random.uniform(-0.002, 0.002)
            v.longitude += random.uniform(-0.002, 0.002)
            v.latitude = round(v.latitude, 6)
            v.longitude = round(v.longitude, 6)
            current = current.next
