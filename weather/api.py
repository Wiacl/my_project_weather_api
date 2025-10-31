"""
Модуль для работы с Open-Meteo API и OpenStreetMap Reverse Geocoding с помощью requests.

"""

import requests

from typing import Dict, Any, Optional

from colorama import Fore, Style

def get_coordinates(city: str) -> tuple[float, float]:
    """
    Получает координаты города через Open-Meteo Geocoding API.
    
    Args:
        city (str): Название города для поиска координат
        
    Returns:
        tuple[float, float]: Кортеж с широтой и долготой города
        
    Raises:
        ValueError: Если город не найден
        requests.RequestException: При ошибках сетевого запроса    
    """
      
    # Формируем URL для запроса к API
    
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
    
    #  HTTP-запрос с таймаутом 10 секунд
    resp = requests.get(url, timeout=10)
    resp.raise_for_status() #проверка статуса ответа
    data = resp.json()     #парсинг полученного ответа json

    #проврека на наличие результата в ответе 
    
    if not data.get("results"):
        raise ValueError(f"Город '{city}' не найден.")

    #из первого результата извлекаем координаты
    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]
    return lat, lon


def get_location_info(
    city: Optional[str] = None, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """
    Определяет координаты и название города.
    Если указан город — используется Open-Meteo Geocoding API.
    Если указаны координаты — используется OpenStreetMap Reverse Geocoding.
    
    Args:
        city (str, optional): Название города
        lat (float, optional): Широта
        lon (float, optional): Долгота
        
    Returns:
        Dict[str, Any]: Словарь с ключами 'city', 'lat', 'lon' или None при ошибке
    """
    

    # Вариант 1: пользователь ввёл город — ищем координаты через Open-Meteo
    
    if city and not lat and not lon:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&language=ru&count=1"
        try:
            response = requests.get(url, timeout=10) #запрос к апи
            response.raise_for_status()         #смотрим статус запроса
            data = response.json()

            #проверяем наличие ответа и берем самый релевантный (первый)
            if "results" in data and len(data["results"]) > 0:
                loc = data["results"][0]
                return {
                    "city": loc.get("name"),
                    "lat": loc.get("latitude"),
                    "lon": loc.get("longitude"),
                }
            else:
                print(f"{Fore.RED} Город '{city}' не найден.{Style.RESET_ALL}")
                return None
        except Exception as e:
            print(f"{Fore.RED}⚠ Ошибка геокодирования Open-Meteo: {e}{Style.RESET_ALL}")
            return None

    # Вариант 2: пользователь ввёл координаты — ищем город через OpenStreetMap
    elif lat and lon:
        # Формируем URL для обратного геокодирования (координаты -> адрес)
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&accept-language=ru"
        
        headers = {"User-Agent": "WeatherCLI/1.0 (by OpenAI)"} # Обязательный заголовок для OSM API
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

             # Ищем название населенного пункта в ответе с приоритетом по типам
            city_name = (
                data.get("address", {}).get("city")
                or data.get("address", {}).get("town")
                or data.get("address", {}).get("village")
                or data.get("address", {}).get("state")
                or "Неизвестно"
            )

            #флоат для единости 
            return {
                "city": city_name,
                "lat": float(lat),
                "lon": float(lon),
            }

        except Exception as e:
            print(f"{Fore.RED} Ошибка обратного геокодирования OSM: {e}{Style.RESET_ALL}")
            return None

    else:
        print(f"{Fore.YELLOW} Укажите город или координаты.{Style.RESET_ALL}")
        return None



def get_weather(
    city: Optional[str] = None, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
) -> Dict[str, Any]:
    """
    Получает текущую погоду по названию города или координатам.
    
    Args:
        city (str, optional): Название города
        lat (float, optional): Широта
        lon (float, optional): Долгота
        
    Returns:
        Dict[str, Any]: Словарь с данными о погоде, включая:
            - city: название города
            - latitude, longitude: координаты
            - current_weather: текущие погодные условия
            
    Raises:
        ValueError: Если не удалось определить местоположение
        ConnectionError: При ошибках получения данных о погоде
    """
    
    #получим данные о местоположении
    
    loc = get_location_info(city=city, lat=lat, lon=lon)
    if not loc:
        raise ValueError("Не удалось определить местоположение.")

    #извлекаем
    lat, lon = loc["lat"], loc["lon"]
    city_name = loc["city"]
    
    #url для запроса погоды
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        data["city"] = city_name
        return data
    except Exception as e:
        raise ConnectionError(f"Ошибка получения данных погоды: {e}")
    

