import string


ABC = list(string.ascii_uppercase)
DEFAULT_CURRENCIES = ['BYN', 'RUB', 'USD', 'EUR']
DEFAULT_COLUMNS = ['Наименование', 'РРЦ', 'Цена', 'Артикул', 'Бренд', 'Оптовая Цена', 'Наличие', 'Категория']
DEFAULT_COLUMNS_EN = ['NAME', 'RRC', 'PRICE', 'SKU', 'BRAND', 'BUY PRICE', 'AVAILABILTY', 'Category']
ADDITIONAL_COLUMNS_FOR_MAIN_DATA_PANEL = ['BRAND_ID', 'CATEGPRY_ID']
DEFAULT_PRICES = ['Эталонный', 'Поставщик', 'Конкурент']

DEFAULT_ESTIMATES_COLUMNS = ["Цена от", "Цена до", "Мин. Процент", "Нету Конкурента %", 'Действие']
DEFAULT_ESTIMATES_COLUMNS_EN = ["min_price", "max_price", "min_percentage", "no_competitor_percentage", 'Действие']

HOME_ICON = 'src/img/home_icon.png'
DELETE_ICON = 'src/img/delete_icon.png'
ADD_ICON = 'src/img/add_icon.png'
PRICE_ICON = 'src/img/price_icon.png'
SYNC_ICON = 'src/img/sync_icon.png'
SAVE_ICON = 'src/img/save_icon.png'
CONNECT_ICON = 'src/img/connect_icon.png'
SCRAPER_ICON = 'src/img/download_icon.png'
ESTIMATE_ICON = 'src/img/estimate_icon.png'
IMPORT_ICON = 'src/img/import_icon.png'
EXPORT_ICON = 'src/img/export_icon.png'
EDIT_ICON = 'src/img/edit_icon.png'

DATABASE_PATH = 'src/database/db/appData.db'