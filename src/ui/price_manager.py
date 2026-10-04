import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QListWidget,
                             QLineEdit, QToolBar, QAction, QSplitter, QWidget, QListWidgetItem, QMessageBox, QFileDialog, QLabel, QFormLayout, QComboBox, QTableWidgetItem,
                             QGroupBox, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
import pandas as pd
import csv
import chardet, itertools

from src.database.database import *
from src.utils import price_sync

from config import *


def detect_csv_delimiter_and_encoding(file_path, sample_size=1024):
    """Определяет разделитель и кодировку для CSV файла."""
    with open(file_path, 'rb') as file:
        raw_data = file.read(sample_size)
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(raw_data.decode(encoding)).delimiter
    return delimiter, encoding

class PriceManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.prices = []  # Правильное место для инициализации списка прайсов
        self.last_selected_price_index = None
        self.last_selected_list_index = None
        self.initUI()
        #self.load_prices()  # Загружаем прайсы при инициализации
        self.populate_price_list()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        # Основной макет, горизонтальный сплиттер для левой и правой панели
        main_layout.setContentsMargins(3, 3, 3, 3)  # Уменьшение маргинов
        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.setHandleWidth(1)

        # Вертикальный сплиттер для основной панели и панели предпросмотра
        vertical_splitter = QSplitter(Qt.Vertical)
        vertical_splitter.setHandleWidth(0)

        # Левая панель
        left_panel = QVBoxLayout()
        left_panel.setSpacing(3)
        self.toolbar = QToolBar("Price Tools", self)
        self.toolbar.setIconSize(QSize(20, 20))
        left_panel.addWidget(self.toolbar)

        add_action = QAction(QIcon(ADD_ICON), 'Добавить прайс', self)
        add_action.triggered.connect(self.openAddPriceDialog)
        self.toolbar.addAction(add_action)

        delete_action = QAction(QIcon(DELETE_ICON), 'Удалить прайс', self)
        delete_action.triggered.connect(self.delete_price)
        self.toolbar.addAction(delete_action)

        self.sync_action = QAction(QIcon(SYNC_ICON), 'Синхронизировать', self)
        self.sync_action.triggered.connect(self.sync_prices)
        self.toolbar.addAction(self.sync_action)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по прайсам...")
        self.search_field.textChanged.connect(self.filterPrices)
        left_panel.addWidget(self.search_field)

        self.price_list = QListWidget()
        self.price_list.itemClicked.connect(self.price_on_select)
        self.price_list.itemDoubleClicked.connect(self.priceDoubleClicked)
        self.price_list.itemChanged.connect(self.on_item_changed)
        left_panel.addWidget(self.price_list)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        horizontal_splitter.addWidget(left_container)

        # Правая панель
        self.right_panel = QHBoxLayout()
        self.right_panel.setSpacing(3)

        self.lists_layout = QVBoxLayout()

        self.lists_toolbar = QToolBar("Lists Tools", self)
        self.lists_toolbar.setIconSize(QSize(20, 20))
        self.lists_layout.addWidget(self.lists_toolbar)

        self.lists_list = QListWidget()
        self.lists_list.setFixedWidth(250)
        self.lists_list.itemClicked.connect(self.list_on_select)
        self.lists_list.itemDoubleClicked.connect(self.edit_list)
        self.lists_layout.addWidget(self.lists_list)

        self.add_list_action = QAction(QIcon(ADD_ICON), 'Добавить лист', self)
        self.add_list_action.triggered.connect(self.add_list)
        self.lists_toolbar.addAction(self.add_list_action)

        self.delete_list_action = QAction(QIcon(DELETE_ICON), 'Удалить лист', self)
        self.delete_list_action.triggered.connect(self.delete_list)
        self.lists_toolbar.addAction(self.delete_list_action)

        self.mapping_layout = QVBoxLayout()

        self.mapping_label = QLabel("Настройки маппинга:")
        self.mapping_layout.addWidget(self.mapping_label)
        self.mapping_table = QTableWidget(0, 4)
        self.mapping_table.setHorizontalHeaderLabels(["Поле БД", "Колонка файла", "Доп", "Действие"])
        self.mapping_table.cellChanged.connect(self.update_field)
        self.mapping_layout.addWidget(self.mapping_table)

        # Кнопка для добавления настроек маппинга
        add_mapping_button = QPushButton("Добавить маппинг")
        add_mapping_button.clicked.connect(self.add_mapping_row)
        self.mapping_layout.addWidget(add_mapping_button) 

        # Все виджеты настроек
        self.settings_layout = QVBoxLayout()

        self.rows_settings_frame = QGroupBox('Строки')
        self.rows_settings_frame.setFixedWidth(250)
        self.rows_settings_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.rows_settigns_layout = QVBoxLayout()
        self.rows_settings_frame.setLayout(self.rows_settigns_layout)

        self.top_layout = QHBoxLayout()
        self.start_label = QLabel('С:')
        self.start_input = QLineEdit()
        self.start_input.setFixedWidth(100)
        self.start_input.textChanged.connect(self.update_rows_settings)
        self.top_layout.addWidget(self.start_label)
        self.top_layout.addWidget(self.start_input)

        self.bottom_layout = QHBoxLayout()
        self.end_label = QLabel('По:')
        self.end_input = QLineEdit()
        self.end_input.setFixedWidth(100)
        self.end_input.textChanged.connect(self.update_rows_settings)
        self.bottom_layout.addWidget(self.end_label)
        self.bottom_layout.addWidget(self.end_input)

        self.rows_settigns_layout.addLayout(self.top_layout)
        self.rows_settigns_layout.addLayout(self.bottom_layout)

        self.currencies_frame = QGroupBox('Валюта')
        self.currencies_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.currencies_layout = QVBoxLayout()
        self.currencies_frame.setLayout(self.currencies_layout)

        self.top_layout = QHBoxLayout()
        self.price_label = QLabel('Цена:')
        self.price_currencies_comboBox = QComboBox()
        self.price_currencies_comboBox.addItems(DEFAULT_CURRENCIES)
        self.price_currencies_comboBox.currentTextChanged.connect(self.update_currency_settings)
        self.top_layout.addWidget(self.price_label)
        self.top_layout.addWidget(self.price_currencies_comboBox)

        self.bottom_layout = QHBoxLayout()
        self.rrc_label = QLabel('РРЦ:')
        self.rrc_combobox = QComboBox()
        self.rrc_combobox.addItems(DEFAULT_CURRENCIES)
        self.rrc_combobox.currentTextChanged.connect(self.update_currency_settings)
        self.bottom_layout.addWidget(self.rrc_label)
        self.bottom_layout.addWidget(self.rrc_combobox)

        self.currencies_layout.addLayout(self.top_layout)
        self.currencies_layout.addLayout(self.bottom_layout)

        self.settings_layout.addWidget(self.rows_settings_frame)
        self.settings_layout.addWidget(self.currencies_frame)

        self.right_panel.addLayout(self.lists_layout)
        self.right_panel.addLayout(self.settings_layout)
        self.right_panel.addLayout(self.mapping_layout)

        right_container = QWidget()
        right_container.setLayout(self.right_panel)

        horizontal_splitter.addWidget(right_container)

        vertical_splitter.addWidget(horizontal_splitter)

        # Панель предпросмотра
        preview_panel = QVBoxLayout()
        self.preview_table = QTableWidget()
        preview_panel.addWidget(self.preview_table)

        preview_container = QWidget()
        preview_container.setLayout(preview_panel)
        vertical_splitter.addWidget(preview_container)

        # Регулировка размеров панелей
        vertical_splitter.setSizes([400, 200])
        horizontal_splitter.setSizes([200, 800])

        main_layout.addWidget(vertical_splitter)

    def sync_prices(self):
        if price_sync.sync_prices():
            QMessageBox.information(self, "Успех", "Прайсы были обновлены!")

    def on_item_changed(self, item):
        index = self.price_list.row(item)
        # Check the state of the item
        if item.checkState() == Qt.Checked:
            update_price_activity(index+1, True)
        else:
            update_price_activity(index+1, False)

    def price_on_select(self):
        try:
            selected_item = self.price_list.currentItem()
            self.last_selected_price_index = self.price_list.row(selected_item) + 1

            self.last_selected_list_index = None

            selected_price_path = get_price(self.last_selected_price_index)[2]
            self.load_column_mapping_ui(selected_price_path)

            self.lists_list.clear()
            self.mapping_table.clearContents()
            self.mapping_table.setRowCount(0)
            self.populate_lists_list()
        except:
            pass

    def list_on_select(self):        
        selected_item = self.lists_list.currentItem()
        self.last_selected_list_index = self.lists_list.row(selected_item) + 1
        self.mapping_table.clearContents()
        self.mapping_table.setRowCount(0)

        price_path = get_price(self.last_selected_price_index)[2]

        print(selected_item.text())
        self.load_column_mapping_ui(price_path, selected_item.text())

        self.populate_settings()
        self.populate_fields()

    def populate_price_list(self):
        all_prices = fetch_prices()

        for price in all_prices:
            item = QListWidgetItem(f'{price[1]} ({price[3]})')
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkbox
            if price[-1]:
                item.setCheckState(Qt.Checked)  # Set initial state
            else:
                item.setCheckState(Qt.Unchecked)  # Set initial state
            self.price_list.addItem(item)

    def populate_lists_list(self):
        all_lists = fetch_lists(self.last_selected_price_index)

        for list in all_lists:
            self.lists_list.addItem(f'{list[-1]}')

    def populate_settings(self):
        settings = get_settings(self.last_selected_list_index, self.last_selected_price_index)

        self.start_input.setText(str(settings[1]))
        self.end_input.setText(str(settings[2]))

        self.price_currencies_comboBox.setCurrentIndex(DEFAULT_CURRENCIES.index(settings[3]))
        self.rrc_combobox.setCurrentIndex(DEFAULT_CURRENCIES.index(settings[4]))

    def populate_fields(self):
        all_fields = fetch_fields(self.last_selected_list_index, self.last_selected_price_index)
        all_fields = [[element if element is not None else '' for element in inner_list] for inner_list in all_fields]

        for field in all_fields:
            row_count = self.mapping_table.rowCount()
            self.mapping_table.insertRow(row_count)
            combo_db_field = QComboBox()
            combo_db_field.addItems(DEFAULT_COLUMNS_EN)  # Example database fields
            combo_db_field.setCurrentIndex(DEFAULT_COLUMNS_EN.index(field[3]))
            combo_db_field.currentIndexChanged.connect(lambda index, row=row_count: self.db_field_changed(row, index))

            combo_file_column = QLineEdit(field[2])
            combo_file_column.textChanged.connect(lambda text, row=row_count: self.file_column_changed(row, text))

            additional_data_edit = QLineEdit(field[4])
            additional_data_edit.textChanged.connect(lambda text, row=row_count: self.additional_data_changed(row, text))

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda: self.delete_mapping_row(row_count))

            self.mapping_table.setCellWidget(row_count, 0, combo_db_field)
            self.mapping_table.setCellWidget(row_count, 1, combo_file_column)
            self.mapping_table.setCellWidget(row_count, 2, additional_data_edit)
            self.mapping_table.setCellWidget(row_count, 3, delete_button)

    def additional_data_changed(self, row, text):
        # Example: print or handle change
        print(row+1, text, 'additional_data', self.last_selected_list_index, self.last_selected_price_index)
        update_field(row+1, text, 'additional_data', self.last_selected_list_index, self.last_selected_price_index)

    def append_list(self, list_name):
        add_list(list_name, self.last_selected_price_index)
        self.last_selected_list_index = len(fetch_lists(self.last_selected_price_index))
        
        self.lists_list.addItem(list_name)

    def append_price(self, price_name, price_path, price_type):
        add_price(price_name, price_path, price_type)

        item = QListWidgetItem(f'{price_name} ({price_type})')
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkbox
        item.setCheckState(Qt.Unchecked)  # Set initial state
        self.price_list.addItem(item)

    def change_list(self, list_name):
        if self.last_selected_list_index:
            update_list(self.last_selected_list_index, list_name, self.last_selected_price_index)

            item_to_change = self.lists_list.item(self.last_selected_list_index-1)
            item_to_change.setText(list_name)

    def change_price(self, price_name, price_path, price_type):
        if self.last_selected_price_index:
            update_price(self.last_selected_price_index, price_name, price_path, price_type)

            item_to_change = self.price_list.item(self.last_selected_price_index-1)
            item_to_change.setText(f'{price_name} ({price_type})')
        else:
            QMessageBox.critical(self, "Ошибка", "Вы не выбрали прайс")

    def delete_list(self):
        if self.last_selected_list_index:
            response = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот лист?", QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.Yes:
                self.lists_list.takeItem(self.last_selected_list_index-1)
                delete_price(self.last_selected_list_index)
                self.preview_table.clear()  # Очищаем таблицу деталей

    def delete_price(self):
        response = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот прайс?", QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            self.price_list.takeItem(self.last_selected_price_index-1)
            delete_price(self.last_selected_price_index)
            self.preview_table.clear()  # Очищаем таблицу деталей

    def add_list(self):
        if self.last_selected_price_index:
            dialog = AddListDialog(self)
            if dialog.exec_():
                print("Лист добавлен")
        else:
            QMessageBox.critical(self, "Ошибка", "Вы не выбрали прайс")


    def edit_list(self):
        if self.last_selected_price_index:
            dialog = EditListDialog(self)
            if dialog.exec_():
                print("Лист изменен")
        else:
            QMessageBox.critical(self, "Ошибка", "Вы не выбрали прайс")

    def update_rows_settings(self):
        if self.last_selected_list_index:
            update_settings(self.start_input.text(), 'start_row', self.last_selected_list_index, self.last_selected_price_index)
            update_settings(self.end_input.text(), 'end_row', self.last_selected_list_index, self.last_selected_price_index)

    def update_currency_settings(self):
        if self.last_selected_list_index:
            update_settings(self.price_currencies_comboBox.currentText(), 'price_currency', self.last_selected_list_index, self.last_selected_price_index)
            update_settings(self.rrc_combobox.currentText(), 'rrc_currency', self.last_selected_list_index, self.last_selected_price_index)

    def load_data_preview(self):
        try:
            rows = int(self.preview_rows_input.text())
            # Загрузка данных для превью
            # Это место для реализации загрузки данных
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_field(self, row, column):
        # This method is called whenever a cell is changed
        print(f"Cell changed in row {row}, column {column}")
        row_values = [self.table.item(row, col).text() if self.table.item(row, col) else '' for col in range(self.table.columnCount())]
        print(f"Row {row} values: {row_values}")

    def db_field_changed(self, row, index):
        # Example: print or handle change
        print(row+1, DEFAULT_COLUMNS_EN[index], 'final_column', self.last_selected_list_index, self.last_selected_price_index)
        update_field(row+1, DEFAULT_COLUMNS_EN[index], 'final_column', self.last_selected_list_index, self.last_selected_price_index)

    def file_column_changed(self, row, text):
        # Example: print or handle change
        print(row+1, text, 'file_field', self.last_selected_list_index, self.last_selected_price_index)
        update_field(row+1, text, 'file_field', self.last_selected_list_index, self.last_selected_price_index)

    def add_mapping_row(self):
        if self.last_selected_price_index:
            if self.last_selected_list_index:
                row_count = self.mapping_table.rowCount()
                self.mapping_table.insertRow(row_count)
                combo_db_field = QComboBox()
                combo_db_field.addItems(DEFAULT_COLUMNS_EN)  # Example database fields
                combo_db_field.currentIndexChanged.connect(lambda index, row=row_count: self.db_field_changed(row, index))

                combo_file_column = QLineEdit()
                combo_file_column.textChanged.connect(lambda text, row=row_count: self.file_column_changed(row, text))

                additional_data_edit = QLineEdit()
                additional_data_edit.textChanged.connect(lambda text, row=row_count: self.additional_data_changed(row, text))

                add_field(self.last_selected_list_index, None, DEFAULT_COLUMNS_EN[0], None, self.last_selected_price_index)

                delete_button = QPushButton("Удалить")
                delete_button.clicked.connect(lambda: self.delete_mapping_row(row_count))

                self.mapping_table.setCellWidget(row_count, 0, combo_db_field)
                self.mapping_table.setCellWidget(row_count, 1, combo_file_column)
                self.mapping_table.setCellWidget(row_count, 2, additional_data_edit)
                self.mapping_table.setCellWidget(row_count, 3, delete_button)
            else:
                QMessageBox.critical(self, "Ошибка", "Вы не выбрали лист")
        else:
            QMessageBox.critical(self, "Ошибка", "Вы не выбрали прайс")

    def delete_mapping_row(self, row):
        self.mapping_table.removeRow(row)
        delete_field(row+1, self.last_selected_list_index, self.last_selected_price_index)

    def openAddPriceDialog(self):
        allow_reference = not self.hasReferencePrice()
        dialog = AddPriceDialog(allow_reference, self)  # Передаем self.addPrice как коллбэк
        if dialog.exec_():
            print("Прайс добавлен")

    def hasReferencePrice(self):
        # Проверка на наличие эталонного прайса
        return any(price['type'] == 'Эталонный' for price in self.prices)

    def filterPrices(self, text):
        """Фильтрует список прайсов на основе введенного текста и обновляет GUI.

        Args:
            text (str): Текст для фильтрации списка прайсов.
        """
        if not text.strip():  # Если строка поиска пуста, показываем все прайсы
            self.update_price_list()
        else:
            filtered_items = [price for price in self.prices if text.lower() in price['name'].lower() or text.lower() in price['type'].lower()]
            self.update_price_list(filtered_items)  # Обновляем список GUI с отфильтрованными прайсами

    def detect_delimiter(file_path):
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            sniffer = csv.Sniffer()
            sample = csvfile.read(2048)
            dialect = sniffer.sniff(sample)
            return dialect.delimiter
        
    def create_alphabet_labels(self, n):
        """Generate a list of column names based on the alphabet for n columns."""
        labels = []
        length = 1
        while len(labels) < n:
            # Generate labels of the current length using itertools.product
            possible_combinations = [''.join(combination) for combination in itertools.product(string.ascii_uppercase, repeat=length)]
            labels.extend(possible_combinations)
            length += 1
        return labels[:n]    

    def load_column_mapping_ui(self, file_path, sheet_name=None):
        file_extension = file_path.split('.')[-1].lower()

        try:
            if file_extension in ['csv', 'txt']:
                delimiter, encoding = detect_csv_delimiter_and_encoding(file_path)
                df = pd.read_csv(file_path, nrows=50, delimiter=delimiter, encoding=encoding)
            elif file_extension in ['xls', 'xlsx']:
                if not sheet_name:
                    xls = pd.ExcelFile(file_path)
                    sheet_name = xls.sheet_names[0]
                df = pd.read_excel(file_path, nrows=50, sheet_name=sheet_name)
            elif file_extension == 'json':
                df = pd.read_json(file_path, lines=True, nrows=50)  # lines=True если JSON в формате line-delimited
            else:
                QMessageBox.critical(self, "Неподдерживаемый формат файла", "Поддерживаются только CSV, Excel и JSON файлы.")
                return
    
            # Step 1: Create a new row with the column names
            new_row = pd.DataFrame([df.columns.tolist()], columns=df.columns)

            # Step 2: Append this new row to the top of the DataFrame
            df = pd.concat([new_row, df], ignore_index=True)

            # Step 4: Rename the columns
            new_labels = self.create_alphabet_labels(len(df.columns))
            df.columns = new_labels

            # Очищаем предыдущие виджеты
            self.preview_table.setColumnCount(len(df.columns))
            self.preview_table.setRowCount(len(df.index))
            self.preview_table.setHorizontalHeaderLabels(df.columns)
            
            for i, row in df.iterrows():
                for j, value in enumerate(row):
                    self.preview_table.setItem(i, j, QTableWidgetItem(str(value)))

        except UnicodeDecodeError as e:
            QMessageBox.critical(self, "Ошибка кодировки", "Невозможно прочитать файл в автоопределенной кодировке.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки файла", f"Произошла ошибка при загрузке файла: {str(e)}")

    def load_file_with_autodetect_encoding(self, file_path):
        # Чтение первых байтов файла для определения кодировки
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Читаем первые 10КБ для анализа
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Чтение файла с установленной кодировкой
                df = pd.read_csv(file_path, encoding=encoding, nrows=50)
                return df
        except UnicodeDecodeError:
            QMessageBox.critical(self, "Ошибка кодировки", "Не удалось автоматически определить кодировку файла.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка чтения файла", str(e))

    # Пример использования
    def display_file_data(self):
        file_path = "path_to_your_file.csv"
        df = self.load_file_with_autodetect_encoding(file_path)
        if df is not None:
            print(df.head())

    def loadPricesFromDataFrame(self, df):
        # Очистить существующие данные
        self.table.setRowCount(0)
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns.tolist())

        # Заполнить таблицу данными
        for i, row in df.iterrows():
            self.table.insertRow(i)
            for j, value in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(value)))

        # Обновить список прайсов для внутреннего использования
        self.prices = df.to_dict('records')  # Сохраняем данные в виде списка словарей

    def priceDoubleClicked(self):
        price = get_price(self.last_selected_price_index)
        price_info = {
            'name': price[1],
            'type': price[3],
            'file_path': price[2]
        }

        edit_dialog = EditPriceDialog(price_info, self)
        if edit_dialog.exec_():
            # Обновляем список прайсов после возможных изменений
            self.update_price_list()

class AddListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить новый лист')
        self.master = parent
        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)

        self.label_layout = QHBoxLayout()
        self.layout.addLayout(self.label_layout)

        self.list_name_label = QLabel("Название листа: ")
        self.list_name_input = QLineEdit()

        self.label_layout.addWidget(self.list_name_label)
        self.label_layout.addWidget(self.list_name_input)

        self.addButton = QPushButton("Добавить")
        self.addButton.clicked.connect(self.addList)

        self.layout.addWidget(self.addButton)

    def addList(self):
        list_name = self.list_name_input.text()
        if not list_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, напишите имя листа.")
            return  # Возвращаемся без закрытия диалога

        self.master.append_list(list_name)

        self.accept()

class EditListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Изменить лист')
        self.master = parent
        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)

        list_name = get_list(self.master.last_selected_list_index, self.master.last_selected_price_index)

        self.label_layout = QHBoxLayout()
        self.layout.addLayout(self.label_layout)

        self.list_name_label = QLabel("Название листа: ")
        self.list_name_input = QLineEdit(list_name[2])

        self.label_layout.addWidget(self.list_name_label)
        self.label_layout.addWidget(self.list_name_input)

        self.changeButton = QPushButton("Изменить")
        self.changeButton.clicked.connect(self.updateList)

        self.layout.addWidget(self.changeButton)

    def updateList(self):
        list_name = self.list_name_input.text()
        if not list_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, напишите имя листа.")
            return  # Возвращаемся без закрытия диалога

        self.master.change_list(list_name)

        self.accept()

class AddPriceDialog(QDialog):
    def __init__(self, allow_reference=True, parent=None, add_price_callback=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить новый прайс')
        self.master = parent
        self.allow_reference = allow_reference
        self.add_price_callback = add_price_callback  # Убедитесь, что коллбэк корректно сохраняется
        self.selected_file_path = None  # Инициализация как None
        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.formLayout = QFormLayout()
        self.nameLineEdit = QLineEdit()
        self.formLayout.addRow("Название поставщика:", self.nameLineEdit)

        self.typeComboBox = QComboBox()
        print(select_data("SELECT * FROM prices WHERE price_type='Эталонный'"))
        price_types = DEFAULT_PRICES if not select_data("SELECT * FROM prices WHERE price_type='Эталонный'") else DEFAULT_PRICES[1:]
        self.typeComboBox.addItems(price_types)
        self.formLayout.addRow("Тип прайса:", self.typeComboBox)

        # Кнопка и поле для пути файла
        self.fileButton = QPushButton("Выбрать файл")
        self.fileButton.clicked.connect(self.selectFile)
        self.filePathLabel = QLabel("Файл не выбран")
        self.formLayout.addRow(self.fileButton, self.filePathLabel)

        self.layout.addLayout(self.formLayout)
        self.addButton = QPushButton("Добавить")
        self.addButton.clicked.connect(self.addPrice)
        self.layout.addWidget(self.addButton)

    def selectFile(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Выбрать файл прайс-листа", "", "All Files (*);;CSV Files (*.csv);;Excel Files (*.xls *.xlsx);;JSON Files (*.json)")
        if filepath:
            self.selected_file_path = "files"+filepath.split('files')[1]
            self.filePathLabel.setText(self.selected_file_path)

    def get_first_list_name_or_filename(self, file_path):
        """
        Get the first worksheet name from an Excel file or return the file name if it's a CSV file.

        Args:
        file_path (str): The path to the file.

        Returns:
        str: The name of the first worksheet or the file name.
        """
        # Get the file extension
        _, file_extension = os.path.splitext(file_path)

        # Check if the file is an Excel file
        if file_extension in ['.xls', '.xlsx']:
            # Open the file using pandas ExcelFile
            with pd.ExcelFile(file_path) as xls:
                # Return the first sheet name
                return xls.sheet_names[0]
        elif file_extension == '.csv':
            # Return the file name
            print(os.path.basename(file_path))
            return os.path.basename(file_path).rsplit('.', 1)[0]
        else:
            # Return a message for unsupported file types
            return "Unsupported file format"

    def addPrice(self):
        if not self.selected_file_path:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите файл прайс-листа.")
            return  # Возвращаемся без закрытия диалога

        price_info = {
            'name': self.nameLineEdit.text(),
            'type': self.typeComboBox.currentText(),
            'file_path': self.selected_file_path
        }

        self.master.append_price(price_info['name'], price_info['file_path'], price_info['type'])

        self.master.last_selected_price_index = len(fetch_prices())

        self.master.lists_list.clear()
        list_name = self.get_first_list_name_or_filename(price_info['file_path'])
        print(list_name)
        self.master.append_list(list_name)

        self.accept()

class EditPriceDialog(QDialog):
    def __init__(self, price_info, parent=None):
        super().__init__(parent)
        self.master = parent
        self.price_info = price_info  # Данные прайса для редактирования
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout(self)
        self.nameLineEdit = QLineEdit(self.price_info['name'])
        layout.addWidget(QLabel("Название:"))
        layout.addWidget(self.nameLineEdit)

        self.typeComboBox = QComboBox()
        price_types = ["Эталонный", "Поставщик", "Конкурент"]  # Пример типов прайсов
        self.typeComboBox.addItems(price_types)
        self.typeComboBox.setCurrentIndex(price_types.index(self.price_info['type']))
        layout.addWidget(QLabel("Тип прайса:"))
        layout.addWidget(self.typeComboBox)

        self.filePathLabel = QLabel(self.price_info['file_path'])
        self.fileButton = QPushButton("Изменить файл")
        self.fileButton.clicked.connect(self.selectFile)
        layout.addWidget(self.fileButton)
        layout.addWidget(self.filePathLabel)

        self.saveButton = QPushButton("Сохранить изменения")
        self.saveButton.clicked.connect(self.save_changes)
        layout.addWidget(self.saveButton)

    def selectFile(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Выбрать файл прайс-листа", "", "All Files (*);;CSV Files (*.csv);;Excel Files (*.xls *.xlsx);;JSON Files (*.json)")
        if filepath:
            self.filePathLabel.setText(filepath)

    def save_changes(self):
        updated_name = self.nameLineEdit.text()  # Обновляем на правильное имя виджета
        updated_type = self.typeComboBox.currentText()
        updated_file_path = self.filePathLabel.text()

        self.master.change_price(updated_name, updated_file_path, updated_type)
        
        QMessageBox.information(self, "Информация", "Изменения сохранены.")
        self.accept()