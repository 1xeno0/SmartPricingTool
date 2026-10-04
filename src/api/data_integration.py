# Файл: src/api/data_integration.py

import requests
from ftplib import FTP
from typing import Dict

class DataIntegration:
    def fetch_data_from_api(self, url: str, params: Dict[str, str]) -> Dict:
        """Выполняет запрос к API и возвращает полученные данные."""
        response = requests.get(url, params=params)
        return response.json()

    def download_file_from_ftp(self, host: str, username: str, password: str, file_path: str) -> None:
        """Скачивает файл с FTP сервера."""
        with FTP(host) as ftp:
            ftp.login(username, password)
            with open(file_path, 'wb') as file:
                ftp.retrbinary(f'RETR {file_path}', file.write)

# Пример использования
if __name__ == '__main__':
    integrator = DataIntegration()
    api_data = integrator.fetch_data_from_api('https://api.example.com/prices', {'item_id': '123'})
    print(api_data)
    integrator.download_file_from_ftp('ftp.example.com', 'user', 'pass', 'prices.csv')
