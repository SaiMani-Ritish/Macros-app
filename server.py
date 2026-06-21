from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow requests from the HTML file

# ── Database Configuration ─────────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password@123",  # ← Change this to your MySQL root password
    "database": "macros_app"
}
# ──────────────────────────────────────────────────────────────────────────


def get_connection():
    """Return a new MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


# ── POST /log ──────────────────────────────────────────────────────────────
# Saves a food entry to the database.
# Expected JSON body:
#   { food_name, serving_qty, serving_unit, calories, protein, carbs, fat }
@app.route("/log", methods=["POST"])
def log_food():
    data = request.get_json()
    required = ["food_name", "calories", "protein", "carbs", "fat"]

    if not data or not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO food_log
                (food_name, serving_qty, serving_unit, calories, protein, carbs, fat)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["food_name"],
                data.get("serving_qty"),
                data.get("serving_unit"),
                data["calories"],
                data["protein"],
                data["carbs"],
                data["fat"],
            ),
        )
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({"message": "Food logged successfully", "id": new_id}), 201

    except Error as e:
        return jsonify({"error": str(e)}), 500


# ── GET /history ───────────────────────────────────────────────────────────
# Returns all logged food entries, newest first.
# Optional query param: ?date=YYYY-MM-DD  →  filter by a specific day
@app.route("/history", methods=["GET"])
def get_history():
    date_filter = request.args.get("date")  # e.g. ?date=2026-06-21

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if date_filter:
            cursor.execute(
                """
                SELECT * FROM food_log
                WHERE DATE(logged_at) = %s
                ORDER BY logged_at DESC
                """,
                (date_filter,),
            )
        else:
            cursor.execute("SELECT * FROM food_log ORDER BY logged_at DESC")

        rows = cursor.fetchall()

        # Convert datetime objects to ISO strings for JSON serialization
        for row in rows:
            if isinstance(row.get("logged_at"), datetime):
                row["logged_at"] = row["logged_at"].isoformat()

        cursor.close()
        conn.close()
        return jsonify(rows), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


# ── DELETE /log/<id> ───────────────────────────────────────────────────────
# Deletes a specific food log entry by its ID.
@app.route("/log/<int:entry_id>", methods=["DELETE"])
def delete_log(entry_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM food_log WHERE id = %s", (entry_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()

        if affected == 0:
            return jsonify({"error": "Entry not found"}), 404
        return jsonify({"message": "Entry deleted"}), 200

    except Error as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("✅ Macros backend running at http://localhost:5000")
    app.run(debug=True, port=5000)
