from fastapi import APIRouter,HTTPException
import requests
from database.user import get_preferences
import json,re


route = APIRouter()

CLIMATE_API_KEY = "f98c3cac75094bae6edee547d15b5e50"
CITY_NAME_REGEX = r"^[a-zA-Z\s]+$"

#checks format of city name
def validate_city_name(city_name):
    if not re.match(CITY_NAME_REGEX, city_name):
        raise HTTPException(status_code=400, detail="Invalid city name format")

#Collects attractions based on the climate data and user preference    
def get_nearby_places(latitude, longitude, radius, preferences, weather_cat):
    overpass_url = "http://overpass-api.de/api/interpreter"
    queries = []
    results = []

    for preference in preferences:
        if preference == "Nature Lover":
            if weather_cat == "Indoors Climate":
                queries.append('node["amenity"](around:{},{},{});'.format(radius, latitude, longitude))
            elif weather_cat == "Outdoors Climate":
                queries.append('node["leisure"](around:{},{},{});'.format(radius, latitude, longitude))
            queries.extend([
                'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="fast_food"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="aquarium"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude)
            ])
            if weather_cat == "Outdoors Climate":
                queries.extend([
                    'node["leisure"="park"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["leisure"="garden"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["leisure"="picnic_site"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["tourism"="viewpoint"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["tourism"="zoo"](around:{},{},{});'.format(radius, latitude, longitude)
                ])
        elif preference in ("Cultural Enthusiast", "Art Aficionado"):
            if weather_cat == "Indoors Climate":
                queries.extend([
                    'node["tourism"="museum"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["tourism"="art_gallery"](around:{},{},{});'.format(radius, latitude, longitude)
                ])
            queries.extend([
                'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="cinema"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["shop"="mall"](around:{},{},{});'.format(radius, latitude, longitude)
            ])
        elif preference == "Food Connoisseur":
            queries.extend([
                'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="cinema"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="bar"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["shop"="mall"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="pub"](around:{},{},{});'.format(radius, latitude, longitude),
                'node["amenity"="fast_food"](around:{},{},{});'.format(radius, latitude, longitude)
            ])
            if weather_cat == "Outdoors Climate":
                queries.extend([
                    'node["tourism"="zoo"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["tourism"="aquarium"](around:{},{},{});'.format(radius, latitude, longitude)
                ])
        elif preference == "Adventure Seeker":
            if weather_cat == "Indoors Climate":
                queries.extend([
                    'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="cinema"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["shop"="mall"](around:{},{},{});'.format(radius, latitude, longitude)
                ])
            elif weather_cat == "Outdoors Climate":
                queries.extend([
                    'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="fast_food"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["shop"="mall"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="amusement_arcade"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["tourism"="theme_park"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["tourism"="viewpoint"](around:{},{},{});'.format(radius, latitude, longitude)
                ])
        elif preference == "Party Animal":
            if weather_cat == "Indoors Climate":
                queries.extend([
                    'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="cinema"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["shop"="mall"](around:{},{},{});'.format(radius, latitude, longitude)
                ])
            elif weather_cat == "Outdoors Climate":
                queries.extend([
                    'node["amenity"="restaurant"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="cafe"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="fast_food"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["shop"="mall"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="pub"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="bar"](around:{},{},{});'.format(radius, latitude, longitude),
                    'node["amenity"="nightclub"](around:{},{},{});'.format(radius, latitude, longitude)
                ])

        query = ''.join(queries)
        overpass_query = '[out:json];(' + query +');out center;'
        response = requests.get(overpass_url, params={'data': overpass_query})
        result = response.json()["elements"]
    return result  



#categorizes the data into Outdoor and Indoor Climate[need further research for better results]
def weather_category(weather_data):
    weather_main = weather_data['weather'][0]['main']
    temperature_celsius = weather_data['main']['temp'] - 273.15

    if weather_main == 'Clear' and temperature_celsius < 33:
        return 'Outdoors Climate'
    elif 'Clouds' in weather_main and temperature_celsius < 33:
        return 'Outdoors Climate'
    elif weather_main == 'Rain':
        return 'Indoors Climate'
    elif weather_main == 'Clear' and temperature_celsius > 33:
        return 'Indoors Climate'
    elif weather_main == 'Thunderstorm':
        return 'Indoors Climate'
    else:
        return 'Outdoors Climate'
    
#categorizes the attraction into a more readable and understandable format  
def categorize_attraction(attraction):
    tags = attraction.get("tags", {})
    category = None
    activity_type = None
    
    if "amenity" in tags:
        amenity = tags["amenity"]
        if amenity in ("restaurant", "bar", "pub", "cafe", "fast_food", "mall", "cinema", "nightclub"):
            category = "Amenity"
            activity_type = "Indoor"
    elif "leisure" in tags:
        leisure = tags["leisure"]
        if leisure in ("park", "playground", "garden", "swimming_pool", "sports_centre", "fitness_centre", "golf_course", "stadium", "amusement_arcade", "theme_park"):
            category = "Leisure"
            activity_type = "Outdoor"
    elif "tourism" in tags:
        tourism = tags["tourism"]
        if tourism in ("museum", "aquarium", "zoo", "art_gallery", "picnic_site", "viewpoint"):
            category = "Tourism"
            activity_type = "Indoor"
    
    name = tags.get("name", "Unnamed")
    coordinates = (attraction["lat"], attraction["lon"])

    value =  {
        "name": name,
        "category": category,
        "activity_type": activity_type,
        "coordinates": coordinates
    }
    print("\n\nType of value:", type(value))
    if value is None:
        print("Value is None")
    else:
        print("Value is not None")
        print(value)
    return value

def categorize_attractions(attractions):
    categorized_attractions = []
    for attraction in attractions:
        attraction_info = categorize_attraction(attraction)
        if attraction_info["category"] is not None:
            categorized_attractions.append(attraction_info)
    return categorized_attractions


#route to collect weather data
@route.post("/weather_data")
def getClimateData(city: str):
        validate_city_name(city)
        URL = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={CLIMATE_API_KEY}"
        response = requests.get(URL)
        if response.status_code == 200:
            print(response.json())
            weather_data = response.json()
            category = weather_category(weather_data)
            result = {
                    "category": category,
                    "description": weather_data['weather'][0]['description'],
                    "temperature": weather_data['main']['temp'] - 273.15,
                    "feels_like": weather_data['main']['feels_like'],
                    "temp_min": weather_data['main']['temp_min'],
                    "temp_max": weather_data['main']['temp_max'],
                    "wind_speed": weather_data['wind']['speed'],
                    "wind_direction": weather_data['wind']['deg'],
                    "cloudiness": weather_data['clouds']['all'],
                    "humidity": weather_data['main']['humidity'],
                    "sunrise": weather_data['sys']['sunrise'],
                    "sunset": weather_data['sys']['sunset'],
                    "visibility": weather_data.get('visibility'),
    }

            print(category)
            return result
        else:
            return {"error": "Failed to retrieve weather data from OpenWeatherMap."}
    
   
 #route to generate recommendations based on climate and user preference..
@route.post("/recommendation")
async def getRecommendation(email: str, city: str, search_radius: int):
    try:
        validate_city_name(city)
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={CLIMATE_API_KEY}"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        weather_cat = weather_category(weather_data)
        latitude = weather_data["coord"]["lat"]
        longitude = weather_data["coord"]["lon"]
        preferences = await get_preferences(email)
        attractions = get_nearby_places(latitude, longitude, search_radius, preferences, weather_cat)       
        recommendation = categorize_attractions(attractions)
        return recommendation
    except requests.exceptions.RequestException as e:
        return {"error": f"HTTP request error: {str(e)}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
    
    
    
