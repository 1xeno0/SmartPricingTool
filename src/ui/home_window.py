import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableWidget,
                             QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QFileDialog, QHeaderView, QAction, QToolBar, QComboBox, QDialog,
                             QFormLayout, QDialogButtonBox, QHBoxLayout, QSplitter, QMessageBox, QMenu)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from random import randint  # For demonstration purposes
from config import *

from src.database.database import *
from src.ui.connection_manager import ConnectionManager
from src.utils import price_sync
from src.utils import estimates_sync


class HomeFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = []
        self.last_selected_product_id = None
        self.reference_data = []
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        # Category Panel
        self.category_widget = QWidget()
        self.category_widget.setMaximumWidth(300)
        self.category_layout = QVBoxLayout(self.category_widget)

        self.category_search = QLineEdit()
        self.category_search.setPlaceholderText("Введите название категории...")
        self.category_layout.addWidget(self.category_search)

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Categories")
        self.category_layout.addWidget(self.category_tree)
        self.populateCategories()

        # Splitter for layout management

        # Data Panel
        self.data_panel_widget = QWidget()
        self.data_panel_layout = QVBoxLayout(self.data_panel_widget)

        self.data_panel_search = QLineEdit()
        self.data_panel_search.setPlaceholderText("Введите название или артикул...")
        self.data_panel_search.textChanged.connect(self.search_data)
        self.data_panel_layout.addWidget(self.data_panel_search)

        self.table = QTableWidget()
        self.table.setColumnCount(len(DEFAULT_COLUMNS_EN)+3)  # Setting number of columns
        self.table.setHorizontalHeaderLabels(['Connection', 'Competitor', 'ID']+DEFAULT_COLUMNS_EN)  # Setting column headers
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showContextMenu)
        self.data_panel_layout.addWidget(self.table)

        self.refresh_table_button = QPushButton('Обновить')
        self.refresh_table_button.clicked.connect(self.refresh_data_panel)
        self.data_panel_layout.addWidget(self.refresh_table_button)

        self.refresh_table_button = QPushButton('Загрузить цены')
        self.refresh_table_button.clicked.connect(self.sync_table)
        self.data_panel_layout.addWidget(self.refresh_table_button)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.category_widget)
        splitter.addWidget(self.data_panel_widget)
        self.layout.addWidget(splitter)

        # Populate the table with example data
        self.populate_data_panel()
        
    def refresh_data_panel(self):
        price_sync.sync_prices()
        
        self.populate_data_panel()
        QMessageBox.information(self, "Успех", "Прайсы были обновлены!")
        
    def sync_table(self):
        estimates_sync.sync_prices()
        
        QMessageBox.information(self, "Успех", "Прайс был обновлен!")
        self.populate_data_panel()

    def showContextMenu(self, pos):
        # Get the global position of the right-click
        globalPos = self.table.mapToGlobal(pos)

        # Get the row index of the clicked cell
        row = self.table.indexAt(pos).row() 
            
        self.last_selected_product_id = int(self.table.item(row, 2).text())  # Index 2 corresponds to the 3rd column 
        self.last_selected_sku= self.table.item(row, 6).text()  # Index 2 corresponds to the 3rd column 

        # Create a context menu
        menu = QMenu(self)

        action = QAction(f"Просмотреть связи продукта с айди: {self.last_selected_product_id}", self)
        action.triggered.connect(self.open_product_connections)  # Connect the action to a function
        menu.addAction(action)

        # Execute the context menu at the global position
        menu.exec_(globalPos)

    def open_product_connections(self):
        ConnectionManager(self)

    def search_data(self):
        search_word = self.data_panel_search.text()
        print(search_word)

        searched_data = []
        compared_products = fetch_compared_products()
        all_ids = [i[1] for i in compared_products]

        self.table.clearContents()
        self.table.setRowCount(0)    

        for line in self.data:
            l = ['-', '?']
            if line[0] in self.connected:
                l[0] = '+'
            if line[0] in all_ids:
                product = compared_products[all_ids.index(line[0])]
                l[1] = product[-1]
                line[3] = product[2]
            if line[1]:
                if search_word.lower() in line[1].lower() or search_word=='':
                    searched_data.append(l+list(line))
            elif line[1] and search_word.lower() in line[4].lower():
                searched_data.append(l+list(line))
                    
        self.table.setRowCount(len(searched_data))  
        for index, line in enumerate(searched_data):
            for col_index, value in enumerate(list(line)):
                self.table.setItem(index, col_index, QTableWidgetItem(str(value)))

    def populateCategories(self):
        electronics = QTreeWidgetItem(["Electronics"])
        electronics.addChild(QTreeWidgetItem(["Laptops"]))
        electronics.addChild(QTreeWidgetItem(["Smartphones"]))
        self.category_tree.addTopLevelItem(electronics)

        appliances = QTreeWidgetItem(["Home Appliances"])
        appliances.addChild(QTreeWidgetItem(["Refrigerators"]))
        appliances.addChild(QTreeWidgetItem(["Washing Machines"]))
        self.category_tree.addTopLevelItem(appliances)

    def populate_data_panel(self):
        
        self.table.clearContents()
        self.table.setRowCount(0)

        self.data = get_all_my_data()
        self.data = [[element if element is not None else '' for element in inner_list] for inner_list in self.data]
        self.connected = get_full_connections()
        if not self.connected:
            self.connected=[]

        self.connected = [i[0] for i in self.connected]
        compared_products = fetch_compared_products()
        all_ids = [i[1] for i in compared_products]

        self.table.setRowCount(len(self.data))
        for row_index, item in enumerate(self.data):
            l = ['-', '?']
            if item[0] in self.connected:
                l[0] = '+'
            if item[0] in all_ids:
                product = compared_products[all_ids.index(item[0])]
                l[1] = product[-1]
                item[3] = product[2]
            for col_index, value in enumerate(l+list(item)):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
