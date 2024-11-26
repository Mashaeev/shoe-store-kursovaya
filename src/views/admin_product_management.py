from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit, QMessageBox, QFileDialog, QInputDialog
from PyQt6.QtGui import QPixmap
from src.db.database import get_db_connection

class AdminProductManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление каталогом товаров")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        self.product_name_label = QLabel("Название продукта:")
        self.product_name_input = QLineEdit()

        self.product_price_label = QLabel("Цена продукта:")
        self.product_price_input = QLineEdit()

        self.product_image_label = QLabel("Изображение:")
        self.product_image_input = QLineEdit()

        # Correct connection for upload_image
        self.upload_image_button = QPushButton("Загрузить изображение")
        self.upload_image_button.clicked.connect(self.upload_image)  # Ensure upload_image is defined
        self.upload_image_button.setStyleSheet(
            "background-color: #008CBA; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")

        self.add_product_button = QPushButton("Добавить продукт")
        self.add_product_button.clicked.connect(self.add_product)
        self.add_product_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; border-radius: 5px;")

        layout.addWidget(self.product_name_label)
        layout.addWidget(self.product_name_input)
        layout.addWidget(self.product_price_label)
        layout.addWidget(self.product_price_input)
        layout.addWidget(self.product_image_label)
        layout.addWidget(self.product_image_input)
        layout.addWidget(self.upload_image_button)
        layout.addWidget(self.add_product_button)

        self.setLayout(layout)

        # Initialize product list
        self.product_list = QListWidget()
        layout.addWidget(self.product_list)

    def load_products(self):
        """Загружает список товаров из базы данных."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT product_id, name, price FROM Products")
            products = cursor.fetchall()
            self.product_list.clear()
            for product_id, name, price in products:
                self.product_list.addItem(f"{product_id} - {name} - {price} руб.")
        except Exception as e:
            print(f"Ошибка при загрузке товаров: {e}")
        finally:
            cursor.close()
            conn.close()

    def add_product(self):
        """Добавляет новый продукт."""
        name, ok1 = QInputDialog.getText(self, "Добавить товар", "Введите название товара:")
        if not ok1 or not name:
            return
        price, ok2 = QInputDialog.getDouble(self, "Добавить товар", "Введите цену товара:", decimals=2)
        if not ok2:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Products (name, price) VALUES (%s, %s)", (name, price))
            conn.commit()
            self.load_products()  # Обновляем список после добавления
            QMessageBox.information(self, "Добавление товара", "Товар успешно добавлен.")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при добавлении товара: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить товар.")
        finally:
            cursor.close()
            conn.close()

    def edit_product(self):
        """Редактирует выбранный товар."""
        selected_item = self.product_list.currentItem()
        if selected_item is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите товар для редактирования.")
            return

        product_info = selected_item.text().split(" - ")
        product_id = int(product_info[0])

        new_name, ok1 = QInputDialog.getText(self, "Редактировать товар", "Введите новое название товара:")
        if not ok1 or not new_name:
            return
        new_price, ok2 = QInputDialog.getDouble(self, "Редактировать товар", "Введите новую цену товара:", decimals=2)
        if not ok2:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Products SET name = %s, price = %s WHERE product_id = %s",
                           (new_name, new_price, product_id))
            conn.commit()
            self.load_products()  # Обновляем список после редактирования
            QMessageBox.information(self, "Редактирование товара", "Товар успешно обновлен.")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при редактировании товара: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить товар.")
        finally:
            cursor.close()
            conn.close()

    def delete_product(self):
        """Удаляет выбранный товар из базы данных."""
        selected_item = self.product_list.currentItem()
        if selected_item is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите товар для удаления.")
            return

        product_info = selected_item.text().split(" - ")
        product_id = int(product_info[0])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Products WHERE product_id = %s", (product_id,))
            conn.commit()
            self.load_products()  # Обновляем список после удаления
            QMessageBox.information(self, "Удаление товара", "Товар успешно удален.")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при удалении товара: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось удалить товар.")
        finally:
            cursor.close()
            conn.close()

    def upload_image(self):
        """Загружает изображение для выбранного товара и сохраняет его в базе данных."""
        selected_item = self.product_list.currentItem()
        if selected_item is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите товар для загрузки изображения.")
            return

        product_info = selected_item.text().split(" - ")
        product_id = int(product_info[0])

        image_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not image_path:
            return

        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Products SET image = %s WHERE product_id = %s", (image_data, product_id))
            conn.commit()
            QMessageBox.information(self, "Загрузка изображения", "Изображение успешно загружено.")
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при загрузке изображения: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение.")
        finally:
            cursor.close()
            conn.close()
