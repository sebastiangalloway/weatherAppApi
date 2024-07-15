import streamlit as st
import requests
from streamlit_folium import folium_static
import folium

# visit this site to get your own api key: https://www.iqair.com/us/commercial-air-quality-monitors/api
api_key= "Insert your api"

st.title("Weather and Air Quality Web App")
st.header("Streamlit and AirVisual API")

@st.cache_data
def map_creator(latitude,longitude):

    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # add marker for the station
    folium.Marker([latitude, longitude], popup="Station", tooltip="Station").add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)

@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    # st.write(countries_dict)
    return countries_dict

@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    # st.write(states_dict)
    return states_dict

@st.cache_data
def generate_list_of_cities(state_selected,country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    # st.write(cities_dict)
    return cities_dict
        
def display_data(aqi_data_dict):
    if aqi_data_dict["status"] == "success":
        data = aqi_data_dict["data"]
        st.subheader(f"Weather and Air Quality in {data['city']}, {data['state']}, {data['country']}")
        with st.container(border=True):
            st.write(f"The temperature is {data['current']['weather']['tp']}°C")
            st.write(f"The humidity is {data['current']['weather']['hu']}%")
            st.write(f"The air quality index (AQI) is currently {data['current']['pollution']['aqius']}")
            st.write(f"Latitude: {data["location"]["coordinates"][1]}° Longitude: {data["location"]["coordinates"][0]}°")
        map_creator(data["location"]["coordinates"][1], data["location"]["coordinates"][0])
    else:
        st.warning("No data available for this location.")

#st.selectbox(label, options, index=0, format_func=special_internal_function, key=None, help=None, on_change=None, args=None, kwargs=None, *, placeholder="Choose an option", disabled=False, label_visibility="visible")
category = st.selectbox("Choose a category", ("By City, State, and Country","By Nearest City (IP Address)","By Latitude and Longitude"), index = None)

if category == "By City, State, and Country":
    countries_dict=generate_list_of_countries()
    if countries_dict["status"] == "success":
        countries_list=[]
        for i in countries_dict["data"]:
            countries_list.append(i["country"])
        countries_list.insert(0,"")

        country_selected = st.selectbox("Select a country", options=countries_list)
        if country_selected:

            state_dict=generate_list_of_states(country_selected)
            if state_dict["status"] == "success":
                state_list=[]
                for i in state_dict["data"]:
                    state_list.append(i["state"])
                state_list.insert(0,"")

                state_selected = st.selectbox("Select a state", options= state_list)
                if state_selected:

                    city_dict=generate_list_of_cities(state_selected,country_selected)

                    if city_dict["status"] == "success":
                        city_list=[]
                        for i in city_dict["data"]:
                            city_list.append(i["city"])
                        city_list.insert(0,"")

                        city_selected = st.selectbox("Select a city", options= city_list)

                        if city_selected:
                            aqi_data_url = f"https://api.airvisual.com/v2/city?city={city_selected}&state={state_selected}&country={country_selected}&key={api_key}"
                            aqi_data_dict = requests.get(aqi_data_url).json()
                            if aqi_data_dict["status"] == "success":
                                # TODO: Display the weather and air quality data as shown in the video and description of the assignment
                                display_data(aqi_data_dict)
                            else:
                                st.warning("No data available for this location.")

                    else:
                        st.warning("No stations available, please select another state.")
            else:
                st.warning("No stations available, please select another country.")
    else:
        st.error("Too many requests. Wait for a few minutes before your next API call.")

elif category == "By Nearest City (IP Address)":
    url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
    aqi_data_dict = requests.get(url).json()

    if aqi_data_dict["status"] == "success":
    # TODO: Display the weather and air quality data as shown in the video and description of the assignment
        display_data(aqi_data_dict)
    else:
        st.warning("No data available for this location.")

elif category == "By Latitude and Longitude":
    # TODO: Add two text input boxes for the user to enter the latitude and longitude information
    latitude = st.text_input("Latitude", value="", max_chars=None, key=None, type="default", help="For latitude, positive would represent North and negative would represent South.", 
                            autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    longitude = st.text_input("Longitude", value="", max_chars=None, key=None, type="default", help="For longitude, positive would represent East and negative would represent West.",
                            autocomplete=None, on_change=None, args=None, kwargs=None, placeholder=None, disabled=False, label_visibility="visible")
    
    if latitude and longitude:
        url = f"https://api.airvisual.com/v2/nearest_city?lat={latitude}&lon={longitude}&key={api_key}"
        aqi_data_dict = requests.get(url).json()

        if aqi_data_dict["status"] == "success":
        # TODO: Display the weather and air quality data as shown in the video and description of the assignment
            display_data(aqi_data_dict)
        else:
            st.warning("No data available for this location.")