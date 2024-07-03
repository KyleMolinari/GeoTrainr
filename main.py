'''
Training for Geoguessr

Find city name on google maps quickly
'''
import pydeck as pdk
import pandas as pd
import streamlit as st
from streamlit_shortcuts import add_keyboard_shortcuts
import time


def main():
    st.set_page_config(page_title="GeoTraining", layout="wide", initial_sidebar_state="auto",
                       menu_items={
                           "Get help": None,
                           "Report a Bug": None,
                           "About": None}
                       )

    st.title("GeoTraining")
    st.subheader("Find the City on the Map")

    if 'loc' not in st.session_state:
        st.session_state.loc = None
    if 'prevloc' not in st.session_state:
        st.session_state.prevloc = None
    if 'prevcity' not in st.session_state:
        st.session_state.prevcity = None
    if 'numcities' not in st.session_state:
        st.session_state.numcities = None
    if 'numcountries' not in st.session_state:
        st.session_state.numcountries = None
    if 'radius' not in st.session_state:
        st.session_state.radius = 200000

    col1, col2, col3, col4 = st.columns(4)
    poprange = []
    for i in range(501):
        poprange.append(100000*i)
    with col2:
        minpop, maxpop = st.select_slider("City Population Range", options=poprange, value=(500000, 50000000))
    with col3:
        region = st.selectbox("Country/Group", ["All", "EU", "NA", "SA", "ME", "Africa", "Cyrillic",
                          "Canada", "United States", "Mexico", "Guatemala", "Panama", "Colombia", "Ecuador", "Peru",
                          "Brazil", "Bolivia", "Argentina", "Uruguay", "Chile", "Denmark", "Iceland", "Ireland",
                          "United Kingdom", "Portugal", "Spain", "France", "Andorra", "Belgium", "Netherlands",
                          "Luxembourg", "Germany", "Norway", "Sweden", "Finland", "Estonia", "Latvia", "Lithuania",
                          "Poland", "Ukraine", "Russia", "Czechia", "Slovakia", "Hungary", "Switzerland", "Austria",
                          "Italy", "San Marino", "Malta", "Slovenia", "Croatia", "Romania", "Serbia", "Montenegro",
                          "Albania", "North Macedonia", "Greece", "Turkey", "Bulgaria", "Tunisia", "Senegal", "Ghana",
                          "Nigeria", "Uganda", "Rwanda", "Kenya", "Botswana", "South Africa", "Lesotho", "Eswatini",
                          "Madagascar", "Israel", "Jordan", "Lebanon", "Qatar", "United Arab Emirates", "India",
                          "Sri Lanka", "Bangladesh", "Bhutan", "Thailand", "Cambodia", "Laos", "Malaysia", "Singapore",
                          "Indonesia", "Philippines", "Taiwan", "Korea, South", "Japan", "Australia", "New Zealand",
                          "Kyrgyzstan", "Kazakhstan", "Mongolia", "Dominican Republic"])
    with col1:
        st.button("Randomize City (or press 1)", on_click=newcity(countries=region, min=minpop, max=maxpop))
    with col4:
        st.write("\n")
        st.write("\n")
        st.write("\n")
        st.write(str(st.session_state.numcities) + " Cities from " + str(st.session_state.numcountries) +
                 " countries fit the criteria")

    add_keyboard_shortcuts({
        '1': 'Randomize City (or press 1)',
    })

    layer1 = pdk.Layer(
        'ScatterplotLayer',
        data=st.session_state.loc,
        get_position='-',
        auto_highlight=True,
        get_radius=1000,
        get_fill_color=[180, 0, 200, 140],
        pickable=True
    )

    layer2 = pdk.Layer(
        'ScatterplotLayer',
        data=st.session_state.prevloc,
        get_position='-',
        auto_highlight=True,
        get_radius=st.session_state.radius,
        get_fill_color=[180, 30, 30, 140],
        pickable=True
    )

    deck = pdk.Deck(map_style='mapbox://styles/mapbox/streets-v12',
                             initial_view_state=pdk.ViewState(
                                 latitude=0,
                                 longitude=0,
                                 zoom=0,
                                 pitch=0),
                             layers=[layer1, layer2]
                             )

    st.pydeck_chart(deck, use_container_width=True)
    try:
        st.subheader("Previous city: " + st.session_state.prevcity["city"].iloc[0] + ", " + st.session_state.prevcity["country"].iloc[0] + ". Population: " + f'{int(st.session_state.prevcity["population"].iloc[0]):,}')
    except:
        "Previous city: N/A"
    st.session_state.prevloc = st.session_state.loc
    st.session_state.prevcity = st.session_state.city

    time.sleep(0.5)


def newcity(countries="All", min=1000000, max=100000000):
    cities = load_cities(countries, min, max)

    st.session_state.numcities = cities.shape[0]
    st.session_state.numcountries = cities["country"].nunique()

    city = cities.sample(n=1)
    st.subheader(city.city.iloc[0])


    st.session_state.city = city
    st.session_state.loc = [[city.lng.iloc[0], city.lat.iloc[0]]]


@st.cache
def load_cities(countries="All", min=1000000, max=100000000):
    geoguessrcountries = ["Canada", "United States", "Mexico", "Guatemala", "Panama", "Colombia", "Ecuador", "Peru",
                          "Brazil", "Bolivia", "Argentina", "Uruguay", "Chile", "Denmark", "Iceland", "Ireland",
                          "United Kingdom", "Portugal", "Spain", "France", "Andorra", "Belgium", "Netherlands",
                          "Luxembourg", "Germany", "Norway", "Sweden", "Finland", "Estonia", "Latvia", "Lithuania",
                          "Poland", "Ukraine", "Russia", "Czechia", "Slovakia", "Hungary", "Switzerland", "Austria",
                          "Italy", "San Marino", "Malta", "Slovenia", "Croatia", "Romania", "Serbia", "Montenegro",
                          "Albania", "North Macedonia", "Greece", "Turkey", "Bulgaria", "Tunisia", "Senegal", "Ghana",
                          "Nigeria", "Uganda", "Rwanda", "Kenya", "Botswana", "South Africa", "Lesotho", "Eswatini",
                          "Madagascar", "Israel", "Jordan", "Lebanon", "Qatar", "United Arab Emirates", "India",
                          "Sri Lanka", "Bangladesh", "Bhutan", "Thailand", "Cambodia", "Laos", "Malaysia", "Singapore",
                          "Indonesia", "Philippines", "Taiwan", "Korea, South", "Japan", "Australia", "New Zealand",
                          "Kyrgyzstan", "Kazakhstan", "Mongolia", "Dominican Republic"]

    EUcountries = ["Denmark", "Iceland", "Ireland", "United Kingdom", "Portugal", "Spain", "France", "Andorra",
                       "Belgium", "Netherlands", "Luxembourg", "Germany", "Norway", "Sweden", "Finland", "Estonia",
                       "Latvia", "Lithuania", "Poland", "Ukraine", "Russia", "Czechia", "Slovakia", "Hungary",
                       "Switzerland", "Austria","Italy", "San Marino", "Malta", "Slovenia", "Croatia", "Romania",
                       "Serbia", "Montenegro","Albania", "North Macedonia", "Greece", "Turkey", "Bulgaria"]

    NAcountries = ["Canada", "United States", "Mexico", "Guatemala", "Panama"]

    SAcountries = ["Colombia", "Ecuador", "Peru", "Brazil", "Bolivia", "Argentina", "Uruguay", "Chile"]

    Africacountries = ["Tunisia", "Senegal", "Ghana","Nigeria", "Uganda", "Rwanda", "Kenya", "Botswana",
                       "South Africa", "Lesotho", "Eswatini","Madagascar"]

    MEcountries = ["Israel", "Jordan", "Lebanon", "Qatar", "United Arab Emirates"]

    Cyrilliccountries = ["Ukraine", "Russia", "Montenegro", "North Macedonia", "Bulgaria", "Kyrgyzstan",
                         "Kazakhstan", "Mongolia"]

    if countries == "All":
        countries = geoguessrcountries
    elif countries == "EU":
        countries = EUcountries
    elif countries == "NA":
        countries = NAcountries
    elif countries == "SA":
        countries = SAcountries
    elif countries == "Africa":
        countries = Africacountries
    elif countries == "ME":
        countries == MEcountries
    elif countries == "Cyrillic":
        countries = Cyrilliccountries
    else:
        countries = [countries]
        st.session_state.radius = 50000

    df = pd.read_excel("worldcities.xlsx",index_col=False)
    df = df.drop(["city_ascii", "iso2", "iso3", "admin_name", "capital", "id"], axis=1)
    df = df.dropna()
    df = df.drop(df[df.population < min].index)
    df = df.drop(df[df.population > max].index)
    df = df[df.country.isin(countries)]

    return df

if __name__ == '__main__':
    main()
