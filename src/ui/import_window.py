import sys
import schedule
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, QTextEdit, QPushButton, QMenu, QTableWidgetItem,
                             QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox, QCheckBox,
                             QTableWidget, QTabWidget, QDialog, QLabel)
from PyQt5.QtWidgets import QToolButton, QMenu
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent
from src.database.database import *

class ImportFrame(QWidget):
    def __init__(self):
        super().__init__()
        self.task_table = TaskTable(self)
        self.initUI()
        self.left_layout.addWidget(self.task_table)
        self.task_table.cellClicked.connect(self.on_task_selected)
        
        self.last_selected_task_index = None

    def initUI(self):
        # Основной навигационный тулбар

        # Основной виджет и layout
        main_layout = QHBoxLayout(self)

        # Создание и настройка Splitter
        self.splitter = QSplitter(self)
        main_layout.addWidget(self.splitter)

        # Левая панель
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.task_toolbar = QToolBar('Task Toolbar', self.left_panel)

        tool_button = QToolButton(self)
        tool_button.setIcon(QIcon('src/img/add_icon.png'))
        tool_button.setText('Добавить')
        tool_button.setPopupMode(QToolButton.InstantPopup)
        add_task_menu = QMenu()
        add_email_action = QAction('E-mail', self)
        add_ftp_action = QAction('FTP/SFTP', self)
        add_google_docs_action = QAction('Google Doc', self)
        add_task_menu.addAction(add_email_action)
        add_task_menu.addAction(add_ftp_action)
        add_task_menu.addAction(add_google_docs_action)
        tool_button.setMenu(add_task_menu)
        self.task_toolbar.addWidget(tool_button)

        add_email_action.triggered.connect(self.open_add_email_task_dialog)
        add_ftp_action.triggered.connect(self.open_add_ftp_task_dialog)
        add_google_docs_action.triggered.connect(self.open_add_google_docs_task_dialog)

        copy_action = QAction(QIcon('src/img/copy_icon.png'), 'Копировать', self)
        self.task_toolbar.addAction(copy_action)
        delete_action = QAction(QIcon('src/img/delete_icon.png'), 'Удалить', self)
        delete_action.triggered.connect(self.task_table.delete_task)
        self.task_toolbar.addAction(delete_action)
        self.task_toolbar.addAction(QAction(QIcon('src/img/start_icon.png'), 'Запустить', self))
        self.task_toolbar.addAction(QAction(QIcon('src/img/stop_icon.png'), 'Прервать', self))

        add_task_button = QPushButton("Добавить задание", self)
        add_task_button.clicked.connect(self.open_add_task_dialog)
        self.task_toolbar.addWidget(add_task_button)

        self.left_layout.addWidget(self.task_toolbar)
        # Предположим, здесь будет таблица или другой виджет для заданий
        self.splitter.addWidget(self.left_panel)

        # Правая панель с вкладками
        self.right_panel = QTabWidget()
        self.email_tab = EmailSettingsTab()
        self.ftp_tab = FTPSettingsTab()
        self.google_docs_tab = GoogleDocsSettingsTab()
        self.log_tab = LogTab()
        self.right_panel.addTab(self.email_tab, "E-mail")
        self.right_panel.addTab(self.ftp_tab, "FTP/SFTP")
        self.right_panel.addTab(self.google_docs_tab, "Google Docs")
        self.right_panel.addTab(self.log_tab, "Лог")
        self.splitter.addWidget(self.right_panel)

        self.splitter.setSizes([300, 700])

        self.setGeometry(300, 300, 900, 600)
        self.setWindowTitle('Автоматизация')

    def connect_actions(self):
        self.add_email_action.triggered.connect(self.open_add_email_task_dialog)
        self.add_ftp_action.triggered.connect(self.open_add_ftp_task_dialog)
        self.add_google_docs_action.triggered.connect(self.open_add_google_docs_task_dialog)
    
    def open_add_email_task_dialog(self):
        self.open_add_task_dialog('email')

    def open_add_ftp_task_dialog(self):
        self.open_add_task_dialog('FTP/SFTP')

    def open_add_google_docs_task_dialog(self):
        self.open_add_task_dialog('Google Doc')

    def on_task_selected(self, selected_row):
        task_type = self.task_table.item(selected_row, 3).text()
        self.show_tab(task_type.lower())

    def show_tab(self, tab_type):
        # Логика переключения вкладок
        index = {'email': 0, 'ftp': 1, 'google_docs': 2}.get(tab_type, 0)
        self.right_panel.setCurrentIndex(index)

    def open_add_task_dialog(self, task_type):
        print(f"Открываем диалог для добавления задачи типа: {task_type}")
        dialog = AddTaskDialog(task_type, self)  # Убедитесь, что AddTaskDialog принимает параметр task_type
        dialog.exec_()

# Вспомогательные классы EmailSettingsTab, FTPSettingsTab, GoogleDocsSettingsTab, LogTab должны быть определены
class EmailSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Расписание запуска
        self.schedule_settings = ScheduleSettings()
        layout.addWidget(self.schedule_settings)

        # Табы для настроек E-mail
        self.tab_widget = QTabWidget()
        self.main_tab = QWidget()
        self.main_layout = QVBoxLayout(self.main_tab)
        self.email_table = QTableWidget()
        self.main_layout.addWidget(self.email_table)
        self.tab_widget.addTab(self.main_tab, "Основные")

        self.settings_tab = QWidget()
        self.settings_layout = QFormLayout(self.settings_tab)
        self.server_input = QLineEdit(self)
        self.settings_layout.addRow("Сервер:", self.server_input)
        self.port_input = QLineEdit(self)
        self.settings_layout.addRow("Порт:", self.port_input)
        self.login_input = QLineEdit(self)
        self.settings_layout.addRow("Логин:", self.login_input)
        self.password_input = QLineEdit(self)
        self.settings_layout.addRow("Пароль:", self.password_input)
        self.connection_type = QComboBox(self)
        self.connection_type.addItems(['SMTP', 'IMAP'])
        self.settings_layout.addRow("Тип подключения:", self.connection_type)
        self.encryption_type = QComboBox(self)
        self.encryption_type.addItems(['SSL', 'TLS'])
        self.settings_layout.addRow("Шифрование:", self.encryption_type)

        self.tab_widget.addTab(self.settings_tab, "Настройки почтового ящика")
        
        layout.addWidget(self.tab_widget)

class FTPSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Расписание запуска
        self.schedule_settings = ScheduleSettings()
        layout.addWidget(self.schedule_settings)

        # Настройки FTP/SFTP
        settings_layout = QFormLayout()
        protocol_combo = QComboBox()
        protocol_combo.addItems(["FTP", "SFTP"])
        settings_layout.addRow("Протокол:", protocol_combo)
        server_input = QLineEdit(self)
        settings_layout.addRow("Сервер:", server_input)
        login_input = QLineEdit(self)
        settings_layout.addRow("Логин:", login_input)
        password_input = QLineEdit(self)
        settings_layout.addRow("Пароль:", password_input)
        port_input = QLineEdit(self)
        settings_layout.addRow("Порт:", port_input)
        operation_combo = QComboBox()
        operation_combo.addItems(["Отправить", "Получить"])
        settings_layout.addRow("Операция:", operation_combo)
        file_path_input = QLineEdit(self)
        settings_layout.addRow("Файл/Папка:", file_path_input)
        server_path_input = QLineEdit(self)
        settings_layout.addRow("Папка на сервере:", server_path_input)
        
        layout.addLayout(settings_layout)

class GoogleDocsSettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        # Расписание запуска
        self.schedule_settings = ScheduleSettings()
        layout.addWidget(self.schedule_settings)

        # Тулбар для таблицы
        self.toolbar = QToolBar("Документы Toolbar", self)
        self.toolbar.addAction(QAction('Добавить', self))
        self.toolbar.addAction(QAction('Удалить', self))
        self.toolbar.addAction(QAction('Сохранить', self))
        layout.addWidget(self.toolbar)

        # Таблица для документов Google Docs
        self.docs_table = QTableWidget()
        self.docs_table.setColumnCount(3)
        self.docs_table.setHorizontalHeaderLabels(['Активность', 'URL', 'Название'])
        layout.addWidget(self.docs_table)

class LogTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.log_text_edit = QTextEdit(self)
        self.log_text_edit.setReadOnly(True)
        layout.addWidget(self.log_text_edit)

        self.clear_log_button = QPushButton("Очистить Лог", self)
        self.clear_log_button.clicked.connect(self.log_text_edit.clear)
        layout.addWidget(self.clear_log_button)


class TaskTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.master = parent
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['ID', 'Активность', 'Название задания', 'Тип', 'Последний запуск', 'Статус'])
        self.setColumnWidth(1, 10)  # Ширина колонки для чекбокса
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.itemClicked.connect(self.on_select)
        self.initUI()
        
    def checkbox_changed(self, row, state):
        update_task_activity(row, True if state else False)

    def initUI(self):
        data = fetch_tasks()
        self.clearContents()
        self.setRowCount(len(data))
        for row_count, values in enumerate(data): 
            for index, i in enumerate(values):
                if index==1:
                    item = QCheckBox()
                    item.setChecked(True if i else False)
                    item.stateChanged.connect(lambda state, row=row_count: self.checkbox_changed(row, state))
                else:
                    item = QLineEdit(str(i))
                    item.installEventFilter(self)
                print(row_count, index)
                self.setCellWidget(row_count, index, item)
            
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            row = self.find_row(obj)
            self.master.last_selected_task_index = row+1
            print(self.master.last_selected_task_index)
            return True
        return super(TaskTable, self).eventFilter(obj, event)
    
    def find_row(self, widget):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                if self.cellWidget(i, j) == widget:
                    return i
        return -1
            

    def update_task_status(self, row, state):
        if state == Qt.Checked:
            self.setItem(row, 5, QTableWidgetItem("Активно"))
        else:
            self.setItem(row, 5, QTableWidgetItem("Неактивно"))
        
    def on_select(self):
        self.master.last_selected_task_index = self.currentRow()+1
        
    def delete_task(self):
        delete_task(self.master.last_selected_task_index)
        self.removeRow(self.master.last_selected_task_index-1)

class AddTaskDialog(QDialog):
    def __init__(self, task_type, parent=None):
        super().__init__(parent)
        self.master = parent
        self.task_type = task_type
        self.setWindowTitle(f"Добавить новое задание: {self.task_type}")
        self.setFixedSize(300, 200)
        self.initUI()

    def initUI(self):
        self.layout = QFormLayout(self)
        self.name_input = QLineEdit(self)  # Убедитесь, что здесь имя переменной 'name_input'
        self.layout.addRow("Название задачи:", self.name_input)
        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.addTask)
        self.layout.addWidget(self.add_button)
        
    def addTask(self):
        row_count = self.master.task_table.rowCount()
        self.master.task_table.setRowCount(row_count+1)
        values = [row_count+1, True, self.name_input.text(), self.task_type, '', '']
        
        add_task(self.task_type, self.name_input.text())
        
        for index, i in enumerate(values):
            if index==1:
                item = QCheckBox()
                item.setChecked(True if i else False)
                item.stateChanged.connect(lambda state, row=row_count: self.master.checkbox_changed(row, state))
            else:
                item = QLineEdit(str(i))
            
            print(row_count, index)
            self.master.task_table.setCellWidget(row_count, index, item)
            
        self.accept()

#Автозапуск заданий
class ScheduleSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Выбор режима запуска
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Точное время", "Периодичность", "Ручной"])
        self.mode_combo.currentIndexChanged.connect(self.update_mode_settings)
        
        # Контейнеры для настроек каждого режима
        self.time_input = QLineEdit(self)
        self.interval_input = QLineEdit(self)
        self.manual_label = QLabel("Запуск задачи осуществляется вручную через интерфейс.")

        # Добавление виджетов в layout
        self.layout.addWidget(QLabel("Выберите режим запуска:"))
        self.layout.addWidget(self.mode_combo)
        self.layout.addWidget(QLabel("Укажите время или интервал:"))
        self.layout.addWidget(self.time_input)
        self.layout.addWidget(self.interval_input)
        self.layout.addWidget(self.manual_label)

        self.update_mode_settings(self.mode_combo.currentIndex())

    def update_mode_settings(self, index):
        # Скрываем все поля
        self.time_input.hide()
        self.interval_input.hide()
        self.manual_label.hide()

        # Показываем нужные поля в зависимости от выбранного режима
        if index == 0:  # Точное время
            self.time_input.show()
        elif index == 1:  # Периодичность
            self.interval_input.show()
        elif index == 2:  # Ручной
            self.manual_label.show()

    def refresh_task_table(self):
        tasks = self.database_manager.fetch_all_tasks()  # Предположим, что такой метод существует
        self.task_table.setRowCount(0)  # Очищаем таблицу перед добавлением новых данных
        for task in tasks:
            self.add_task_to_table(task)  # Метод для добавления задачи в таблицу

    def run_task(task_name):
        print(f"Запуск задачи {task_name}")

    def schedule_tasks():
        tasks = database_manager.fetch_all_tasks()
        for task in tasks:
            task_id, name, task_type, schedule_mode, time_or_interval = task
            if schedule_mode == "Точное время":
                # Расписание для выполнения в конкретное время каждый день
                schedule.every().day.at(time_or_interval).do(run_task, name)
            elif schedule_mode == "Периодичность":
                # Расписание для периодического выполнения
                if "minute" in time_or_interval:
                    minutes = int(time_or_interval.split()[0])
                    schedule.every(minutes).minutes.do(run_task, name)
                elif "hour" in time_or_interval:
                    hours = int(time_or_interval.split()[0])
                    schedule.every(hours).hours.do(run_task, name)
                elif "day" in time_or_interval:
                    days = int(time_or_interval.split()[0])
                    schedule.every(days).days.do(run_task, name)
            elif schedule_mode == "Ручной":
                # Ручные задачи не добавляются в планировщик
                print(f"Задача {name} настроена на ручной запуск")
            else:
                print(f"Неизвестный режим расписания для задачи {name}")

    def get_task_info(task_name):
        return database_manager.get_task_details_by_name(task_name)

    if __name__ == "__main__":
        database_manager = DatabaseManager('db/db.sqlite')
        schedule_tasks()
        while True:
            schedule.run_pending()
            time.sleep(1)
