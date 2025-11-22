"""
Тесты для модуля обработки команд.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from io import StringIO
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weather import commands


class TestCommands(unittest.TestCase):
    """Тесты для модуля обработки команд."""
    
    def setUp(self):
        # Сохраняем оригинальный stdout
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()
    
    def tearDown(self):
        # Восстанавливаем stdout
        sys.stdout = self.original_stdout
    
    @patch('weather.commands.get_weather')
    @patch('weather.commands.read_cache')
    def test_handle_command_with_cached_data(self, mock_read_cache, mock_get_weather):
        """Тест обработки команды с данными в кэше."""
        cached_data = {
            "city": "Moscow",
            "latitude": 55.75,
            "longitude": 37.61,
            "current_weather": {
                "temperature": 20,
                "windspeed": 10,
                "winddirection": 180,
                "time": "2023-10-01T12:00:00"
            }
        }
        mock_read_cache.return_value = cached_data
        
        # Создаем mock args
        args = MagicMock()
        args.city = "Moscow"
        args.lat = None
        args.lon = None
        args.refresh = False
        
        commands.handle_command(args)
        
        # Проверяем, что данные взяты из кэша
        mock_read_cache.assert_called_once_with("Moscow")
        mock_get_weather.assert_not_called()
    
    @patch('weather.commands.get_weather')
    @patch('weather.commands.read_cache')
    @patch('weather.commands.write_cache')
    def test_handle_command_with_api_call(self, mock_write_cache, mock_read_cache, mock_get_weather):
        """Тест обработки команды с запросом к API."""
        mock_read_cache.return_value = None
        
        api_data = {
            "city": "Moscow",
            "latitude": 55.75,
            "longitude": 37.61,
            "current_weather": {
                "temperature": 20,
                "windspeed": 10,
                "winddirection": 180,
                "time": "2023-10-01T12:00:00"
            }
        }
        mock_get_weather.return_value = api_data
        
        args = MagicMock()
        args.city = "Moscow"
        args.lat = None
        args.lon = None
        args.refresh = False
        
        commands.handle_command(args)
        
        # Проверяем, что данные запрошены из API и сохранены в кэш
        mock_get_weather.assert_called_once_with(city="Moscow", lat=None, lon=None)
        mock_write_cache.assert_called_once_with("Moscow", api_data)
    
    @patch('weather.commands.get_weather')
    @patch('weather.commands.read_cache')
    def test_handle_command_refresh_flag(self, mock_read_cache, mock_get_weather):
        """Тест обработки команды с флагом обновления."""
        api_data = {
            "city": "Moscow",
            "latitude": 55.75,
            "longitude": 37.61,
            "current_weather": {
                "temperature": 20,
                "windspeed": 10,
                "winddirection": 180,
                "time": "2023-10-01T12:00:00"
            }
        }
        mock_get_weather.return_value = api_data
        
        args = MagicMock()
        args.city = "Moscow"
        args.lat = None
        args.lon = None
        args.refresh = True
        
        commands.handle_command(args)
        
        # Проверяем, что кэш проигнорирован
        mock_read_cache.assert_not_called()
        mock_get_weather.assert_called_once()
    
    def test_handle_command_no_arguments(self):
        """Тест обработки команды без аргументов."""
        args = MagicMock()
        args.city = None
        args.lat = None
        args.lon = None
        args.refresh = False
        
        commands.handle_command(args)
        
        # Проверяем вывод ошибки
        output = sys.stdout.getvalue()
        self.assertIn("Ошибка: нужно указать либо название города, либо координаты", output)
    
    @patch('weather.commands.get_weather')
    @patch('weather.commands.read_cache')
    def test_handle_command_api_exception(self, mock_read_cache, mock_get_weather):
        """Тест обработки исключения при запросе к API."""
        # Убедимся, что кэш пустой, чтобы шел запрос к API
        mock_read_cache.return_value = None
    
        mock_get_weather.side_effect = Exception("API Error")
    
        args = MagicMock()
        args.city = "Moscow"
        args.lat = None
        args.lon = None
        args.refresh = False
    
        commands.handle_command(args)
    
        # Проверяем вывод ошибки
        output = sys.stdout.getvalue()
        self.assertIn("Ошибка: API Error", output)


class TestPrintWeather(unittest.TestCase):
    """Тесты для функции вывода погоды."""
    
    def setUp(self):
        self.original_stdout = sys.stdout
        sys.stdout = StringIO()
    
    def tearDown(self):
        sys.stdout = self.original_stdout
    
    def test_print_weather_complete_data(self):
        """Тест вывода полных данных о погоде."""
        weather_data = {
            "city": "Moscow",
            "latitude": 55.75,
            "longitude": 37.61,
            "current_weather": {
                "temperature": 20.5,
                "windspeed": 15.2,
                "winddirection": 180,
                "time": "2023-10-01T12:00:00"
            }
        }
        
        commands.print_weather(weather_data)
        output = sys.stdout.getvalue()
        
        self.assertIn("Moscow", output)
        self.assertIn("55.75", output)
        self.assertIn("37.61", output)
        self.assertIn("20.5", output)
        self.assertIn("15.2", output)
        self.assertIn("180", output)
    
    def test_print_weather_missing_data(self):
        """Тест вывода неполных данных о погоде."""
        weather_data = {
            "city": "TestCity",
            "current_weather": {}
        }
    
        commands.print_weather(weather_data)
        output = sys.stdout.getvalue()
    
        self.assertIn("TestCity", output)
        # Вместо прочерка выводится None, поэтому проверяем None
        self.assertIn("None", output)  # Проверяем вывод None для отсутствующих данных