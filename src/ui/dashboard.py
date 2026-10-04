from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QTableWidget, QPushButton, QHBoxLayout, QListWidget,
                             QLineEdit, QToolBar, QAction, QSplitter, QWidget, QListWidgetItem, QMessageBox, QFileDialog, QLabel, QFormLayout, QComboBox, QTableWidgetItem,
                             QGroupBox, QSizePolicy, QApplication, QStackedWidget, QMainWindow, QDesktopWidget)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys

# Assume these modules are correctly implemented and imported
from src.ui.price_manager import PriceManager
from src.ui.home_window import HomeFrame
from src.ui.scraper_window import ScraperFrame
from src.ui.estimates_window import EstimatesFrame
from src.ui.import_window import ImportFrame
from src.ui.export_window import ExportFrame
from config import *

class MainFrame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SmartPricingTool')
        self.setGeometry(0, 0, 1100, 600)
        self.center()  # Center the window

        # Stacked widget to manage multiple pages
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)

        # Initialize frames
        self.home_window_frame = HomeFrame()
        self.price_manager_frame = PriceManager()
        self.scraper_window_frame = ScraperFrame()
        self.estimates_window_frame = EstimatesFrame()
        self.import_window_frame = ImportFrame()
        self.export_window_frame = ExportFrame()

        # Add frames to the stacked widget
        self.stacked_widget.addWidget(self.home_window_frame)
        self.stacked_widget.addWidget(self.price_manager_frame)
        self.stacked_widget.addWidget(self.estimates_window_frame)
        self.stacked_widget.addWidget(self.scraper_window_frame)
        self.stacked_widget.addWidget(self.import_window_frame)
        self.stacked_widget.addWidget(self.export_window_frame)

        # Initialize toolbar and actions
        self.toolbar = QToolBar("Main Toolbar", self)
        self.addToolBar(self.toolbar)
        self.setupActions()

    def center(self):
        qr = self.frameGeometry()  # Get a rectangle specifying the geometry of the main window
        cp = QDesktopWidget().availableGeometry().center()  # Get the center point of the screen
        qr.moveCenter(cp)  # Move the rectangle's center to the screen's center
        self.move(qr.topLeft())

    def setupActions(self):
        # Home Window Action
        home_action = QAction(QIcon(HOME_ICON), 'Главная', self)
        home_action.triggered.connect(self.showHome)
        self.toolbar.addAction(home_action)

        # Price Manager Window Action
        price_manager_action = QAction(QIcon(PRICE_ICON), 'Управление прайсами', self)
        price_manager_action.triggered.connect(self.showPriceManager)
        self.toolbar.addAction(price_manager_action)

        # Scraper Window Action
        scraper_window_action = QAction(QIcon(SCRAPER_ICON), 'Парсер', self)
        scraper_window_action.triggered.connect(self.showScraper)
        self.toolbar.addAction(scraper_window_action)

        estimates_window_action = QAction(QIcon(ESTIMATE_ICON), 'Наценки', self)
        estimates_window_action.triggered.connect(self.showEstimates)
        self.toolbar.addAction(estimates_window_action)

        import_window_action = QAction(QIcon(IMPORT_ICON), 'Импорт', self)
        import_window_action.triggered.connect(self.showImportFrame)
        self.toolbar.addAction(import_window_action)
        
        export_window_frame = QAction(QIcon(EXPORT_ICON), 'Экспорт', self)
        export_window_frame.triggered.connect(self.showExportFrame)
        self.toolbar.addAction(export_window_frame)

    def showHome(self):
        self.stacked_widget.setCurrentWidget(self.home_window_frame)
        self.home_window_frame.populate_data_panel()

    def showPriceManager(self):
        self.stacked_widget.setCurrentWidget(self.price_manager_frame)

    def showScraper(self):
        self.stacked_widget.setCurrentWidget(self.scraper_window_frame)

    def showEstimates(self):
        self.stacked_widget.setCurrentWidget(self.estimates_window_frame)
        
    def showImportFrame(self):
        self.stacked_widget.setCurrentWidget(self.import_window_frame)
        
    def showExportFrame(self):
        self.stacked_widget.setCurrentWidget(self.export_window_frame)


class ProductView(QDialog):
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_frame = MainFrame()
    main_frame.show()
    sys.exit(app.exec_())
