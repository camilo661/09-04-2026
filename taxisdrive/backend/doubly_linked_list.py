"""
doubly_linked_list.py - Doubly linked list structure to manage vehicles
This is the core data structure required by the assignment.
"""

import math
from backend.node import Node
from backend.vehicle import Vehicle


class DoublyLinkedList:
    """
    Doubly linked list that stores and manages Vehicle nodes.
    Supports traversal in both directions, insertion, removal,
    and sector-based searching.
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    # ------------------------------------------------------------------ #
    #  Basic operations                                                    #
    # ------------------------------------------------------------------ #

    def append(self, vehicle: Vehicle):
        """Add a vehicle node at the end of the list."""
        new_node = Node(vehicle)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1

    def prepend(self, vehicle: Vehicle):
        """Add a vehicle node at the beginning of the list."""
        new_node = Node(vehicle)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.length += 1

    def _traverse_to_index(self, index: int) -> Node:
        """Traverse list to a given index and return the node."""
        current_node = self.head
        i = 0
        while i != index:
            current_node = current_node.next
            i += 1
        return current_node

    def insert(self, index: int, vehicle: Vehicle):
        """Insert a vehicle at a specific index position."""
        if index == 0:
            self.prepend(vehicle)
        elif index >= self.length:
            self.append(vehicle)
        else:
            new_node = Node(vehicle)
            leader = self._traverse_to_index(index - 1)
            follower = leader.next
            leader.next = new_node
            new_node.prev = leader
            new_node.next = follower
            follower.prev = new_node
            self.length += 1

    def remove(self, index: int):
        """Remove a vehicle node at the given index."""
        if index == 0:
            self.head = self.head.next
            if self.head:
                self.head.prev = None
        elif index == self.length - 1:
            self.tail = self.tail.prev
            if self.tail:
                self.tail.next = None
        else:
            leader = self._traverse_to_index(index - 1)
            node_to_remove = leader.next
            follower = node_to_remove.next
            leader.next = follower
            follower.prev = leader
        self.length -= 1

    # ------------------------------------------------------------------ #
    #  Search & filter operations                                          #
    # ------------------------------------------------------------------ #

    def find_by_id(self, vehicle_id: int) -> Node | None:
        """Find a node by vehicle id."""
        current = self.head
        while current:
            if current.vehicle.vehicle_id == vehicle_id:
                return current
            current = current.next
        return None

    def get_vehicles_by_sector(self, sector: str) -> list[Vehicle]:
        """Return all available vehicles in the given sector."""
        result = []
        current = self.head
        while current:
            v = current.vehicle
            if v.sector.lower() == sector.lower() and v.status == Vehicle.STATUS_AVAILABLE:
                result.append(v)
            current = current.next
        return result

    def find_nearest_available(self, lat: float, lon: float,
                               sector: str) -> Vehicle | None:
        """
        Traverse the list to find the nearest available vehicle.
        Priority: same sector first, then closest by Euclidean distance.
        """
        best_vehicle = None
        best_distance = float("inf")

        current = self.head
        while current:
            v = current.vehicle
            if v.status == Vehicle.STATUS_AVAILABLE:
                distance = math.sqrt(
                    (v.latitude - lat) ** 2 + (v.longitude - lon) ** 2
                )
                # Sector bonus: halve distance for same sector
                if v.sector.lower() == sector.lower():
                    distance *= 0.5
                if distance < best_distance:
                    best_distance = distance
                    best_vehicle = v
            current = current.next

        return best_vehicle

    def get_all_vehicles(self) -> list[Vehicle]:
        """Return all vehicles as a list (forward traversal)."""
        result = []
        current = self.head
        while current:
            result.append(current.vehicle)
            current = current.next
        return result

    def get_all_vehicles_reversed(self) -> list[Vehicle]:
        """Return all vehicles in reverse order (backward traversal)."""
        result = []
        current = self.tail
        while current:
            result.append(current.vehicle)
            current = current.prev
        return result

    def update_vehicle_status(self, vehicle_id: int, status: str):
        """Update the status of a specific vehicle."""
        node = self.find_by_id(vehicle_id)
        if node:
            node.vehicle.status = status

    def get_available_count(self) -> int:
        """Count available vehicles."""
        count = 0
        current = self.head
        while current:
            if current.vehicle.status == Vehicle.STATUS_AVAILABLE:
                count += 1
            current = current.next
        return count

    def get_stats(self) -> dict:
        """Return fleet statistics."""
        total = self.length
        available = 0
        busy = 0
        en_route = 0

        current = self.head
        while current:
            s = current.vehicle.status
            if s == Vehicle.STATUS_AVAILABLE:
                available += 1
            elif s == Vehicle.STATUS_BUSY:
                busy += 1
            elif s == Vehicle.STATUS_EN_ROUTE:
                en_route += 1
            current = current.next

        return {
            "total": total,
            "available": available,
            "busy": busy,
            "en_route": en_route,
        }
