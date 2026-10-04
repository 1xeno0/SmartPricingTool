import os
import requests
from bs4 import BeautifulSoup
import openpyxl
from urllib.parse import urlparse
import re
import aiohttp
import asyncio
from transliterate import translit

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QListWidget,
                             QLineEdit, QToolBar, QCheckBox, QTextEdit, QHeaderView, QFileDialog, QAction, QSplitter, QWidget, QListWidgetItem, QMessageBox, QFileDialog, QLabel, QFormLayout, QComboBox, QTableWidgetItem,
                             QGroupBox, QSizePolicy)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QEvent
from src.database.database import *
from config import *

from src.utils.parcer import *

from pprint import pprint


class ScraperFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.parser_name = ""
        self.last_selected_scraper_index = None

    def initUI(self):
        main_layout = QVBoxLayout(self)
        
        main_layout.setContentsMargins(3, 3, 3, 3)  # Уменьшение маргинов
        horizontal_splitter = QSplitter(Qt.Horizontal)
        horizontal_splitter.setHandleWidth(1)
        
        # Левая панель
        left_panel = QVBoxLayout()
        left_panel.setSpacing(3)
        self.toolbar = QToolBar("Scraper Tools", self)
        self.toolbar.setIconSize(QSize(20, 20))
        left_panel.addWidget(self.toolbar)

        add_action = QAction(QIcon(ADD_ICON), 'Добавить парсер', self)
        add_action.triggered.connect(self.addScraper)
        self.toolbar.addAction(add_action)

        delete_action = QAction(QIcon(DELETE_ICON), 'Удалить парсер', self)
        delete_action.triggered.connect(self.delete_scraper)
        self.toolbar.addAction(delete_action)

        self.sync_action = QAction(QIcon(SYNC_ICON), 'Запустить', self)
        #self.sync_action.triggered.connect(self.start_scraping)
        self.toolbar.addAction(self.sync_action)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Поиск по парсерам...")
        #self.search_field.textChanged.connect(self.filterScraper)
        left_panel.addWidget(self.search_field)

        self.scraper_list = QListWidget()
        self.scraper_list.itemClicked.connect(self.scraper_list_on_select)
        self.scraper_list.itemDoubleClicked.connect(self.chanageScraper)
        self.scraper_list.itemChanged.connect(self.update_activity)
        left_panel.addWidget(self.scraper_list)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        horizontal_splitter.addWidget(left_container)

        # Правая панель
        right_panel = QVBoxLayout()
        right_panel.setSpacing(5)

        url_group = QGroupBox("URL Settings")
        url_layout = QVBoxLayout()
        
        # URL input section
        url_group = QGroupBox("Enter URLs (one per line):", self)
        url_layout.addWidget(url_group)
        url_layout = QVBoxLayout(url_group)
        self.url_text = QTextEdit(url_group)
        self.url_text.textChanged.connect(self.on_change_links)
        url_layout.addWidget(self.url_text)
        
        right_panel.addWidget(url_group)
        
        # Таблица полей парсера
        table_group = QGroupBox("Data Fields")
        table_layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Field", "Left Bound", "Right Bound", "Only Numbers", "Default Value"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.table_on_select)
        table_layout.addWidget(self.table)
        table_group.setLayout(table_layout)
        right_panel.addWidget(table_group)

        controls_layout = QHBoxLayout()
        self.add_row_button = QPushButton('Добавить поле')
        self.add_row_button.clicked.connect(self.add_field)
        controls_layout.addWidget(self.add_row_button)

        self.remove_row_button = QPushButton('Удалить поле')
        self.remove_row_button.clicked.connect(self.delete_field)
        controls_layout.addWidget(self.remove_row_button)

        self.start_button = QPushButton('Начать скрапинг')
        self.start_button.clicked.connect(self.start_scraping)
        controls_layout.addWidget(self.start_button)
        right_panel.addLayout(controls_layout)

        # Контейнер для правой панели и добавление в сплиттер
        right_container = QWidget()
        right_container.setLayout(right_panel)
        horizontal_splitter.addWidget(right_container)

        # Добавление сплиттера в главный лейаут
        main_layout.addWidget(horizontal_splitter)
        self.setLayout(main_layout)
        
        self.populate_scraper_list()
        
    def start_scraping(self):
        if not self.last_selected_scraper_index:
            QMessageBox.warning(self, "Ошибка", "Вы не выбрали парсер!")
            return
        
        fields = fetch_scraper_settings(self.last_selected_scraper_index)
        links = get_scraper_links(self.last_selected_scraper_index)
        
        print(get_scraper(self.last_selected_scraper_index))
        name, directory = get_scraper(self.last_selected_scraper_index)[1:3]
        
        print(links)
        scrape_and_save(links[1].split('\n'), directory, name, fields)
        
        QMessageBox.information(self, "Успех", "Сайты были спаршены!")
        
    def update_activity(self, item):
        index = self.price_list.row(item)
        # Check the state of the item
        if item.checkState() == Qt.Checked:
            update_scraper_activity(index+1, True)
        else:
            update_scraper_activity(index+1, False)
        
    def populate_scraper_list(self):
        all_scrapers = fetch_scrapers()
        
        for scraper in all_scrapers:
            item = QListWidgetItem(scraper[1])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkbox
            if scraper[-1]:
                item.setCheckState(Qt.Checked)  # Set initial state
            else:
                item.setCheckState(Qt.Unchecked)  # Set initial state
            self.scraper_list.addItem(item)
        
    def scraper_list_on_select(self):
        selected_item = self.scraper_list.currentItem()
        self.last_selected_scraper_index = self.scraper_list.row(selected_item) + 1
        
        self.populate_fields()
        links = get_scraper_links(self.last_selected_scraper_index)[1]
        self.url_text.setPlainText(links)
        
    def delete_scraper(self):
        self.scraper_list.takeItem(self.last_selected_scraper_index-1)
        delete_scraper(self.last_selected_scraper_index)
        self.table.clearContents()
        self.table.setRowCount(0)
        self.url_text.clear()
        
    def addScraper(self):
        AddScraperDialog(self).exec_()
    
    def chanageScraper(self):
        EditScraperDialog(self).exec_()

    def populate_fields(self):
        all_fields = fetch_scraper_settings(self.last_selected_scraper_index)
        all_fields = [[element if element is not None else '' for element in inner_list] for inner_list in all_fields]
        
        self.table.clearContents()
        self.table.setRowCount(0)

        for field in all_fields:
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            first_edit = QComboBox()
            first_edit.addItems(DEFAULT_COLUMNS_EN)  # Example database fields
            first_edit.setCurrentIndex(DEFAULT_COLUMNS_EN.index(field[1]))
            second_edit = QLineEdit(field[2])
            third_edit = QLineEdit(field[3])

            # Connect textChanged signals for QLineEdit
            first_edit.currentIndexChanged.connect(lambda index, row=row_count: self.combobox_changed(row, index))
            second_edit.textChanged.connect(lambda text, row=row_count: self.field_on_change(row, text, "left_bound"))
            second_edit.installEventFilter(self)
            third_edit.textChanged.connect(lambda text, row=row_count: self.field_on_change(row, text, "right_bound"))
            third_edit.installEventFilter(self)

            # Create QCheckBox
            checkbox = QCheckBox("Only Numbers")
            print(field)
            checkbox.setChecked(field[4])
            checkbox.stateChanged.connect(lambda state, row=row_count: self.numbers_on_change(row, state))

            # Create another QLineEdit
            fourth_edit = QLineEdit(field[5])
            fourth_edit.textChanged.connect(lambda text, row=row_count: self.field_on_change(row, text, "default_value"))
            fourth_edit.installEventFilter(self)

            # Add all widgets to the table
            self.table.setCellWidget(row_count, 0, first_edit)
            self.table.setCellWidget(row_count, 1, second_edit)
            self.table.setCellWidget(row_count, 2, third_edit)
            self.table.setCellWidget(row_count, 3, checkbox)
            self.table.setCellWidget(row_count, 4, fourth_edit)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            row = self.find_row(obj)
            self.last_selected_scraper_settings_index = row+1
            print(self.last_selected_scraper_settings_index)
            return True
        return super(ScraperFrame, self).eventFilter(obj, event)
    
    def find_row(self, widget):
        for i in range(self.table.rowCount()):
            for j in range(self.table.columnCount()):
                if self.table.cellWidget(i, j) == widget:
                    return i
        return -1
            
    def table_on_select(self, row, column):
        self.last_selected_scraper_settings_index = row+1
        print(self.last_selected_scraper_settings_index)
        
    def on_change_links(self):
        links = self.url_text.toPlainText()
        pprint(links)
        update_scraper_links(self.last_selected_scraper_index, links)
        #update_scraper_settings_column(self.last_selected_scraper_settings_index, self.last_selected_scraper_index, "links", self.url_text.toPlainText())
    
    def numbers_on_change(self, row, state):
        print(row+1, state)
        if state == Qt.Checked:
            update_scraper_settings_column(row+1, self.last_selected_scraper_index, "only_numbers", True)
        else:
            update_scraper_settings_column(row+1, self.last_selected_scraper_index, "only_numbers", False)
    
    def field_on_change(self, row, text, column_name):
        print(row+1, text, column_name)
        update_scraper_settings_column(row+1, self.last_selected_scraper_index, column_name, text)

    def combobox_changed(self, row, index):
        # Example: print or handle change
        print(row+1, self.last_selected_scraper_index, 'field', DEFAULT_COLUMNS_EN[index])
        update_scraper_settings_column(row+1, self.last_selected_scraper_index, 'field', DEFAULT_COLUMNS_EN[index])
        
    def add_field(self):
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)
        first_edit = QComboBox()
        second_edit = QLineEdit()
        third_edit = QLineEdit()

        # Connect textChanged signals for QLineEdit
        first_edit.addItems(DEFAULT_COLUMNS_EN)  # Example database fields
        first_edit.currentIndexChanged.connect(lambda index, row=row_count: self.combobox_changed(row, index))
        second_edit.textChanged.connect(lambda text, row=row_count: self.field_on_change(row, text, "left_bound"))
        second_edit.installEventFilter(self)
        third_edit.textChanged.connect(lambda text, row=row_count: self.field_on_change(row, text, "right_bound"))
        third_edit.installEventFilter(self)

        # Create QCheckBox
        checkbox = QCheckBox("Only Numbers")
        checkbox.setChecked(False)
        checkbox.stateChanged.connect(lambda state, row=row_count: self.numbers_on_change(row, state))

        # Create another QLineEdit
        fourth_edit = QLineEdit()
        fourth_edit.textChanged.connect(lambda text, row=row_count: self.field_on_change(row, text, "default_value"))
        
        add_scraper_settings(self.last_selected_scraper_index, None, None, None, False, None, None)

        # Add all widgets to the table
        self.table.setCellWidget(row_count, 0, first_edit)
        self.table.setCellWidget(row_count, 1, second_edit)
        self.table.setCellWidget(row_count, 2, third_edit)
        self.table.setCellWidget(row_count, 3, checkbox)
        self.table.setCellWidget(row_count, 4, fourth_edit)
    
    def delete_field(self):
        if not self.last_selected_scraper_index:
            QMessageBox.warning(self, "Ошибка", "Вы не выбрали парсер!")
            return
        
        print(self.last_selected_scraper_settings_index, self.last_selected_scraper_index)
        delete_scraper_settings(self.last_selected_scraper_settings_index, self.last_selected_scraper_index)
        self.table.removeRow(self.last_selected_scraper_settings_index-1)
        
class AddScraperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Добавить новый парсер')
        self.master = parent
        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.formLayout = QFormLayout()
        self.nameLineEdit = QLineEdit()
        self.formLayout.addRow("Название парсера:", self.nameLineEdit)
        
        self.openDialogButton = QPushButton("Выборери папку", self)
        self.openDialogButton.clicked.connect(self.open_save_folder_dialog)
        self.layout.addLayout(self.formLayout)
        self.layout.addWidget(self.openDialogButton)
        
        self.path_label = QLabel()
        self.layout.addWidget(self.path_label)

        self.addButton = QPushButton("Добавить", self)
        self.addButton.clicked.connect(self.accept)
        self.layout.addWidget(self.addButton)

    def open_save_folder_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения",)
        if directory:
            self.path_label.setText(directory)  # Сохраняем выбранную директорию

    def accept(self):
        name = self.nameLineEdit.text()
        directory = self.path_label.text()
        if not name or not directory:
            QMessageBox.warning(self, "Ошибка", "Необходимо указать название и выбрать директорию.")
            return

        item = QListWidgetItem(name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # Enable checkbox
        item.setCheckState(Qt.Checked)  # Set initial state
        self.master.scraper_list.addItem(item)
        self.master.last_selected_scraper_index = self.master.scraper_list.count()
        print(self.master.last_selected_scraper_index)
        add_scraper(name, directory, True)
        super().accept()
        
class EditScraperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Изменить парсер')
        self.master = parent
        self.scraper = get_scraper(self.master.last_selected_scraper_index)
        self.setupUI()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.formLayout = QFormLayout()
        self.nameLineEdit = QLineEdit(self.scraper[1])
        self.formLayout.addRow("Название парсера:", self.nameLineEdit)
        
        self.openDialogButton = QPushButton("Выборери папку", self)
        self.openDialogButton.clicked.connect(self.open_save_folder_dialog)
        self.layout.addLayout(self.formLayout)
        self.layout.addWidget(self.openDialogButton)
        
        self.path_label = QLabel(self.scraper[2])
        self.layout.addWidget(self.path_label)

        self.addButton = QPushButton("Добавить", self)
        self.addButton.clicked.connect(self.accept)
        self.layout.addWidget(self.addButton)

    def open_save_folder_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if directory:
            self.path_label.setText(directory)  # Сохраняем выбранную директорию

    def accept(self):
        name = self.nameLineEdit.text()
        directory = self.path_label.text()
        if not name or not directory:
            QMessageBox.warning(self, "Ошибка", "Необходимо указать название и выбрать директорию.")
            return
        
        item = self.master.scraper_list.item(self.master.last_selected_scraper_index-1)
        item.setText(name)
        update_scraper(self.master.last_selected_scraper_index, name, directory)
        super().accept()