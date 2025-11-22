"""
Скрипт для запуска всех тестов проекта.
"""

import unittest
import sys
import os

def run_all_tests():
    """Запускает все тесты проекта."""
    # Добавляем текущую директорию в путь Python
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Находим и загружаем все тесты
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем код успеха/ошибки для CI/CD
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_all_tests())