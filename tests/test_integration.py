"""
Интеграционные тесты.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weather.parser import create_parser
from weather import commands


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты."""
    
    @patch('weather.commands.get_weather')
    @patch('weather.commands.read_cache')
    @patch('weather.commands.write_cache')
    def test_full_flow_cached(self, mock_write_cache, mock_read_cache, mock_get_weather):
        """Тест полного потока с использованием кэша."""
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
        
        parser = create_parser()
        args = parser.parse_args(["Moscow"])
        
        commands.handle_command(args)
        
        mock_read_cache.assert_called_once_with("Moscow")
        mock_get_weather.assert_not_called()
        mock_write_cache.assert_not_called()
    
    @patch('weather.commands.get_weather')
    @patch('weather.commands.read_cache')
    def test_full_flow_api_call(self, mock_read_cache, mock_get_weather):
        """Тест полного потока с вызовом API."""
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
        
        parser = create_parser()
        args = parser.parse_args(["Moscow"])
        
        commands.handle_command(args)
        
        mock_read_cache.assert_called_once_with("Moscow")
        mock_get_weather.assert_called_once()