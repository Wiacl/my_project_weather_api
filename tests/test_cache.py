"""
Тесты для модуля кэширования.
"""

import unittest
import sys
import os
import json
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weather.cache import read_cache, write_cache, CACHE_FILE, CACHE_TTL


class TestCache(unittest.TestCase):
    """Тесты для модуля кэширования."""
    
    def setUp(self):
        # Убедимся, что файл кэша не существует перед тестами
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    
    def tearDown(self):
        # Очистка после тестов
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    
    def test_write_and_read_cache(self):
        """Тест записи и чтения из кэша."""
        test_data = {"temperature": 20, "city": "Test"}
        write_cache("Moscow", test_data)
        
        # Проверяем, что файл создан
        self.assertTrue(os.path.exists(CACHE_FILE))
        
        # Читаем данные
        cached_data = read_cache("Moscow")
        self.assertEqual(cached_data, test_data)
    
    def test_read_cache_nonexistent_city(self):
        """Тест чтения несуществующего города из кэша."""
        test_data = {"temperature": 20}
        write_cache("Moscow", test_data)
        
        cached_data = read_cache("London")
        self.assertIsNone(cached_data)
    
    def test_read_cache_expired(self):
        """Тест чтения устаревшего кэша."""
        test_data = {"temperature": 20}
        
        # Создаем устаревшую запись
        cache = {
            "Moscow": {
                "timestamp": (datetime.now() - CACHE_TTL - timedelta(minutes=1)).isoformat(),
                "weather": test_data
            }
        }
        
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f)
        
        cached_data = read_cache("Moscow")
        self.assertIsNone(cached_data)
    
    def test_read_cache_corrupted_file(self):
        """Тест чтения поврежденного файла кэша."""
        # Создаем поврежденный JSON
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            f.write("invalid json content")
        
        cached_data = read_cache("Moscow")
        self.assertIsNone(cached_data)
    
    def test_cache_file_creation(self):
        """Тест создания файла кэша."""
        self.assertFalse(os.path.exists(CACHE_FILE))
        write_cache("Test", {"data": "test"})
        self.assertTrue(os.path.exists(CACHE_FILE))
        