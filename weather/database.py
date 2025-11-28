# weather/database.py
"""
Модуль для работы с PostgreSQL базой данных
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .config import get_connection_string

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDatabase:
    """Класс для работы с базой данных погоды"""
    
    def __init__(self):
        self.connection_string = get_connection_string()
    
    def get_connection(self):
        """Создает и возвращает соединение с базой данных"""
        try:
            conn = psycopg2.connect(self.connection_string, cursor_factory=RealDictCursor)
            return conn
        except Exception as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise
    
    def init_db(self) -> None:
        """Инициализирует базу данных: создает таблицы если они не существуют"""
        create_tables_sql = """
        CREATE TABLE IF NOT EXISTS locations (
            id SERIAL PRIMARY KEY,
            city_name VARCHAR(100) NOT NULL,
            latitude DECIMAL(9,6) NOT NULL,
            longitude DECIMAL(9,6) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS weather_records (
            id SERIAL PRIMARY KEY,
            location_id INTEGER REFERENCES locations(id),
            temperature DECIMAL(5,2) NOT NULL,
            wind_speed DECIMAL(5,2) NOT NULL,
            wind_direction INTEGER,
            weather_time TIMESTAMP NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city_name);
        CREATE INDEX IF NOT EXISTS idx_weather_records_time ON weather_records(weather_time);
        CREATE INDEX IF NOT EXISTS idx_weather_records_location ON weather_records(location_id);
        """
        
        try:
            # ИСПРАВЛЕННАЯ СТРОКА: используем self.get_connection() вместо get_connection()
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_tables_sql)
                    conn.commit()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            # Если ошибка прав доступа, просто логируем и продолжаем
            if "must be owner" in str(e):
                logger.warning("Таблицы уже созданы другим пользователем, продолжаем работу...")
            else:
                logger.error(f"Ошибка инициализации БД: {e}")
                # Не поднимаем исключение, чтобы приложение могло продолжить работу
    
    def save_weather_data(self, weather_data: Dict[str, Any]) -> None:
        """
        Сохраняет данные о погоде в базу данных
        
        Args:
            weather_data: Словарь с данными о погоде из API
        """
        try:
            # Извлекаем данные
            city = weather_data.get('city', 'Unknown')
            lat = weather_data.get('latitude')
            lon = weather_data.get('longitude')
            current = weather_data.get('current_weather', {})
            
            if not all([city, lat, lon, current]):
                logger.warning("Неполные данные для сохранения в БД")
                return
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Сохраняем или получаем location
                    location_id = self._get_or_create_location(cursor, city, lat, lon)
                    
                    # Сохраняем запись о погоде
                    insert_weather_sql = """
                    INSERT INTO weather_records 
                    (location_id, temperature, wind_speed, wind_direction, weather_time)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    
                    cursor.execute(insert_weather_sql, (
                        location_id,
                        current.get('temperature'),
                        current.get('windspeed'),
                        current.get('winddirection'),
                        current.get('time')
                    ))
                    
                    conn.commit()
                    logger.info(f"Данные о погоде для {city} сохранены в БД")
                    
        except Exception as e:
            logger.error(f"Ошибка сохранения данных в БД: {e}")
    
    def _get_or_create_location(self, cursor, city: str, lat: float, lon: float) -> int:
        """
        Находит или создает запись о местоположении
        
        Returns:
            int: ID местоположения
        """
        # Пытаемся найти существующее местоположение
        find_sql = "SELECT id FROM locations WHERE city_name = %s AND latitude = %s AND longitude = %s"
        cursor.execute(find_sql, (city, lat, lon))
        result = cursor.fetchone()
        
        if result:
            return result['id']
        
        # Создаем новое местоположение
        insert_sql = """
        INSERT INTO locations (city_name, latitude, longitude) 
        VALUES (%s, %s, %s) 
        RETURNING id
        """
        cursor.execute(insert_sql, (city, lat, lon))
        return cursor.fetchone()['id']
    
    def get_recent_weather(self, city: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Получает последние записи о погоде для города
        
        Args:
            city: Название города
            limit: Количество записей
            
        Returns:
            Список записей о погоде
        """
        try:
            sql = """
            SELECT 
                wr.temperature,
                wr.wind_speed,
                wr.wind_direction,
                wr.weather_time,
                wr.recorded_at,
                l.city_name,
                l.latitude,
                l.longitude
            FROM weather_records wr
            JOIN locations l ON wr.location_id = l.id
            WHERE l.city_name = %s
            ORDER BY wr.weather_time DESC
            LIMIT %s
            """
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (city, limit))
                    results = cursor.fetchall()
                    
                    # Конвертируем в обычные словари
                    return [dict(row) for row in results]
                    
        except Exception as e:
            logger.error(f"Ошибка получения данных из БД: {e}")
            return []
    
    def get_weather_stats(self, city: str, days: int = 7) -> Dict[str, Any]:
        """
        Получает статистику по погоде за указанный период
        
        Args:
            city: Название города
            days: Количество дней для анализа
            
        Returns:
            Словарь со статистикой
        """
        try:
            sql = """
            SELECT 
                AVG(temperature) as avg_temp,
                MAX(temperature) as max_temp,
                MIN(temperature) as min_temp,
                AVG(wind_speed) as avg_wind,
                COUNT(*) as records_count
            FROM weather_records wr
            JOIN locations l ON wr.location_id = l.id
            WHERE l.city_name = %s 
            AND wr.weather_time >= CURRENT_DATE - INTERVAL '%s days'
            """
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (city, days))
                    result = cursor.fetchone()
                    
                    if result:
                        return dict(result)
                    else:
                        return {}
                        
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {}

# Глобальный экземпляр базы данных
db = WeatherDatabase()