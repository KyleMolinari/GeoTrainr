'''
GeoTrainr

Find city name on google maps quickly

TO DO:
-option to have city names appear in native language/writing system
-add next city name to chart fixed in top corner to allow user to play with map in full screen view
-improve/add map styles
'''

import pydeck as pdk
import pandas as pd
import streamlit as st
from streamlit_shortcuts import add_keyboard_shortcuts
import time

def main():
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem; /* Adjust this value (e.g., 0rem for no space) */
            padding-bottom: 0rem;
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
    st.subheader("GeoTrainr - Find the City on the Map")

    if 'loc' not in st.session_state:
        st.session_state.loc = None
    if 'prevloc' not in st.session_state:
        st.session_state.prevloc = None
    if 'numcities' not in st.session_state:
        st.session_state.numcities = None
    if 'numcountries' not in st.session_state:
        st.session_state.numcountries = None
    if 'radius' not in st.session_state:
        st.session_state.radius = 200000
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
        st.session_state.lat = 0
    if 'long' not in st.session_state:
        st.session_state.long = 0
    if 'zoom' not in st.session_state:
        st.session_state.zoom = 0




    col1, col2, col3, col4, col5 = st.columns(5)
    poprange = []
    for i in range(761):
        poprange.append(50000*i)

    with col2:
        minpop, maxpop = st.select_slider("City Population Range", options=poprange, value=(100000, 38000000))
    with col3: region = st.selectbox("Country/Group",
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
                                      "Vietnam", "Nepal", "Bosnia and Herzegovina", "Liechtenstein", "Monaco"])
    with col1:
        st.button("Randomize City (or press 1)",
                         on_click=newcity(countries=region, min=minpop, max=maxpop))
    with col4:
        st.session_state.mapstyle = st.selectbox("Map Style",getmapstyles().keys(), format_func=mapstylenameconverter)
    with col5:
        st.write("\n")
        st.write("\n")
        st.write(str(st.session_state.numcities) + " Cities from " + str(st.session_state.numcountries) +
                 " countries fit the criteria")

    add_keyboard_shortcuts({ '1': 'Randomize City (or press 1)', })

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


    deck = pdk.Deck(
                    # map_provider="mapbox",
                    # map_style='mapbox://styles/mapbox/streets-v12', # This one used to be good but doesnt work anymore??
                    map_style=st.session_state.mapstyle,
                    initial_view_state=pdk.ViewState(
                        latitude=st.session_state.lat,
                        longitude=st.session_state.long,
                        zoom=st.session_state.zoom,
                        pitch=0),
                    layers=[layer1, layer2, layer3, layer4]
                    )

    deck.to_html("map.html")

    st.pydeck_chart(deck, height=700, use_container_width=True, on_select=handle_selection)

    lastcitystring = "Previous city: " + st.session_state.prevcity["city"].iloc[0] + ", " + st.session_state.prevcity["country"].iloc[0] + ". Population: " + f'{int(st.session_state.prevcity["population"].iloc[0]):,}'
    if st.session_state.lastguesscolour == GREEN():
        st.subheader(f":green[{lastcitystring}]")
    else:
        st.subheader(f":red[{lastcitystring}]")

    st.session_state.prevloc = st.session_state.loc
    st.session_state.prevcity = st.session_state.city

    #sometimes st session state glitches which results in the wrong lastguesscolour and adding this delay helps
    time.sleep(1)

def handle_selection():
    st.session_state.guesscolour = GREEN()

def newcity(countries="All", min=100000, max=38000000):
    cities = load_cities(countries, min, max)

    st.session_state.numcities = cities.shape[0]
    st.session_state.numcountries = cities["country"].nunique()

    city = cities.sample(n=1)
    st.subheader(city.city.iloc[0])

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
def load_cities(countries="All", minpop=1000000, maxpop=100000000):
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
