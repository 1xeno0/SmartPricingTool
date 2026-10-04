import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QSplitter, QToolBar, QAction, 
                             QListWidget, QTableWidget, QTableWidgetItem, QListWidgetItem, 
                             QTextEdit, QLineEdit, QLabel, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from src.database.database import *

class ExportFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Левая панель
        left_panel = QVBoxLayout()

        # Тулбар для управления экспортами
        toolbar = QToolBar("Управление экспортом", self)

        add_action = QAction(QIcon(ADD_ICON), 'Добавить', self)
        toolbar.addAction(add_action)

        delete_action = QAction(QIcon(DELETE_ICON), 'Удалить', self)
        toolbar.addAction(delete_action)

        edit_action = QAction(QIcon(EDIT_ICON), 'Редактировать', self)
        toolbar.addAction(edit_action)

        left_panel.addWidget(toolbar)

        self.export_list = QListWidget()
        left_panel.addWidget(self.export_list)

        left_container = QWidget()
        left_container.setLayout(left_panel)
        splitter.addWidget(left_container)

        # Правая панель
        right_panel = QVBoxLayout()
        self.field_table = QTableWidget(5, 2)  # Примерная инициализация с 5 строками
        self.field_table.setHorizontalHeaderLabels(["Поле", "Наименование для экспорта"])
        
        self.filter_label = QLabel("Фильтры:")
        self.filter_text = QTextEdit()
        
        right_panel.addWidget(self.field_table)
        right_panel.addWidget(self.filter_label)
        right_panel.addWidget(self.filter_text)

        right_container = QWidget()
        right_container.setLayout(right_panel)
        splitter.addWidget(right_container)

        self.setLayout(main_layout)

        # Связывание сигналов и слотов
        add_action.triggered.connect(self.prompt_add_export)
        delete_action.triggered.connect(self.delete_export)
        edit_action.triggered.connect(self.prompt_edit_export)
        self.export_list.itemClicked.connect(self.load_export_details)
        self.populate_exports_list()

    def prompt_add_export(self):
        name, ok = QInputDialog.getText(self, 'Новый экспорт', 'Введите имя экспорта:')
        if ok and name:
            fields = "поле1, поле2"
            filters = "цена > 100"
            add_export(name, fields, filters)
            self.populate_exports_list()

    def delete_export(self):
        selected_item = self.export_list.currentItem()
        if selected_item:
            export_id = selected_item.data(Qt.UserRole)
            delete_export(export_id)
            self.populate_exports_list()

    def load_export_details(self, item):
        export_id = item.data(Qt.UserRole)
        export_data = fetch_export_by_id(export_id)
        if export_data:
            self.field_table.clearContents()
            for row, field in enumerate(zip(["Поле", "Наименование"], export_data[2].split(", "))):
                self.field_table.setItem(row, 0, QTableWidgetItem(field[0]))
                self.field_table.setItem(row, 1, QTableWidgetItem(field[1]))
            self.filter_text.setText(export_data[3])

    def prompt_edit_export(self):
        selected_item = self.export_list.currentItem()
        if selected_item:
            export_id = selected_item.data(Qt.UserRole)
            old_name = selected_item.text()
            new_name, ok = QInputDialog.getText(self, 'Редактировать экспорт', 'Измените имя экспорта:', QLineEdit.Normal, old_name)
            if ok and new_name and new_name != old_name:
                print(f"Updating export ID {export_id} to new name {new_name}")  # Добавьте эту строку для отладки
                update_export_name(export_id, new_name)
                self.populate_exports_list()

    def populate_exports_list(self):
        exports = fetch_exports()
        self.export_list.clear()
        for export in exports:
            item = QListWidgetItem(f"{export[1]}")
            item.setData(Qt.UserRole, export[0])
            self.export_list.addItem(item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ExportFrame()
    ex.show()
    sys.exit(app.exec_())
