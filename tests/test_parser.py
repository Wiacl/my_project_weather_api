"""
Тесты для модуля парсера аргументов.
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from weather.parser import create_parser


class TestParser(unittest.TestCase):
    """Тесты для модуля парсера аргументов."""
    
    def setUp(self):
        self.parser = create_parser()
    
    def test_parser_city_argument(self):
        """Тест парсера с аргументом города."""
        args = self.parser.parse_args(["Moscow"])
        self.assertEqual(args.city, "Moscow")
        self.assertIsNone(args.lat)
        self.assertIsNone(args.lon)
        self.assertFalse(args.refresh)
    
    def test_parser_coordinates_arguments(self):
        """Тест парсера с аргументами координат."""
        args = self.parser.parse_args(["--lat", "55.75", "--lon", "37.61"])
        self.assertIsNone(args.city)
        self.assertEqual(args.lat, 55.75)
        self.assertEqual(args.lon, 37.61)
        self.assertFalse(args.refresh)
    
    def test_parser_refresh_flag(self):
        """Тест парсера с флагом обновления."""
        args = self.parser.parse_args(["Moscow", "--refresh"])
        self.assertEqual(args.city, "Moscow")
        self.assertTrue(args.refresh)
    
    def test_parser_no_arguments(self):
        """Тест парсера без аргументов."""
        args = self.parser.parse_args([])
        self.assertIsNone(args.city)
        self.assertIsNone(args.lat)
        self.assertIsNone(args.lon)
        self.assertFalse(args.refresh)