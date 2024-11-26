# src/views/admin_view.py
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon
from src.views.models.models import add_product

class AdminWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Администратор - Управление продуктами")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon('./admin.png'))
        self.init_ui()

    def init_ui(self):

        layout = QVBoxLayout()


        self.name_label = QLabel("Название товара:")
        self.name_input = QLineEdit()

        self.price_label = QLabel("Цена:")
        self.price_input = QLineEdit()

        self.image_label = QLabel("Изображение:")
        self.image_path_display = QLabel("Файл не выбран")
        self.image_button = QPushButton("Загрузить изображение")

        self.quantity_label = QLabel("Количество:")
        self.quantity_input = QLineEdit()
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)

        self.add_product_button = QPushButton("Добавить продукт")

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(self.image_label)
        layout.addWidget(self.image_path_display)
        layout.addWidget(self.image_button)
        layout.addWidget(self.add_product_button)

        self.setLayout(layout)

        # Подключаем кнопки к функциям
        self.image_button.clicked.connect(self.load_image)
        self.add_product_button.clicked.connect(self.add_product)

        # Поле для хранения загруженного изображения
        self.image_blob = None

    def load_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.xpm *.jpg)")
        if image_path:
            with open(image_path, "rb") as file:
                self.image_blob = file.read()
            self.image_path_display.setText(image_path)

    def add_product(self):
        name = self.name_input.text()
        price = self.price_input.text()
        quantity = self.quantity_input.text()

        if not (name and price and quantity and self.image_blob):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля и выберите изображение.")
            return

        try:
            add_product(name, float(price), self.image_blob, int(quantity))
            QMessageBox.information(self, "Успех", "Продукт добавлен успешно.")
            self.clear_fields()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить продукт: {e}")

    def clear_fields(self):
        self.name_input.clear()
        self.price_input.clear()
        self.image_path_display.setText("Файл не выбран")
        self.image_blob = None
