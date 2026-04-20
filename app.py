from flask import Flask, render_template_string, request, Response, redirect, url_for
import sqlite3
import os
import networkx as nx

from virtual import (
    ALL_COLLEGES, get_locations_for, get_connections_for,
    build_graph_for_college, generate_map
)

app = Flask(__name__)
DB_NAME = "campus.db"

# ---------- Database initialization ----------
def init_db():
    if os.path.exists(DB_NAME):
        return
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS colleges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        college_id INTEGER,
        loc_key TEXT,
        name TEXT,
        lat REAL,
        lon REAL,
        type TEXT,
        details TEXT,
        FOREIGN KEY(college_id) REFERENCES colleges(id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS connections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        college_id INTEGER,
        loc_a TEXT,
        loc_b TEXT,
        FOREIGN KEY(college_id) REFERENCES colleges(id)
    )""")

    colleges = [(c, "") for c in ALL_COLLEGES]
    cur.executemany("INSERT INTO colleges (name, city) VALUES (?, ?)", colleges)
    conn.commit()

    cur.execute("SELECT id, name FROM colleges")
    db_map = {row[1]: row[0] for row in cur.fetchall()}

    for cname in ALL_COLLEGES:
        cid = db_map[cname]
        locs = get_locations_for(cname)
        import json
        for key, meta in locs.items():
            name = meta.get("name", key)
            lat, lon = meta.get("coords", (0.0, 0.0))
            typ = meta.get("type", "")
            details_json = json.dumps(meta.get("details", {}))
            cur.execute("""
                INSERT INTO locations (college_id, loc_key, name, lat, lon, type, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cid, key, name, lat, lon, typ, details_json))

        conns = get_connections_for(cname)
        for a, b in conns:
            cur.execute("INSERT INTO connections (college_id, loc_a, loc_b) VALUES (?, ?, ?)", (cid, a, b))
        conn.commit()

    conn.close()
    print("✅ campus.db created and populated with ADCET (real) + synthetic colleges.")

init_db()

# ---------- Templates ----------
WELCOME_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Virtual Campus Guide</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: url('{{ url_for('static', filename='bg_welcome.jpg') }}') no-repeat center center fixed;
      background-size: cover;
      text-align: center;
      margin: 0;
      color: white;
    }
    header {
      background: rgba(30,58,138,0.85);
      padding: 20px;
      font-size: 26px;
      font-weight: bold;
      color: #fff;
      text-shadow: 1px 1px 4px #000;
    }
    .container {
      background: rgba(255,255,255,0.85);
      width: 70%;
      margin: 40px auto;
      padding: 25px;
      border-radius: 14px;
      color: #000;
    }
    .cards {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 18px;
      margin-top: 20px;
    }
    .card {
      background: white;
      width: 260px;
      padding: 14px;
      border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }
    .enter {
      background:#1e3a8a;
      color:white;
      padding:8px 12px;
      border:none;
      border-radius:8px;
      cursor:pointer;
    }
  </style>
</head>
<body>
  <header>🎓 Welcome to Virtual Campus Guide</header>
  <div class="container">
    <h2>Select a college to explore its virtual campus</h2>
    <div class="cards">
      {% for c in colleges %}
        <div class="card">
          <h3>{{ c[1] }}</h3>
          <p><b>City:</b> {{ c[2] if c[2] else '—' }}</p>
          <form action="{{ url_for('college') }}" method="get">
            <input type="hidden" name="college_name" value="{{ c[1] }}">
            <button class="enter" type="submit">Enter Campus</button>
          </form>
        </div>
      {% endfor %}
    </div>
  </div>
</body>
</html>
"""

GUIDE_PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ college_name }} — Virtual Guide</title>
  <style>
    body {
      font-family: Arial;
      text-align: center;
      margin: 0;
      color: white;
      {% if college_name == 'ADCET Ashta' %}
        background: url('{{ url_for('static', filename='bg_adcet.jpg') }}') no-repeat center center fixed;
      {% elif college_name == 'COEP Pune' %}
        background: url('{{ url_for('static', filename='bg_coep.jpg') }}') no-repeat center center fixed;
      {% elif college_name == 'VJTI Mumbai' %}
        background: url('{{ url_for('static', filename='bg_vjti.jpg') }}') no-repeat center center fixed;
      {% elif college_name == 'Walchand Sangli' %}
        background: url('{{ url_for('static', filename='bg_walchand.jpg') }}') no-repeat center center fixed;
      {% else %}
        background: #eef3f8;
      {% endif %}
      background-size: cover;
    }
    .header {
      background: rgba(30,58,138,0.85);
      padding: 14px;
      font-size: 22px;
      color: #fff;
    }
    .controls {
      background: rgba(255,255,255,0.9);
      padding: 12px;
      margin: 20px auto;
      width: 80%;
      border-radius: 12px;
      color: #000;
    }
    select, button {
      padding:8px; margin:6px; border-radius:8px;
      border:none; font-size:16px;
    }
    button { background:#1e3a8a; color:white; cursor:pointer; }
    .route {
      margin-top:8px; font-weight:600; color:#000;
    }
    iframe {
      width:90%; height:640px; border:none;
      margin:14px auto; display:block;
      border-radius:10px;
      box-shadow:0 4px 16px rgba(0,0,0,0.3);
    }
  </style>
</head>
<body>
  <div class="header">🏫 {{ college_name }} — Virtual Campus ({{ total_locations }} locations)</div>
  <div class="controls">
    <form method="get" action="{{ url_for('route_map') }}">
      <input type="hidden" name="college_name" value="{{ college_name }}">
      <label><b>From:</b></label>
      <select name="start">
        {% for k,v in locations.items() %}
          <option value="{{ k }}" {% if k==start %}selected{% endif %}>{{ v.name }}</option>
        {% endfor %}
      </select>
      <label><b>To:</b></label>
      <select name="end">
        {% for k,v in locations.items() %}
          <option value="{{ k }}" {% if k==end %}selected{% endif %}>{{ v.name }}</option>
        {% endfor %}
      </select>
      <button type="submit">Show Route</button>
    </form>
    {% if route_text %}
      <div class="route">Selected Route: {{ route_text }}</div>
    {% endif %}
  </div>

  {% if start and end %}
    <iframe src="{{ url_for('map_view') }}?college_name={{ college_name }}&start={{ start }}&end={{ end }}"></iframe>
  {% else %}
    <iframe src="{{ url_for('map_view') }}?college_name={{ college_name }}"></iframe>
  {% endif %}
</body>
</html>
"""

# ---------- Routes ----------
@app.route("/")
def welcome():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, city FROM colleges")
    colleges = cur.fetchall()
    conn.close()
    return render_template_string(WELCOME_PAGE, colleges=colleges)

@app.route("/college")
def college():
    college_name = request.args.get("college_name")
    locs = get_locations_for(college_name)
    if not locs:
        return "<h2>🚧 College guide unavailable.</h2>"
    return redirect(url_for("guide", college_name=college_name))

@app.route("/guide")
def guide():
    college_name = request.args.get("college_name")
    locs = get_locations_for(college_name)
    if not locs:
        return "<h2>🚧 College guide unavailable.</h2>"
    total = len(locs)
    return render_template_string(GUIDE_PAGE, college_name=college_name, locations=locs,
                                  start=None, end=None, route_text=None, total_locations=total)

@app.route("/route_map")
def route_map():
    college_name = request.args.get("college_name")
    start = request.args.get("start")
    end = request.args.get("end")
    locs = get_locations_for(college_name)
    if not locs:
        return "<h2>🚧 College guide unavailable.</h2>"

    try:
        G = build_graph_for_college(college_name)
        path = nx.shortest_path(G, start, end, weight='weight')
        route_text = " ➜ ".join([locs[p]["name"] for p in path])
    except Exception:
        route_text = "No route available between selected locations."

    total = len(locs)
    return render_template_string(GUIDE_PAGE, college_name=college_name, locations=locs,
                                  start=start, end=end, route_text=route_text, total_locations=total)

@app.route("/map_view")
def map_view():
    college_name = request.args.get("college_name")
    start = request.args.get("start")
    end = request.args.get("end")
    locs = get_locations_for(college_name)
    if not locs:
        return "<h2>🚧 College guide unavailable.</h2>"
    html = generate_map(college_name, start=start, end=end, zoom_start=17)
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(debug=True)
