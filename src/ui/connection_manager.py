from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QListWidget,
                             QLineEdit, QToolBar, QAction, QSplitter, QWidget, QListWidgetItem, QMessageBox, QFileDialog, QLabel, QFormLayout, QComboBox, QTableWidgetItem,
                             QGroupBox, QSizePolicy, QTreeWidget, QTreeWidgetItem, QMenu, QDesktopWidget)
from PyQt5.QtGui import QIcon, QColor, QBrush
from PyQt5.QtCore import Qt, QSize
import sys


from config import *
from src.database.database import *

GREEN = QColor(0, 128, 0)
YELLOW = QColor(128, 128, 0)


class ConnectionManager(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('SmartPricingTool')
        self.prices = fetch_prices()
        self.master = parent  # Данные прайса для редактирования
        self.all_connections = get_all_connections()
        if not self.all_connections:
            self.all_connections = []
        self.all_connections = [i[0] for i in self.all_connections]
        self.connections = []
        self.setupUI()
        self.exec_()

    def setupUI(self):
        self.layout = QVBoxLayout(self)
        self.setGeometry(0, 0, 800, 500)
        self.center()  # Center the window

        # Data Panel
        self.data_panel_widget = QWidget(self)
        self.data_panel_layout = QVBoxLayout(self.data_panel_widget)

        self.toolbar = QToolBar("Price Tools", self)
        self.toolbar.setIconSize(QSize(30, 30))
        self.data_panel_layout.addWidget(self.toolbar)

        add_action = QAction(QIcon(CONNECT_ICON), 'Добавить связь', self)
        add_action.triggered.connect(self.add_connection)
        self.toolbar.addAction(add_action)

        delete_action = QAction(QIcon(DELETE_ICON), 'Удалить связь', self)
        delete_action.triggered.connect(self.delete_connection)
        self.toolbar.addAction(delete_action)

        self.data_panel_search = QLineEdit(self.master.last_selected_sku)
        self.data_panel_search.setPlaceholderText("Введите название или артикул...")
        self.data_panel_search.textChanged.connect(self.search_data)
        self.data_panel_layout.addWidget(self.data_panel_search)

        self.last_selected_connection_product_id = None
        self.last_selected_connection_product_index = None

        self.table = QTableWidget()
        self.table.setColumnCount(len(DEFAULT_COLUMNS_EN)+1)  # Setting number of columns
        self.table.setHorizontalHeaderLabels(['ID', 'Price Type']+DEFAULT_COLUMNS_EN)  # Setting column headers 
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemClicked.connect(self.on_select)
        self.data_panel_layout.addWidget(self.table)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.data_panel_widget)
        self.layout.addWidget(splitter)

        # Populate the table with example data
        self.search_data()

    def update_connections(self):
        all_connection = get_connections(self.master.last_selected_product_id)
        if all_connection:
            self.connections = [i[0] for i in all_connection]
        else:
            self.connections = []

    def on_select(self):
        self.last_selected_connection_product_index = self.table.currentRow()
        self.last_selected_connection_product_id = int(self.table.item(self.last_selected_connection_product_index, 0).text())
        print(self.last_selected_connection_product_index)
        print(self.last_selected_connection_product_id)
        self.update_connections()

    def center(self):
        qr = self.frameGeometry()  # Get a rectangle specifying the geometry of the dialog
        cp = QDesktopWidget().availableGeometry().center()  # Get the center point of the screen
        qr.moveCenter(cp)  # Move the rectangle's center to the screen's center
        self.move(qr.topLeft())

    def set_row_color(self, row, color):
        for column in range(self.table.columnCount()):
            self.table.item(row, column).setBackground(color)

    def reset_row_color(self, row):
        for column in range(self.table.columnCount()): 
            self.table.item(row, column).setBackground(QBrush())

    def add_connection(self): 
        if self.last_selected_connection_product_id in self.all_connections:
            response = QMessageBox.question(self, "Подтверждение", "Вы уверены, что заменить связь этого товара?", QMessageBox.Yes | QMessageBox.No)
            if response != QMessageBox.Yes:
                return
        self.set_row_color(self.last_selected_connection_product_index, GREEN)
        add_connection_db(self.master.last_selected_product_id, self.last_selected_connection_product_id)

        if self.last_selected_connection_product_id:
            self.update_connection()

    def update_connection(self):
        update_connection_db(self.master.last_selected_product_id, self.last_selected_connection_product_id)

    def delete_connection(self): 
        delete_connection_db(self.master.last_selected_product_id, self.last_selected_connection_product_id)
        self.reset_row_color(self.last_selected_connection_product_index)

    def search_data(self):
        self.data = get_all_data()
        free = []
        for inner_list in self.data:
            if self.prices[inner_list[1]-1][3] =="Поставщик":
                print(inner_list)
                print(self.prices[inner_list[1]-1][3], len(free))
            free.append([self.prices[inner_list[1]-1][3]]+[element if element is not None else '' for index, element in enumerate(inner_list) if index not in [1,2]])
        self.data = free
        
        from pprint import pprint
        #pprint(self.data)
        search_word = self.data_panel_search.text()

        searched_data = []

        self.table.clearContents()
        self.table.setRowCount(0)    

        for line in self.data:
            if line[2] or line[5]:
                if search_word.lower() in line[2].lower() or search_word=='':
                    searched_data.append(list(line))
                elif search_word.lower() in line[5].lower():
                    searched_data.append(list(line))

                    
        self.table.setRowCount(len(searched_data))  
        for index, line in enumerate(searched_data):
            line = [line[1]] + [line[0]] + line[2:]
            product_id = line[0]
            for col_index, value in enumerate(list(line)):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(index, col_index, item)
            if product_id in self.connections:
                self.set_row_color(index, GREEN)
            elif product_id in self.all_connections:
                self.set_row_color(index, YELLOW)

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
        self.update_connections()
        self.data = get_all_data()
        free = []
        for inner_list in self.data:
            free.append([self.prices[inner_list[1]-1][3]]+[element if element is not None else '' for index, element in enumerate(inner_list) if index not in [1,2]])
        self.data = free
        
        self.table.setRowCount(len(self.data))
        for row_index, item in enumerate(self.data):
            item = [item[1]] + [item[0]] + item[2:]
            product_id = item[0]
            for col_index, value in enumerate(list(item)):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_index, col_index, item)
            if product_id in self.connections:
                self.set_row_color(row_index, GREEN)
            elif product_id in self.all_connections:
                self.set_row_color(row_index, YELLOW)
