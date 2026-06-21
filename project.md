# Macros App — Project Architecture

## What This App Does

A personal food logging app where you can:
1. Search for any food using the USDA FoodData Central API
2. See its calories, protein, carbs, and fat
3. Log it to a MySQL database with a timestamp
4. View your food history filtered by date
5. Delete individual entries
6. See daily macro totals

---

## Architecture Overview

```
┌─────────────────────────────────┐
│         Macros.html             │  ← You open this in your browser
│         (Frontend)              │
│                                 │
│  • Search bar                   │
│  • Food result cards            │
│  • History panel + totals       │
└────────────┬────────────────────┘
             │
             │  Two separate API calls:
             │
    ┌────────▼────────┐        ┌──────────────────────────┐
    │   USDA API      │        │   server.py (Flask)       │
    │ (external)      │        │   localhost:5000          │
    │                 │        │                           │
    │ Searches food   │        │  POST   /log              │
    │ returns macros  │        │  GET    /history          │
    └─────────────────┘        │  DELETE /log/<id>         │
                               └────────────┬─────────────┘
                                            │
                               ┌────────────▼─────────────┐
                               │   MySQL Database          │
                               │   macros_app              │
                               │                           │
                               │   table: food_log         │
                               └──────────────────────────┘
```

---

## The Three Layers

### 1. Frontend — `Macros.html`

A single HTML file that runs entirely in your browser. It has no server of its own — you just open it as a file.

It makes two kinds of network calls:

| Call | Goes to | Purpose |
|---|---|---|
| Search food | USDA API (internet) | Get nutrition data for a food |
| Log / History / Delete | `localhost:5000` (your PC) | Save and retrieve your food log |

**Key JavaScript functions:**

- `fetchNutrition(query)` — calls the USDA API, gets food results
- `renderCards(foods)` — draws the food cards on screen
- `logFood(btn)` — sends a food entry to Flask to be saved in MySQL
- `loadHistory()` — fetches past entries from Flask and displays them
- `deleteEntry(id)` — tells Flask to delete a row from MySQL

---

### 2. Backend — `server.py` (Flask)

A lightweight Python web server that acts as the bridge between your HTML page and the MySQL database. It runs on your machine at `http://localhost:5000`.

Flask was chosen because:
- It is minimal and easy to understand
- Python has excellent MySQL support
- It can be started with a single command

**Why does the frontend need a backend at all?**
Browsers cannot connect to MySQL directly — they can only make HTTP requests. Flask translates those HTTP requests into SQL queries.

#### API Endpoints

---

**`POST /log`**

Saves a food entry to the database.

Request body (JSON):
```json
{
  "food_name": "Chicken Breast",
  "serving_qty": 100,
  "serving_unit": "g",
  "calories": 165,
  "protein": 31,
  "carbs": 0,
  "fat": 4
}
```

Response:
```json
{ "message": "Food logged successfully", "id": 42 }
```

What Flask does internally:
1. Reads the JSON body from the request
2. Validates that required fields are present
3. Opens a MySQL connection
4. Runs an `INSERT INTO food_log ...` SQL query
5. Returns the new row's ID

---

**`GET /history`**

Returns all logged food entries, newest first.

Optional filter: `GET /history?date=2026-06-21` returns only entries from that day.

Response:
```json
[
  {
    "id": 42,
    "food_name": "Chicken Breast",
    "calories": 165,
    "protein": 31,
    "carbs": 0,
    "fat": 4,
    "logged_at": "2026-06-21T02:31:00"
  }
]
```

What Flask does internally:
1. Checks if a `?date=` query param was passed
2. Runs either a filtered or unfiltered `SELECT` query
3. Converts `datetime` objects to strings (so JSON can handle them)
4. Returns the rows as a JSON array

---

**`DELETE /log/<id>`**

Deletes a single entry by its ID.

Example: `DELETE /log/42` removes the row where `id = 42`.

Response:
```json
{ "message": "Entry deleted" }
```

---

### 3. Database — MySQL (`macros_app`)

A MySQL database with a single table called `food_log`.

#### Table Schema

```sql
CREATE TABLE food_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    food_name   VARCHAR(255) NOT NULL,
    serving_qty FLOAT,
    serving_unit VARCHAR(50),
    calories    FLOAT,
    protein     FLOAT,
    carbs       FLOAT,
    fat         FLOAT,
    logged_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

| Column | Type | Description |
|---|---|---|
| `id` | INT, auto-increment | Unique ID for each entry |
| `food_name` | VARCHAR | Name of the food |
| `serving_qty` | FLOAT | Quantity (e.g. 100) |
| `serving_unit` | VARCHAR | Unit (e.g. "g") |
| `calories` | FLOAT | Calories in kcal |
| `protein` | FLOAT | Protein in grams |
| `carbs` | FLOAT | Carbohydrates in grams |
| `fat` | FLOAT | Fat in grams |
| `logged_at` | DATETIME | Automatically set to current date/time when inserted |

---

## Request Flow — Logging a Food

Here is exactly what happens when you click **"+ Log This Food"**:

```
1. You click the button in Macros.html
         ↓
2. JavaScript reads the food data stored in the button's data-food attribute
         ↓
3. JavaScript sends POST http://localhost:5000/log
   with the food data as JSON in the request body
         ↓
4. Flask (server.py) receives the request
         ↓
5. Flask opens a connection to MySQL
         ↓
6. Flask runs:  INSERT INTO food_log (...) VALUES (...)
         ↓
7. MySQL saves the row, assigns it an auto-increment ID
         ↓
8. Flask returns { "message": "Food logged successfully", "id": 42 }
         ↓
9. JavaScript changes the button to "✓ Logged"
         ↓
10. JavaScript calls loadHistory() to refresh the history panel
```

---

## Request Flow — Loading History

```
1. Page loads (or you change the date filter)
         ↓
2. JavaScript sends GET http://localhost:5000/history?date=2026-06-21
         ↓
3. Flask runs: SELECT * FROM food_log WHERE DATE(logged_at) = '2026-06-21'
         ↓
4. Flask returns a JSON array of all matching rows
         ↓
5. JavaScript calculates daily totals (sum of calories, protein, carbs, fat)
         ↓
6. JavaScript renders the totals banner and the list of entries
```

---

## USDA API

The USDA FoodData Central API is a free, public government food database.

- **Endpoint:** `https://api.nal.usda.gov/fdc/v1/foods/search`
- **Auth:** API key passed as a URL parameter (`?api_key=...`)
- **Request type:** GET
- **Sign up:** https://fdc.nal.usda.gov/api-guide.html

Nutrient IDs used from the USDA response:

| Nutrient | USDA ID |
|---|---|
| Calories (Energy) | 1008 |
| Protein | 1003 |
| Total Fat | 1004 |
| Carbohydrates | 1005 |

---

## File Structure

```
macros-app/
├── Macros.html       ← Frontend (open this in your browser)
├── server.py         ← Python Flask backend (run with: python server.py)
├── requirements.txt  ← Python package dependencies
├── project.md        ← This file
├── README.md         ← Original readme
├── index.html        ← Original version of the app
├── script.js         ← Original JS (not used by Macros.html)
└── style.css         ← Original CSS (not used by Macros.html)
```

---

## How to Run the App

**Every time you want to use the app:**

1. Open a terminal in the project folder and start the backend:
   ```
   python server.py
   ```
   Leave this terminal open. You should see:
   ```
   ✅ Macros backend running at http://localhost:5000
   ```

2. Open `Macros.html` in your browser (double-click it).

3. Search for food, log entries, and view your history.

**To stop the backend:** press `Ctrl+C` in the terminal.

---

## Python Dependencies

Installed via: `pip install flask flask-cors mysql-connector-python`

| Package | Purpose |
|---|---|
| `flask` | Web framework that handles HTTP routes |
| `flask-cors` | Allows the HTML file to make requests to Flask (CORS policy) |
| `mysql-connector-python` | Official MySQL driver for Python |
