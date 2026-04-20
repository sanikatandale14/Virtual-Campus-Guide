# virtual.py
import folium
from folium.plugins import AntPath
import networkx as nx
import math
import random

# deterministic randomness for reproducibility
RND_SEED = 42
random.seed(RND_SEED)

# ---------- ADCET real data (from your description) ----------
# Approximate coordinates (you can fine-tune these later)
ADCET_BASE = (17.0498, 74.4196)

ADCET_LOCATIONS = {
    "engg_gate": {"name": "Engineering Gate", "coords": (17.0498, 74.4196),
                  "type": "Entrance",
                  "details": {"notes": "Main campus entry point."}},
    "canteen": {"name": "Swad Aswad Canteen", "coords": (17.0499, 74.4192),
                "type": "Facility",
                "details": {"hours": "8:00-20:00", "notes": "Student canteen, left of gate."}},
    "public_school": {"name": "Public School", "coords": (17.0499, 74.4200),
                      "type": "Building",
                      "details": {"notes": "Right side of main gate."}},
    "admin_building": {"name": "Administrative Building", "coords": (17.0501, 74.4194),
                       "type": "Building", "details": {"floors": 2, "notes": "Admin wing"}},
    "atm": {"name": "ATM (near Admin)", "coords": (17.05008, 74.41933),
            "type": "Facility", "details": {"provider": "Bank XYZ", "floor": "Ground"}},
    "ccf_lab": {"name": "CCF Lab", "coords": (17.05009, 74.41936),
                "type": "Lab", "details": {"floor": "Ground", "equipments": ["PCs", "Special Kit"]}},
    "mech_dept": {"name": "Mechanical Department", "coords": (17.0501, 74.41945),
                  "type": "Department", "details": {"HOD": "Dr. S. R. Patil", "classrooms": 6,
                                                   "labs": ["Thermal Lab", "Machine Shop"]}},
    "electrical_dept": {"name": "Electrical Department", "coords": (17.0502, 74.4193),
                        "type": "Department", "details": {"HOD": "Dr. A. B. Kale", "classrooms": 4,
                                                         "labs": ["Power Systems Lab"]}},
    "iot_dept": {"name": "IoT Department", "coords": (17.0502, 74.4195),
                 "type": "Department", "details": {"HOD": "Dr. P. K. More", "classrooms": 3,
                                                  "labs": ["IoT Lab", "Embedded Systems"]}},
    "library": {"name": "Library", "coords": (17.0503, 74.4196),
                "type": "Facility", "details": {"books": 12000, "hours": "9:00-18:00"}},
    # Building behind admin (multi-floor)
    "cse_dept": {"name": "CSE Department", "coords": (17.0503, 74.4194),
                 "type": "Department", "details": {"floor": "Ground", "HOD": "Dr. R. T. Shah", "labs": ["DSA Lab"]}},
    "aero_dept": {"name": "Aeronautical Department", "coords": (17.0504, 74.4194),
                  "type": "Department", "details": {"floor": "1st", "HOD": "Dr. M. S. Gujar", "labs": ["Aero Lab"]}},
    "food_dept": {"name": "Food Department", "coords": (17.0505, 74.4194),
                  "type": "Department", "details": {"floor": "2nd", "HOD": "Dr. N. V. Patil", "labs": ["Food Processing"]}},
    "aids_dept": {"name": "AIDS Department", "coords": (17.0506, 74.4194),
                  "type": "Department", "details": {"floor": "3rd", "HOD": "Dr. S. Jadhav", "labs": ["AI Lab"]}},
    "coe_dept": {"name": "COE Department", "coords": (17.0507, 74.4194),
                 "type": "Department", "details": {"floor": "4th", "notes": "Center of Excellence"}},
    # Library adjacent building floors
    "civil_dept": {"name": "Civil Department", "coords": (17.0503, 74.4198),
                   "type": "Department", "details": {"floor": "Ground", "HOD": "Dr. V. N. More"}},
    "bba_bca_dept": {"name": "BBA / BCA Department", "coords": (17.0504, 74.4198),
                     "type": "Department", "details": {"floor": "1st", "notes": "BBA & BCA"}}, 
    "basic_science_dept": {"name": "Basic Science Department", "coords": (17.0505, 74.4198),
                           "type": "Department", "details": {"floor": "2nd", "labs": ["Physics Lab", "Chemistry Lab"]}},
}

ADCET_CONNECTIONS = [
    ("engg_gate", "canteen"),
    ("engg_gate", "public_school"),
    ("canteen", "admin_building"),
    ("admin_building", "atm"),
    ("atm", "ccf_lab"),
    ("ccf_lab", "mech_dept"),
    ("mech_dept", "electrical_dept"),
    ("electrical_dept", "iot_dept"),
    ("admin_building", "library"),
    ("admin_building", "cse_dept"),
    ("cse_dept", "aero_dept"),
    ("aero_dept", "food_dept"),
    ("food_dept", "aids_dept"),
    ("aids_dept", "coe_dept"),
    ("library", "civil_dept"),
    ("civil_dept", "bba_bca_dept"),
    ("bba_bca_dept", "basic_science_dept")
]

# ---------- Synthetic colleges (100 locations each) ----------
COLLEGE_BASES = {
    "COEP Pune": (18.5294, 73.8567),
    "VJTI Mumbai": (19.0222, 72.8553),
    "Walchand Sangli": (16.8450, 74.6017)
}

def synthetic_name(i):
    prefixes = ["Block", "Lab", "Dept", "Centre", "Annex", "Unit", "Hall", "Tower"]
    suffixes = ["A", "B", "North", "South", "East", "West", "Main"]
    p = prefixes[i % len(prefixes)]
    s = suffixes[i % len(suffixes)]
    return f"{p} {s} {i}"

def gen_locations_for(college_name, base_latlon, n=100):
    base_lat, base_lon = base_latlon
    locs = {}
    angle = 0.0
    radius_step = 0.00006
    for i in range(1, n + 1):
        r = radius_step * (i ** 0.5)
        angle += 0.25 + (i % 5) * 0.02
        lat = base_lat + r * math.cos(angle) + (random.random() - 0.5) * 0.00002
        lon = base_lon + r * math.sin(angle) + (random.random() - 0.5) * 0.00002
        key = f"loc_{i:03d}"
        locs[key] = {"name": synthetic_name(i), "coords": (round(lat, 7), round(lon, 7)),
                     "type": "Department", "details": {"note": "Synthetic demo location"}}
    return locs

COLLEGE_LOCATIONS = {}    # name -> dict of keys
COLLEGE_CONNECTIONS = {}  # name -> list of (a,b)

NUM_LOC_PER_SYNT = 100
for cname, base in COLLEGE_BASES.items():
    locs = gen_locations_for(cname, base, n=NUM_LOC_PER_SYNT)
    COLLEGE_LOCATIONS[cname] = locs
    keys = list(locs.keys())
    conns = []
    for a, b in zip(keys[:-1], keys[1:]):
        conns.append((a, b))
    extra = NUM_LOC_PER_SYNT // 10
    for _ in range(extra):
        a = random.choice(keys)
        b = random.choice(keys)
        if a != b:
            conns.append((a, b))
    # dedupe preserving pair orientation
    seen = set()
    uniq = []
    for p in conns:
        pair = tuple(sorted(p))
        if pair not in seen:
            seen.add(pair)
            uniq.append(p)
    COLLEGE_CONNECTIONS[cname] = uniq

# ---------- Combined access function ----------
ALL_COLLEGES = ["ADCET Ashta"] + list(COLLEGE_LOCATIONS.keys())

def get_locations_for(college_name):
    if college_name == "ADCET Ashta":
        return ADCET_LOCATIONS
    return COLLEGE_LOCATIONS.get(college_name, {})

def get_connections_for(college_name):
    if college_name == "ADCET Ashta":
        return ADCET_CONNECTIONS
    return COLLEGE_CONNECTIONS.get(college_name, [])

# ---------- Distance + graph ----------
def distance_between_coords(c1, c2):
    lat1, lon1 = c1
    lat2, lon2 = c2
    R = 6371000
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    return R * (dphi ** 2 + dlambda ** 2) ** 0.5

def build_graph_for_college(college_name):
    locs = get_locations_for(college_name)
    conns = get_connections_for(college_name)
    G = nx.Graph()
    for a, b in conns:
        if a in locs and b in locs:
            w = distance_between_coords(locs[a]["coords"], locs[b]["coords"])
            G.add_edge(a, b, weight=w)
    return G

# ---------- HTML helper for ADCET popups ----------
def adcet_popup_html(key, meta):
    name = meta.get("name", key)
    typ = meta.get("type", "")
    coords = meta.get("coords", ("", ""))
    details = meta.get("details", {})
    lines = []
    lines.append(f"<b>{name}</b><br><i>{typ}</i><br>")
    # show coordinates
    lines.append(f"Lat: {coords[0]}<br>Lon: {coords[1]}<br><hr>")
    # details: iterate known fields
    for k, v in details.items():
        if isinstance(v, list):
            lines.append(f"<b>{k}:</b> {', '.join(v)}<br>")
        else:
            lines.append(f"<b>{k}:</b> {v}<br>")
    # small link to highlight key
    lines.append(f"<hr><small>{key}</small>")
    return "".join(lines)

# ---------- Map generator ----------
def generate_map(college_name, start=None, end=None, zoom_start=18):
    if college_name == "ADCET Ashta":
        base = ADCET_BASE
    else:
        base = COLLEGE_BASES.get(college_name, (17.0500, 74.4200))

    locs = get_locations_for(college_name)
    conns = get_connections_for(college_name)

    m = folium.Map(location=[base[0], base[1]], zoom_start=zoom_start, control_scale=True)

    # draw background connections
    for a, b in conns:
        if a in locs and b in locs:
            coords = [locs[a]["coords"], locs[b]["coords"]]
            folium.PolyLine(coords, color="lightgray", weight=2, opacity=0.5).add_to(m)

    # add markers
    for key, meta in locs.items():
        coords = meta["coords"]
        if college_name == "ADCET Ashta":
            popup_html = adcet_popup_html(key, meta)
        else:
            popup_html = f"<b>{meta['name']}</b><br><i>{meta.get('type','')}</i><br>{key}"
        folium.CircleMarker(
            location=coords,
            radius=5,
            color="gray",
            fill=True,
            fill_color="lightgray",
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    # highlight route if requested
    if start and end:
        try:
            G = build_graph_for_college(college_name)
            path = nx.shortest_path(G, start, end, weight="weight")
            route_coords = [locs[node]["coords"] for node in path]
            AntPath(route_coords, color="blue", weight=6, opacity=0.9, delay=400).add_to(m)
            folium.Marker(locs[start]["coords"], popup=f"Start: {locs[start]['name']}",
                          icon=folium.Icon(color="green")).add_to(m)
            folium.Marker(locs[end]["coords"], popup=f"Destination: {locs[end]['name']}",
                          icon=folium.Icon(color="red")).add_to(m)
        except Exception:
            # ignore path calculation errors so map still renders
            pass

    return m.get_root().render()
