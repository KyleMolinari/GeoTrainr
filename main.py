'''
GeoTrainr

Find city name on google maps quickly

TO DO:
-option to have city names appear in native language/writing system
-improve/add map styles
'''

import pydeck as pdk
import pandas as pd
import streamlit as st
from streamlit_shortcuts import add_keyboard_shortcuts
from streamlit_js_eval import streamlit_js_eval
import unicodedata
import time

def main():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 0rem; /* Adjust this value (e.g., 0rem for no space) */
            padding-bottom: 0rem;
        }
        </style>
        """,
                unsafe_allow_html=True
                )
    st.markdown(
        """
        <style>
        /* Hide Streamlit UI */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        section[data-testid="stSidebar"] {display: none;}

        /* Remove padding/margins */
        .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
        }

        /* Force pydeck to fill screen */
        div[data-testid="stPydeckChart"] {
            position: fixed !important;
            top: 0;
            left: 0;
            width: 100vw !important;
            height: 100vh !important;
            z-index: 9998;
            background: white;
        }

        /* Prevent scrolling */
        body {
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.set_page_config(page_title="GeoTrainr",
                       layout="wide",
                       initial_sidebar_state="auto",
                       menu_items={ "Get help": None,
                                    "Report a Bug": None,
                                    "About": None}
                       )

    if 'loc' not in st.session_state:
        st.session_state.loc = None
    if 'prevloc' not in st.session_state:
        st.session_state.prevloc = None
    if 'numcities' not in st.session_state:
        st.session_state.numcities = None
    if 'numcountries' not in st.session_state:
        st.session_state.numcountries = None
    if 'radius' not in st.session_state:
        st.session_state.radius = 50000
    if 'prevcity' not in st.session_state:
        st.session_state.prevcity = pd.DataFrame([["N/A", "N/A", "N/A", "N/A", "0"]],
                                                 columns=["city", "lat", "lng", "country", "population"])
    if 'mapstyle' not in st.session_state:
        st.session_state.mapstyle = "https://kylemolinari.github.io/CustomMapStyle/custom.json"
    if 'lastguesscolour' not in st.session_state:
        if 'guesscolor' not in st.session_state:
            st.session_state.lastguesscolour = RED()
        else:
            st.session_state.lastguesscolour = st.session_state.guesscolour
    if 'guesscolour' not in st.session_state:
        st.session_state.guesscolour = RED()
    if 'lat' not in st.session_state:
        st.session_state.lat = 52.52
    if 'long' not in st.session_state:
        st.session_state.long = 13.40
    if 'zoom' not in st.session_state:
        st.session_state.zoom = 2.3
    if 'region' not in st.session_state:
        st.session_state.region = "Europe (no UK, IE, RU, UA, TR)"
    if 'minpop' not in st.session_state:
        st.session_state.minpop = None
    if 'maxpop' not in st.session_state:
        st.session_state.maxpop = None
    if "fullscreen" not in st.session_state:
        st.session_state.fullscreen = False
    if "pagewidth" not in st.session_state:
        st.session_state.pagewidth = streamlit_js_eval(js_expressions='window.innerWidth')
    if "pageheight" not in st.session_state:
        st.session_state.pageheight = streamlit_js_eval(js_expressions='window.parent.innerHeight')


    if not st.session_state.fullscreen:
        st.subheader("GeoTrainr - Find the City on the Map")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    poprange = []
    for i in range(761):
        poprange.append(50000*i)


    # Have to do these in a weird order for references to work
    if not st.session_state.fullscreen:
        with col2:
            st.session_state.minpop, st.session_state.maxpop = st.select_slider("City Population Range", options=poprange, value=(100000, 38000000))
        with col3:
            st.session_state.region = st.selectbox("Country/Group",
                                     ["All", "Europe", "Europe (no UK, IE, RU, UA, TR)",
                                      "EU Romance Language Countries", "North America", "South America", "Middle East",
                                      "Africa", "Asia", "Southeast Asia", "Cyrillic", "Balkans", "Baltics",
                                      "Scandinavia", "Canada", "United States", "Mexico",
                                      "Guatemala", "Panama", "Colombia", "Ecuador", "Peru", "Brazil",
                                      "Bolivia", "Argentina", "Uruguay", "Chile", "Denmark", "Iceland",
                                      "Ireland", "United Kingdom", "Portugal", "Spain", "France", "Andorra",
                                      "Belgium", "Netherlands", "Luxembourg", "Germany", "Norway", "Sweden",
                                      "Finland", "Estonia", "Latvia", "Lithuania", "Poland", "Ukraine",
                                      "Russia", "Czechia", "Slovakia", "Hungary", "Switzerland", "Austria",
                                      "Italy", "San Marino", "Malta", "Slovenia", "Croatia", "Romania",
                                      "Serbia", "Montenegro", "Albania", "North Macedonia", "Greece",
                                      "Turkey", "Bulgaria", "Tunisia", "Senegal", "Ghana", "Nigeria",
                                      "Uganda", "Rwanda", "Kenya", "Botswana", "South Africa", "Lesotho",
                                      "Eswatini", "Madagascar", "Israel", "Jordan", "Lebanon", "Qatar",
                                      "United Arab Emirates", "India", "Sri Lanka", "Bangladesh", "Bhutan",
                                      "Thailand", "Cambodia", "Laos", "Malaysia", "Singapore", "Indonesia",
                                      "Philippines", "Taiwan", "Korea, South", "Japan", "Australia",
                                      "New Zealand", "Kyrgyzstan", "Kazakhstan", "Mongolia",
                                      "Dominican Republic", "Oman", "Paraguay", "Costa Rica", "Cyprus",
                                      "Vietnam", "Nepal", "Bosnia and Herzegovina", "Liechtenstein", "Monaco"],
                                                   index=2)
        with col4:
            st.session_state.mapstyle = st.selectbox("Map Style",getmapstyles().keys(), format_func=mapstylenameconverter)
        with col6:
            st.button("Randomize City (or press 1)",
                  on_click=newcity(countries=st.session_state.region, min=st.session_state.minpop, max=st.session_state.maxpop))
            st.button("⛶ Fullscreen (or press 2)", on_click=togglefullscreen)
            add_keyboard_shortcuts({'1': 'Randomize City (or press 1)', })
            add_keyboard_shortcuts({'2': "⛶ Fullscreen (or press 2)", })
        with col5:
            st.write("\n")
            st.write("\n")
            st.write(str(st.session_state.numcities) + " Cities from " + str(st.session_state.numcountries) +
                 " countries fit the criteria")
        with col1:
            st.subheader("\t"+st.session_state.city.city.iloc[0])


    if st.session_state.fullscreen:
        newcity(countries=st.session_state.region, min=st.session_state.minpop, max=st.session_state.maxpop)

        st.markdown(
            """
            <style>
            /* Hide header, footer, sidebar */
            header, footer { visibility: hidden !important; }
            section[data-testid="stSidebar"] { display: none !important; }
            div[data-testid="stForm"], div[data-testid="stExpander"], div[data-testid="stLayoutWrapper"], div[data-testid="stHeader"], div[data-testid="stToolbar"] { display: none !important; }

            /* Hide all buttons */
            button, div.stButton > button { display: none !important; }

            /* Hide sliders, select_sliders, selectboxes, radio, checkboxes */
            div[data-baseweb="select"],
            div[data-baseweb="slider"],
            div[data-baseweb="select-slider"],
            div[data-baseweb="radio"],
            div[data-baseweb="checkbox"] { display: none !important; }

            /* Hide widget labels */
            label[data-testid="stWidgetLabel"] { display: none !important; }

            /* Hide headers/subheaders */
            .block-container h1, .block-container h2, .block-container h3 { display: none !important; }

            /* Hide st.write outputs except overlay */
            .stText:not(.map-overlay *) { display: none !important; }

            /* Fullscreen pydeck map */
            div[data-testid="stPydeckChart"] {
                position: fixed !important;
                inset: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 9998 !important;
                background: white !important;
                pointer-events: all !important;
            }

            /* Overlay */
            .map-overlay {
                position: fixed;
                top: 12px;
                left: 12px;
                z-index: 9999;
                background: rgba(255,255,255,0.9);
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: 600;
                pointer-events: none;
            }

            body { overflow: hidden; }
            </style>
            """,
            unsafe_allow_html=True
        )


    layer1 = pdk.Layer( 'ScatterplotLayer',
                        data=st.session_state.loc,
                        get_position='-',
                        auto_highlight=True,
                        get_radius=1000,
                        get_fill_color=[180, 0, 200, 20],
                        pickable=True )
    layer2 = pdk.Layer( 'ScatterplotLayer',
                        data=st.session_state.prevloc,
                        get_position='-',
                        auto_highlight=True,
                        get_radius=st.session_state.radius,
                        get_fill_color=st.session_state.lastguesscolour,
                        pickable=False)
    layer3 = pdk.Layer( 'ScatterplotLayer',
                        data=st.session_state.prevloc,
                        get_position='-',
                        auto_highlight=True,
                        get_radius=st.session_state.radius * 2 / 3,
                        get_fill_color=st.session_state.lastguesscolour,
                        pickable=False)
    layer4 = pdk.Layer('ScatterplotLayer',
                       data=st.session_state.prevloc,
                       get_position='-',
                       auto_highlight=True,
                       get_radius=st.session_state.radius * 1 / 3,
                       get_fill_color=st.session_state.lastguesscolour,
                       pickable=False)

    if st.session_state.fullscreen and st.session_state.prevcity.city.iloc[0] != 'N/A':

        offset_m = st.session_state.radius + 5000
        offset_deg = offset_m / 111320

        city_data = [
            {
                "position": [row["lng"], row["lat"] + offset_deg],
                "text": f"{remove_accents(row['city'])}, {remove_accents(row['country'])}"
            }
            for _, row in st.session_state.prevcity.iterrows()
        ]

        label_layer = pdk.Layer(
            "TextLayer",
            data=city_data,
            get_position="position",
            get_text="text",
            get_size=12,
            get_color=st.session_state.lastguesscolour[:3] + [255], # same colour but opaque
            pickable=False
        )



    else:
        label_layer = pdk.Layer(
            "TextLayer",
            data=[],
            get_position="position",
            get_text="text",
            get_size=12,
            get_color=st.session_state.lastguesscolour,
            pickable=False
        )


    deck = pdk.Deck(
                    # map_provider="mapbox",
                    # map_style='mapbox://styles/mapbox/streets-v12', # This one used to be good but doesnt work anymore??
                    map_style=st.session_state.mapstyle,
                    initial_view_state=pdk.ViewState(
                        latitude=st.session_state.lat,
                        longitude=st.session_state.long,
                        zoom=st.session_state.zoom,
                        pitch=0),
                    layers=[layer1, layer2, layer3, layer4, label_layer]
                    )

    # deck.to_html("map.html")

    if st.session_state.fullscreen:
        # Output map HTML inside a container div
        st.markdown(
            """
            <div id="fullscreen-map-container">
            </div>
            <style>
            /* Make the pydeck chart fill the entire viewport */
            #fullscreen-map-container > div[data-testid="stPydeckChart"] {
                position: fixed !important;
                inset: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                z-index: 9998 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.pydeck_chart(deck, height=st.session_state.pageheight, use_container_width=True, on_select=handle_selection)

        st.markdown(
            f'<div class="map-overlay">🌍 Find: <strong>{st.session_state.city.city.iloc[0]}</strong></div>',
            unsafe_allow_html=True
        )
    else:
        # safe fallback values
        st.session_state.pagewidth = 1200
        st.session_state.pageheight = 500

        st.pydeck_chart(deck, height=st.session_state.pageheight, width=st.session_state.pagewidth,
                        use_container_width=not st.session_state.fullscreen, on_select=handle_selection)

    # if fullscreen need map to display before these buttons but still need them below map for functionality
    # (even though they will be invisible)
    if st.session_state.fullscreen:
        st.button("Randomize City (or press 1)")
        st.button("⛶ Fullscreen (or press 2)", on_click=togglefullscreen)
        add_keyboard_shortcuts({'1': 'Randomize City (or press 1)', })
        add_keyboard_shortcuts({'2': "⛶ Fullscreen (or press 2)", })


    lastcitystring = "Previous city: " + st.session_state.prevcity["city"].iloc[0] + ", " + st.session_state.prevcity["country"].iloc[0] + ". Population: " + f'{int(st.session_state.prevcity["population"].iloc[0]):,}'
    if st.session_state.lastguesscolour == GREEN():
        st.subheader(f":green[{lastcitystring}]")
    else:
        st.subheader(f":red[{lastcitystring}]")

    st.session_state.prevloc = st.session_state.loc
    st.session_state.prevcity = st.session_state.city

    st.session_state.pagewidth = streamlit_js_eval(js_expressions='window.innerWidth', key='PAGE_WIDTH')
    st.session_state.pageheight = streamlit_js_eval(js_expressions='window.parent.innerHeight', key='PAGE_HEIGHT')

    #sometimes st session state glitches which results in the wrong lastguesscolour and adding this delay helps
    time.sleep(1)

def togglefullscreen():
    st.session_state.fullscreen = not st.session_state.fullscreen
    del st.session_state['prevcity']
    del st.session_state['prevloc']


def handle_selection():
    st.session_state.guesscolour = GREEN()


def remove_accents(text):
    # Replace Vietnamese Đ/đ
    text = text.replace('Đ', 'D').replace('đ', 'd')

    # Normalize to NFD, remove diacritics
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def newcity(countries="Europe (no UK, IE, RU, UA, TR)", min=100000, max=38000000):
    cities = load_cities(countries, min, max)

    st.session_state.numcities = cities.shape[0]
    st.session_state.numcountries = cities["country"].nunique()

    city = cities.sample(n=1)

    st.session_state.city = city
    st.session_state.loc = [[city.lng.iloc[0], city.lat.iloc[0]]]

    st.session_state.lastguesscolour = st.session_state.guesscolour
    st.session_state.guesscolour = RED()

@st.cache_data
def getmapstyles():
    url2name = {
                "https://kylemolinari.github.io/CustomMapStyle/custom.json": "custom",
                "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json": "voyager",
                "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json": "positron",
                "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json": "dark matter",
                # "https://tiles.stadiamaps.com/styles/stamen_terrain.json": "terrain", # this one works when run locally but not when deployed on streamlit community cloud :/ - might need API token which i dont want to use on here
                }

    return url2name

@st.cache_data
def load_cities(countries="Europe (no UK, IE, RU, UA, TR)", minpop=1000000, maxpop=100000000):
    geoguessrcountries = ["Canada", "United States", "Mexico", "Guatemala", "Panama", "Colombia",
                          "Ecuador", "Peru", "Brazil", "Bolivia", "Argentina", "Uruguay", "Chile",
                          "Denmark", "Iceland", "Ireland", "United Kingdom", "Portugal", "Spain",
                          "France", "Andorra", "Belgium", "Netherlands", "Luxembourg", "Germany",
                          "Norway", "Sweden", "Finland", "Estonia", "Latvia", "Lithuania", "Poland",
                          "Ukraine", "Russia", "Czechia", "Slovakia", "Hungary", "Switzerland", "Austria",
                          "Italy", "San Marino", "Malta", "Slovenia", "Croatia", "Romania", "Serbia",
                          "Montenegro", "Albania", "North Macedonia", "Greece", "Turkey", "Bulgaria",
                          "Tunisia", "Senegal", "Ghana", "Nigeria", "Uganda", "Rwanda", "Kenya", "Botswana",
                          "South Africa", "Lesotho", "Eswatini", "Madagascar", "Israel", "Jordan", "Lebanon",
                          "Qatar", "United Arab Emirates", "India", "Sri Lanka", "Bangladesh", "Bhutan",
                          "Thailand", "Cambodia", "Laos", "Malaysia", "Singapore", "Indonesia", "Philippines",
                          "Taiwan", "Korea, South", "Japan", "Australia", "New Zealand", "Kyrgyzstan",
                          "Kazakhstan", "Mongolia", "Dominican Republic", "Oman", "Paraguay", "Costa Rica", "Cyprus",
                          "Vietnam", "Nepal", "Bosnia and Herzegovina", "Liechtenstein", "Monaco"]
    EUcountries = ["Denmark", "Iceland", "Ireland", "United Kingdom", "Portugal", "Spain", "France", "Andorra",
                   "Belgium", "Netherlands", "Luxembourg", "Germany", "Norway", "Sweden", "Finland", "Estonia",
                   "Latvia", "Lithuania", "Poland", "Ukraine", "Russia", "Czechia", "Slovakia", "Hungary",
                   "Switzerland", "Austria","Italy", "San Marino", "Malta", "Slovenia", "Croatia", "Romania",
                   "Serbia", "Montenegro","Albania", "North Macedonia", "Greece", "Turkey", "Bulgaria", "Cyprus",
                   "Bosnia and Herzegovina", "Liechtenstein", "Monaco"]
    EUselectivecountries = ["Denmark", "Iceland", "Portugal", "Spain", "France",
                            "Andorra", "Belgium", "Netherlands", "Luxembourg", "Germany", "Norway", "Sweden",
                            "Finland", "Estonia", "Latvia", "Lithuania", "Poland", "Czechia", "Slovakia",
                            "Hungary", "Switzerland", "Austria","Italy", "San Marino", "Malta", "Slovenia",
                            "Croatia", "Romania", "Serbia", "Montenegro","Albania", "North Macedonia", "Greece",
                            "Bulgaria", "Cyprus", "Bosnia and Herzegovina", "Liechtenstein", "Monaco"]
    EUromancecountries = ["France", "Italy", "Spain", "Portugal", "Monaco", "San Marino", "Andorra", "Switzerland",
                          "Belgium", "Luxembourg"]
    NAcountries = ["Canada", "United States", "Mexico", "Guatemala", "Panama", "Costa Rica"]
    SAcountries = ["Colombia", "Ecuador", "Peru", "Brazil", "Bolivia", "Argentina", "Uruguay", "Chile", "Paraguay"]
    Africacountries = ["Tunisia", "Senegal", "Ghana", "Nigeria", "Uganda", "Rwanda", "Kenya", "Botswana",
                       "South Africa", "Lesotho", "Eswatini", "Madagascar"]
    Asiacountries = ["India", "Sri Lanka", "Bangladesh", "Bhutan", "Nepal", "Thailand", "Cambodia", "Laos", "Vietnam",
                     "Malaysia", "Singapore", "Indonesia", "Philippines", "Taiwan", "Japan", "Korea, South", "Mongolia",
                     "Kazakhstan", "Kyrgyzstan"]
    SouthEastAsiacountries = ["Thailand", "Cambodia", "Laos", "Vietnam", "Malaysia", "Singapore",
                              "Indonesia", "Philippines"]
    Balkancountries = ["Albania", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Greece", "Montenegro",
                       "North Macedonia", "Serbia"]
    Balticcountries = ["Estonia", "Latvia", "Lithuania"]
    Scandinaviacountries = ["Norway", "Sweden", "Finland", "Denmark", "Iceland"]
    MEcountries = ["Israel", "Jordan", "Lebanon", "Qatar", "United Arab Emirates", "Oman"]
    Cyrilliccountries = ["Ukraine", "Russia", "Montenegro", "Serbia", "North Macedonia", "Bulgaria", "Kyrgyzstan",
                         "Kazakhstan", "Mongolia"]
    setmapview = False
    if countries == "All":
        countries = geoguessrcountries
        st.session_state.lat = 0
        st.session_state.long = 0
        st.session_state.zoom = 0
        st.session_state.radius = 200000
    elif countries == "Europe":
        countries = EUcountries
        st.session_state.lat = 49.22
        st.session_state.long = 18.74
        st.session_state.zoom = 2
        st.session_state.radius = 50000
    elif countries == "Europe (no UK, IE, RU, UA, TR)":
        countries = EUselectivecountries
        st.session_state.lat = 52.52
        st.session_state.long = 13.40
        st.session_state.zoom = 2.3
        st.session_state.radius = 50000
    elif countries == "EU Romance Language Countries":
        countries = EUromancecountries
        st.session_state.lat = 45.76
        st.session_state.long = 4.84
        st.session_state.zoom = 4
        st.session_state.radius = 15000
    elif countries == "North America":
        countries = NAcountries
        st.session_state.lat = 46.80
        st.session_state.long = -100.79
        st.session_state.zoom = 2.1
        st.session_state.radius = 50000
    elif countries == "South America":
        countries = SAcountries
        st.session_state.lat = -24.63
        st.session_state.long = -58.18
        st.session_state.zoom = 2
        st.session_state.radius = 50000
    elif countries == "Africa":
        countries = Africacountries
        st.session_state.lat = 2.50
        st.session_state.long = 17.45
        st.session_state.zoom = 2
        st.session_state.radius = 50000
    elif countries == "Middle East":
        countries = MEcountries
        st.session_state.lat = 24.71
        st.session_state.long = 46.68
        st.session_state.zoom = 3
        st.session_state.radius = 20000
    elif countries == 'Asia':
        countries = Asiacountries
        st.session_state.lat = 29.65
        st.session_state.long = 91.14
        st.session_state.zoom = 2.5
        st.session_state.radius = 50000
    elif countries == 'Southeast Asia':
        countries = SouthEastAsiacountries
        st.session_state.lat = 4.42
        st.session_state.long = 114.02
        st.session_state.zoom = 3.5
        st.session_state.radius = 30000
    elif countries == "Balkans":
        countries = Balkancountries
        st.session_state.lat = 42.67
        st.session_state.long = 21.16
        st.session_state.zoom = 4.5
        st.session_state.radius = 20000
    elif countries == "Baltics":
        countries = Balticcountries
        st.session_state.lat = 56.97
        st.session_state.long = 24.11
        st.session_state.zoom = 5.4
        st.session_state.radius = 8000
    elif countries == "Scandinavia":
        countries = Scandinaviacountries
        st.session_state.lat = 64.39
        st.session_state.long = 17.31
        st.session_state.zoom = 3.5
        st.session_state.radius = 15000
    elif countries == "Cyrillic":
        countries = Cyrilliccountries
        st.session_state.lat = 55.00
        st.session_state.long = 73.36
        st.session_state.zoom = 2
        st.session_state.radius = 50000
    else:
        countries = [countries]
        setmapview = True

    df = pd.read_excel("worldcities.xlsx",index_col=False)
    df = df.drop(["city_ascii", "iso2", "iso3", "admin_name", "capital", "id"], axis=1)
    df = df.dropna()
    df = df.drop(df[df.population < minpop].index)
    df = df.drop(df[df.population > maxpop].index)
    df = df[df.country.isin(countries)]

    if setmapview:
        latmax = df['lat'].max()
        latmin = df['lat'].min()
        longmax = df['lng'].max()
        longmin = df['lng'].min()
        st.session_state.lat = latmin + (latmax-latmin)/2
        st.session_state.long = longmin + (longmax-longmin)/2

        #need to figure out a formula to map country size to zoom level
        st.session_state.zoom = 70.0 / (max([latmax - latmin, longmax - longmin]) + 11) + 1.7

        st.session_state.radius = 200000 * 2 * max([latmax - latmin, longmax - longmin]) / 180

    return df

@st.cache_data
def mapstylenameconverter(url):
    return getmapstyles().get(url, "Unknown")

@st.cache_data
def RED():
    return [180, 30, 30, 100]

@st.cache_data
def GREEN():
    return [30, 180, 30, 100]

if __name__ == '__main__':
    main()
