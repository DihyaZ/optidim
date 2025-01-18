import requests
from django.conf import settings

# Fonction pour récupérer les données météo actuelles d'OpenWeather (par ville)
def get_weather_data(city):
    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)

    if response.status_code == 200:
        weather_data = response.json()

        # Vérification et calcul de la température moyenne
        temp_min = weather_data['main'].get('temp_min', 0)
        temp_max = weather_data['main'].get('temp_max', 0)
        temp_moyenne = round((temp_min + temp_max) / 2, 1)

        # Ajout au dictionnaire des données météo
        weather_data['temp_moyenne'] = temp_moyenne

        return weather_data
    else:
        return None


# Fonction pour récupérer les données météorologiques journalières d'Open-Meteo (par latitude/longitude)
def get_meteo_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,sunshine_duration,shortwave_radiation_sum&timezone=Europe/Paris"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print("Réponse API :", data)  # Débogage

        if "daily" in data:
            meteo_data = []
            for i in range(len(data["daily"]["time"])):
                meteo_data.append({
                    "date": data["daily"]["time"][i],
                    "temp_max": data["daily"]["temperature_2m_max"][i],
                    "temp_min": data["daily"]["temperature_2m_min"][i],
                    "sunshine": data["daily"]["sunshine_duration"][i],  # En minutes
                    "irradiation": data["daily"]["shortwave_radiation_sum"][i]  # En kWh/m²
                })
            return meteo_data
        else:
            print("⚠️ Erreur : Clé 'daily' non trouvée dans la réponse.")
            return None
    else:
        print(f"⚠️ Erreur API : {response.status_code}")
        return None


# Test avec Open-Meteo (coordonnées de Toulouse)
lat, lon = 43.6043, 1.4437
meteo_data = get_meteo_data(lat, lon)

if meteo_data:
    for day in meteo_data:
        print(day)
else:
    print("⚠️ Aucune donnée récupérée.")


# utils.py
def get_coordinates(city):
    api_key = settings.OPENWEATHER_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        return lat, lon
    else:
        return None, None
