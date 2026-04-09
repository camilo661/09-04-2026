"""
app.py - Flask backend application for TaxisDrive.
Exposes REST API endpoints consumed by the frontend.
"""

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

from backend.fleet_manager import FleetManager
from backend.order_manager import OrderManager

# ------------------------------------------------------------------ #
#  Application setup                                                   #
# ------------------------------------------------------------------ #

app = Flask(
    __name__,
    template_folder="frontend/templates",
    static_folder="frontend/static",
)
CORS(app)

# Singleton managers (shared state for the session)
fleet_manager = FleetManager()
order_manager = OrderManager(fleet_manager)


# ------------------------------------------------------------------ #
#  Frontend route                                                      #
# ------------------------------------------------------------------ #

@app.route("/")
def index():
    """Serve the main SPA page."""
    return render_template("index.html")


# ------------------------------------------------------------------ #
#  Fleet endpoints                                                     #
# ------------------------------------------------------------------ #

@app.route("/api/fleet", methods=["GET"])
def get_fleet():
    """Return all vehicles in the fleet."""
    fleet_manager.simulate_vehicle_movement()
    return jsonify({
        "vehicles": fleet_manager.get_fleet_data(),
        "stats": fleet_manager.get_fleet_stats(),
    })


@app.route("/api/fleet/stats", methods=["GET"])
def get_fleet_stats():
    """Return fleet statistics only."""
    return jsonify(fleet_manager.get_fleet_stats())


@app.route("/api/sectors", methods=["GET"])
def get_sectors():
    """Return all sectors and neighborhoods."""
    return jsonify({
        "sectors": fleet_manager.get_all_sectors(),
        "neighborhoods": fleet_manager.get_neighborhoods(),
    })


# ------------------------------------------------------------------ #
#  Order endpoints                                                     #
# ------------------------------------------------------------------ #

@app.route("/api/orders", methods=["GET"])
def get_orders():
    """Return all orders."""
    return jsonify({"orders": order_manager.get_all_orders()})


@app.route("/api/orders/active", methods=["GET"])
def get_active_orders():
    """Return only active orders."""
    return jsonify({"orders": order_manager.get_active_orders()})


@app.route("/api/orders", methods=["POST"])
def create_order():
    """Create a new transport order."""
    data = request.get_json(force=True)

    required = ["user_name", "neighborhood", "address", "destination"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Campo requerido: {field}"}), 400

    result = order_manager.create_order(
        user_name=data["user_name"].strip(),
        neighborhood=data["neighborhood"].strip(),
        address=data["address"].strip(),
        destination=data["destination"].strip(),
    )
    return jsonify(result), 201


@app.route("/api/orders/<int:order_id>/complete", methods=["PUT"])
def complete_order(order_id: int):
    """Mark an order as completed."""
    result = order_manager.complete_order(order_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@app.route("/api/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_order(order_id: int):
    """Cancel an order."""
    result = order_manager.cancel_order(order_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id: int):
    """Get a specific order by id."""
    result = order_manager.get_order(order_id)
    if "error" in result:
        return jsonify(result), 404
    return jsonify(result)


# ------------------------------------------------------------------ #
#  Run                                                                 #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
