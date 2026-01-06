'''
Constantly running and updating pydeck map with local mapstyle2.json

Use while modifying json to see updates in real time
'''

import pydeck as pdk
import json
import time
import os
from pathlib import Path

# Path to your map style JSON
STYLE_FILE = "mapstyle2.json"
# Temporary HTML file to display the map
OUTPUT_HTML = "map_preview.html"
# Time interval to check for changes (seconds)
CHECK_INTERVAL = 2

def load_style():
    """Load the JSON map style."""
    with open(STYLE_FILE, "r") as f:
        return json.load(f)

def build_deck(style_json):
    """Create a PyDeck Deck object from the style JSON."""
    raster_layer = pdk.Layer(
        "BitmapLayer",
        data=None,
        image="https://tiles.stadiamaps.com/tiles/stamen_terrain_background/{z}/{x}/{y}.png",
        bounds=[-180, -90, 180, 90],
        opacity=1
    )

    deck = pdk.Deck(
        map_provider="mapbox",  # required when passing a dict
        map_style=style_json,
        initial_view_state=pdk.ViewState(
            latitude=49.25,
            longitude=-123.1,
            zoom=4,
        ),
        layers=raster_layer
    )
    return deck

def open_browser(html_file):
    """Open the HTML file in the default browser (Windows, Mac, Linux)."""
    if os.name == "nt":  # Windows
        os.system(f"start {html_file}")
    elif os.name == "posix":
        if os.uname().sysname == "Darwin":  # Mac
            os.system(f"open {html_file}")
        else:  # Linux
            os.system(f"xdg-open {html_file}")

def watch_file():
    """Watch the JSON file and refresh map when it changes."""
    last_mtime = 0
    print(f"Watching {STYLE_FILE} for changes... (Press Ctrl+C to exit)")
    while True:
        try:
            mtime = Path(STYLE_FILE).stat().st_mtime
            if mtime != last_mtime:
                last_mtime = mtime
                print(f"[{time.strftime('%H:%M:%S')}] Detected change, updating map...")
                style_json = load_style()
                deck = build_deck(style_json)
                deck.to_html(OUTPUT_HTML, notebook_display=False)
                open_browser(OUTPUT_HTML)
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopped watching.")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    watch_file()