from flask import Flask, render_template, request, jsonify
import heapq

app = Flask(__name__)


# ============================================================
# BUILDING MAP
# ============================================================

# Each connection represents a corridor between two locations.
# The number is the distance in meters.

GRAPH = {
    "Main Entrance": {
        "Room 101": 4
    },

    "Room 101": {
        "Main Entrance": 4,
        "Room 102": 4,
        "Room 103": 4
    },

    "Room 102": {
        "Room 101": 4,
        "Room 104": 4
    },

    "Room 103": {
        "Room 101": 4,
        "Room 104": 4
    },

    "Room 104": {
        "Room 102": 4,
        "Room 103": 4
    }
}


# ============================================================
# DIJKSTRA SHORTEST PATH ALGORITHM
# ============================================================

def find_shortest_path(start, destination):

    # Priority queue
    # (distance, current_node, path)
    priority_queue = [
        (0, start, [start])
    ]

    # Stores the shortest known distance
    distances = {
        start: 0
    }

    while priority_queue:

        current_distance, current_node, path = heapq.heappop(
            priority_queue
        )

        # Destination reached
        if current_node == destination:

            return current_distance, path

        # Ignore an older/larger distance
        if current_distance > distances.get(
            current_node,
            float("inf")
        ):
            continue

        # Visit connected locations
        for neighbour, weight in GRAPH.get(
            current_node,
            {}
        ).items():

            new_distance = (
                current_distance + weight
            )

            # Found a shorter route
            if new_distance < distances.get(
                neighbour,
                float("inf")
            ):

                distances[neighbour] = new_distance

                new_path = path + [neighbour]

                heapq.heappush(
                    priority_queue,
                    (
                        new_distance,
                        neighbour,
                        new_path
                    )
                )

    # No route found
    return None, None


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ============================================================
# FIND ROUTE API
# ============================================================

@app.route(
    "/find-route",
    methods=["POST"]
)
def find_route():

    try:

        # ----------------------------------------------------
        # Read JSON sent by index.html
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        )

        print(
            "Received data:",
            data
        )


        # ----------------------------------------------------
        # Check whether JSON was received
        # ----------------------------------------------------

        if not data:

            return jsonify({
                "success": False,
                "message": "No JSON data received."
            }), 400


        # ----------------------------------------------------
        # Get starting point
        # ----------------------------------------------------

        start = data.get(
            "start"
        )


        # ----------------------------------------------------
        # Get destination
        # ----------------------------------------------------

        destination = data.get(
            "destination"
        )


        print(
            "Start:",
            start
        )

        print(
            "Destination:",
            destination
        )


        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not start or not destination:

            return jsonify({
                "success": False,
                "message": "Starting point and destination are required."
            }), 400


        # ----------------------------------------------------
        # Check whether locations exist
        # ----------------------------------------------------

        if start not in GRAPH:

            return jsonify({
                "success": False,
                "message": f"Unknown starting location: {start}"
            }), 400


        if destination not in GRAPH:

            return jsonify({
                "success": False,
                "message": f"Unknown destination: {destination}"
            }), 400


        # ----------------------------------------------------
        # Same location check
        # ----------------------------------------------------

        if start == destination:

            return jsonify({
                "success": False,
                "message": "Starting point and destination cannot be the same."
            }), 400


        # ----------------------------------------------------
        # Calculate shortest route
        # ----------------------------------------------------

        distance, path = find_shortest_path(
            start,
            destination
        )


        # ----------------------------------------------------
        # No route found
        # ----------------------------------------------------

        if path is None:

            return jsonify({
                "success": False,
                "message": "No route found between the selected locations."
            }), 404


        # ----------------------------------------------------
        # Successful route
        # ----------------------------------------------------

        result = {

            "success": True,

            "message": "Route found",

            "distance": distance,

            "path": path

        }


        print(
            "Route result:",
            result
        )


        return jsonify(
            result
        )


    except Exception as error:

        print(
            "ERROR:",
            error
        )


        return jsonify({

            "success": False,

            "message": "Server error while calculating route.",

            "error": str(error)

        }), 500


# ============================================================
# RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )