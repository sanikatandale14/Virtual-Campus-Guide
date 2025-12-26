# Virtual Campus Navigator (ADCET Ashta)

This small Flask app serves an interactive map using Folium and NetworkX.

Quick Windows (CMD) steps to run locally:

1. Create a virtual environment (recommended):

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies:

```cmd
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Run the app:

```cmd
python app.py
```

4. Open a browser to:

http://127.0.0.1:5000

Notes:
- If you get errors about missing packages, double-check activation of the virtual environment and rerun the `pip install` step.
- The app uses `folium` to generate map HTML and NetworkX to compute routes.
