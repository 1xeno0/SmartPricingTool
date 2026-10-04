import pandas as pd
from typing import List, Dict
from ..database.database_manager import DatabaseManager

class DataProcessor:
    def __init__(self, db_path: str):
        """Инициализация с подключением к базе данных."""
        self.db_manager = DatabaseManager(db_path)

    def process_data(self, data: List[Dict]) -> pd.DataFrame:
        """Преобразует список словарей в DataFrame и обогащает его наценками."""
        df = pd.DataFrame(data)
        df['markup'] = df['category'].apply(self.db_manager.get_markup_by_category)
        df['final_price'] = df['base_price'] * (1 + df['markup'] / 100)
        return df

# Пример использования
if __name__ == '__main__':
    processor = DataProcessor('path_to_your_database.db')
    raw_data = [{'name': 'Laptop', 'category': 'Electronics', 'base_price': 1000}]
    processed_data = processor.process_data(raw_data)
    print(processed_data)
