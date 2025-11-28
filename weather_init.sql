-- weather_init.sql
-- Создаем базу данных (если не существует)
CREATE DATABASE weather_db;

-- Подключаемся к созданной базе данных
\c weather_db;

-- Создаем пользователя
CREATE USER weather_user WITH PASSWORD 'weather_pass';

-- Даем права пользователю
GRANT ALL PRIVILEGES ON DATABASE weather_db TO weather_user;

-- Создаем таблицы
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

-- Создаем индексы
CREATE INDEX IF NOT EXISTS idx_locations_city ON locations(city_name);
CREATE INDEX IF NOT EXISTS idx_weather_records_time ON weather_records(weather_time);
CREATE INDEX IF NOT EXISTS idx_weather_records_location ON weather_records(location_id);

-- Даем права на схему и последовательности
GRANT ALL ON SCHEMA public TO weather_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO weather_user;

-- Даем права на таблицы
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO weather_user;