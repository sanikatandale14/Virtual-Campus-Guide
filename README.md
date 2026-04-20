# 🎓 Virtual Campus Buddy (Flask + Graph Navigation)

Virtual Campus Buddy is a smart web-based campus navigation system built using Flask and NetworkX. It allows users to explore different college campuses, view locations, and find the shortest path between places using graph algorithms.

---

## 🚀 Features

### 🏫 Multi-College Support (ADCET, COEP, VJTI, Walchand, etc.)
The system allows users to select and explore multiple college campuses. Each college has its own set of locations and connections, making the platform scalable and adaptable for different institutions.

### 🗄️ SQLite Database (Auto Initialization)
The application uses an SQLite database that is automatically created and populated when the system runs for the first time. It stores college details, campus locations, and connections between locations, eliminating the need for manual database setup.

### 🧭 Smart Route Finder (Shortest Path Algorithm)
Users can select a starting point and destination within the campus. The system calculates the most efficient route using a shortest path algorithm, ensuring minimal distance or steps between locations.

### 🧠 Graph-Based Navigation using NetworkX
Campus locations are represented as nodes and paths as edges. Using the NetworkX library, the system builds a graph structure and applies algorithms to dynamically determine the best possible route.

### 🗺️ Interactive Map View
The system generates a visual map of the campus showing all locations and the selected route. This map is displayed in the browser, helping users understand navigation clearly.

### 🎨 Dynamic UI with College Backgrounds
Each college has a customized background and visual theme, enhancing user experience and giving a realistic feel of different campuses.

### 📊 Location Selection Interface
Users can easily choose their starting and ending locations using dropdown menus, making the system simple, intuitive, and user-friendly.

### ⚡ Real-Time Route Calculation
The system instantly calculates and displays the route as soon as the user selects locations, ensuring a fast and interactive experience.

---

## 💡 Project Objective

The main objective of this project is to create a virtual campus navigation system that:

- Helps students easily navigate college campuses  
- Provides shortest path between locations  
- Uses graph algorithms for efficient routing  
- Improves digital campus experience  

---

## 🧩 Tech Stack

- **Frontend:** HTML, CSS, JS (Leaflet via Folium) 
- **Backend:** Flask (Python)  
- **Database:** SQLite  
- **Graph Library:** NetworkX  
- **Map Rendering:** Custom HTML Map (via `generate_map` function)  
