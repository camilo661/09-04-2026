"""
node.py - Node definition for the doubly linked list structure
"""


class Node:
    """
    Represents a single node in the doubly linked list.
    Each node holds a vehicle object and pointers to previous/next nodes.
    """

    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.next = None
        self.prev = None
