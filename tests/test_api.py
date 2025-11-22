"""
Тесты для модуля работы с API.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weather.api import get_coordinates, get_location_info, get_weather


class TestAPI(unittest.TestCase):
    """Тесты для модуля работы с API."""
    
    @patch('weather.api.requests.get')
    def test_get_coordinates_success(self, mock_get):
        """Тест успешного получения координат."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"latitude": 55.75, "longitude": 37.61}]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        lat, lon = get_coordinates("Moscow")
        self.assertEqual(lat, 55.75)
        self.assertEqual(lon, 37.61)
    
    @patch('weather.api.requests.get')
    def test_get_coordinates_city_not_found(self, mock_get):
        """Тест получения координат для несуществующего города."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with self.assertRaises(ValueError):
            get_coordinates("NonexistentCity")
    
    @patch('weather.api.requests.get')
    def test_get_coordinates_request_exception(self, mock_get):
        """Тест исключения при запросе координат."""
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception):
            get_coordinates("Moscow")
    
    @patch('weather.api.requests.get')
    def test_get_location_info_by_city(self, mock_get):
        """Тест получения информации о местоположении по городу."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {
                    "name": "Moscow",
                    "latitude": 55.75,
                    "longitude": 37.61
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_location_info(city="Moscow")
        self.assertEqual(result["city"], "Moscow")
        self.assertEqual(result["lat"], 55.75)
        self.assertEqual(result["lon"], 37.61)
    
    @patch('weather.api.requests.get')
    def test_get_location_info_by_coordinates(self, mock_get):
        """Тест получения информации о местоположении по координатам."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "address": {
                "city": "Moscow"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_location_info(lat=55.75, lon=37.61)
        self.assertEqual(result["city"], "Moscow")
        self.assertEqual(result["lat"], 55.75)
        self.assertEqual(result["lon"], 37.61)
    
    def test_get_location_info_no_parameters(self):
        """Тест получения информации о местоположении без параметров."""
        result = get_location_info()
        self.assertIsNone(result)
    
    @patch('weather.api.get_location_info')
    @patch('weather.api.requests.get')
    def test_get_weather_success(self, mock_get, mock_location):
        """Тест успешного получения погоды."""
        mock_location.return_value = {
            "city": "Moscow",
            "lat": 55.75,
            "lon": 37.61
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "latitude": 55.75,
            "longitude": 37.61,
            "current_weather": {
                "temperature": 20,
                "windspeed": 10,
                "winddirection": 180,
                "time": "2023-10-01T12:00:00"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = get_weather(city="Moscow")
        self.assertEqual(result["city"], "Moscow")
        self.assertIn("current_weather", result)
    
    @patch('weather.api.get_location_info')
    def test_get_weather_location_failed(self, mock_location):
        """Тест получения погоды при ошибке определения местоположения."""
        mock_location.return_value = None
        
        with self.assertRaises(ValueError):
            get_weather(city="NonexistentCity")
    
    @patch('weather.api.get_location_info')
    @patch('weather.api.requests.get')
    def test_get_weather_connection_error(self, mock_get, mock_location):
        """Тест получения погоды при ошибке соединения."""
        mock_location.return_value = {
            "city": "Moscow",
            "lat": 55.75,
            "lon": 37.61
        }
        mock_get.side_effect = Exception("API unavailable")
        
        with self.assertRaises(ConnectionError):
            get_weather(city="Moscow")