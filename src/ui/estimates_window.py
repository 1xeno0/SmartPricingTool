import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QTableWidget,
                             QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QFileDialog, QHeaderView, QAction, QToolBar, QComboBox, QDialog,
                             QFormLayout, QDialogButtonBox, QHBoxLayout, QSplitter, QMessageBox, QMenu, QLabel)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from random import randint  # For demonstration purposes
from config import *

from src.database.database import *


class EstimatesFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.mapping_layout = QVBoxLayout()
        self.layout.addLayout(self.mapping_layout)

        self.mapping_label = QLabel("Настройки наценок:")
        self.mapping_layout.addWidget(self.mapping_label)
        self.mapping_table = QTableWidget(0, 5)
        self.mapping_table.setHorizontalHeaderLabels(DEFAULT_ESTIMATES_COLUMNS)
        self.mapping_layout.addWidget(self.mapping_table)

        # Кнопка для добавления настроек маппинга
        add_mapping_button = QPushButton("Добавить настройку")
        add_mapping_button.clicked.connect(self.add_mapping_row)
        self.mapping_layout.addWidget(add_mapping_button)

        self.populate_mapping_tabel()

    def on_select(self):
        self.last_selected_connection_product_index = self.table.currentRow()
        self.last_selected_connection_product_id = int(self.table.item(self.last_selected_connection_product_index, 0).text())
        self.update_connections()

    def populate_mapping_tabel(self):
        self.mapping_table.clearContents()
        self.mapping_table.setRowCount(0)

        all_estimates = fetch_estimates()
        all_estimates = [[element if element is not None else '' for index, element in enumerate(inner_list)] for inner_list in all_estimates]

        self.mapping_table.setRowCount(len(all_estimates))
        for row_count, values in enumerate(all_estimates):
            for index, column_name in enumerate(DEFAULT_ESTIMATES_COLUMNS[:-1]):
                additional_data_edit = QLineEdit(str(values[index+1]))
                additional_data_edit.textChanged.connect(lambda text, row=row_count+1, column_name=column_name: self.on_field_changed(row, text, column_name))
                self.mapping_table.setCellWidget(row_count, index, additional_data_edit)

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda: self.delete_mapping_row(row_count+1))
            self.mapping_table.setCellWidget(row_count, len(DEFAULT_ESTIMATES_COLUMNS)-1, delete_button)

    def add_mapping_row(self):
        row_count = self.mapping_table.rowCount()

        add_estimates(None, None, None, None)
        
        self.populate_mapping_tabel()

    def delete_mapping_row(self, row):
        delete_estimates(row)
        self.mapping_table.removeRow(row-1)

    def on_field_changed(self, row, text, column_name):
        if not text:
            text = None
        else:
            text = float(text)
            
        update_estimates(row, DEFAULT_ESTIMATES_COLUMNS_EN[DEFAULT_ESTIMATES_COLUMNS.index(column_name)], text)
