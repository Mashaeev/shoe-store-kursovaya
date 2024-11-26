from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QListWidget, QMessageBox, QFrame
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt
from src.views.models.models import get_products
from src.db.database import get_db_connection


class BuyerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Покупатель - Магазин обуви")
        self.setGeometry(100, 100, 600, 500)
        self.init_ui()

    def init_ui(self):
        # Настройка основного шрифта
        font = QFont("Arial", 12)

        # Основной layout
        layout = QVBoxLayout()


        # Лейблы для отображения информации
        self.name_label = QLabel("Название: ")
        self.price_label = QLabel("Цена: ")
        self.product_image_label = QLabel()
        self.product_image_label.setFixedSize(200, 200)

        # Настройка списка товаров
        self.products_list = QListWidget()
        self.products_list.setFont(font)
        self.products_list.itemClicked.connect(self.display_product_image)

        # Настройка кнопок с округлыми краями
        self.cart_button = QPushButton("Добавить в корзину")
        self.cart_button.setFont(font)
        self.cart_button.setStyleSheet("QPushButton { border-radius: 10px; padding: 8px; background-color: #87CEEB; }")

        self.buy_button = QPushButton("Купить")
        self.buy_button.setFont(font)
        self.buy_button.setStyleSheet("QPushButton { border-radius: 10px; padding: 8px; background-color: #87CEEB; }")

        self.purchase_history_button = QPushButton("История покупок")
        self.purchase_history_button.setFont(font)
        self.purchase_history_button.setStyleSheet(
            "QPushButton { border-radius: 10px; padding: 8px; background-color: #87CEEB; }")

        # Добавляем элементы в основной layout
        layout.addWidget(QLabel("Доступные товары:"))
        layout.addWidget(self.products_list)
        layout.addWidget(self.product_image_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.price_label)
        layout.addWidget(self.cart_button)
        layout.addWidget(self.buy_button)
        layout.addWidget(self.purchase_history_button)

        # Подключение кнопок к функциям
        self.cart_button.clicked.connect(self.add_to_cart)
        self.buy_button.clicked.connect(self.buy_product)
        self.purchase_history_button.clicked.connect(self.view_purchase_history)

        self.setLayout(layout)
        self.cart = []
        self.load_products()

    def load_products(self):
        products = get_products()
        self.products_list.clear()
        for product in products:
            product_id, name, price, image_data, quantity = product
            self.products_list.addItem(f"{product_id}: {name} - {price} руб - {quantity} шт.")

    def display_product_image(self, item):
        try:
            product_info = item.text().split(": ")
            product_id = int(product_info[0])
            product_details = product_info[1].split(" - ")
            name = product_details[0]
            price = product_details[1]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT image FROM Products WHERE product_id = %s", (product_id,))
            image_data = cursor.fetchone()[0]

            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.product_image_label.setPixmap(pixmap.scaled(150, 150))
            self.product_image_label.setScaledContents(True)

            self.name_label.setText(f"Название: {name}")
            self.price_label.setText(f"Цена: {price}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {e}")

    def add_to_cart(self):
        current_item = self.products_list.currentItem()
        if current_item:
            self.cart.append(current_item.text())
            QMessageBox.information(self, "Добавлено в корзину", f"{current_item.text()} добавлен(а) в корзину.")

    def buy_product(self):
        if not self.cart:
            QMessageBox.warning(self, "Корзина пуста", "Добавьте товары перед покупкой.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            user_id = 1
            for item in self.cart:
                product_info = item.split(": ")
                product_id = int(product_info[0])
                product_name = product_info[1].split(" - ")[0]

                cursor.execute("SELECT quantity FROM Products WHERE product_id = %s", (product_id,))
                result = cursor.fetchone()

                if result is None:
                    QMessageBox.warning(self, "Ошибка", f"Товар '{product_name}' не найден в базе данных.")
                    continue

                quantity = result[0]
                if quantity > 0:
                    cursor.execute("INSERT INTO Purchases (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
                    cursor.execute("UPDATE Products SET quantity = quantity - 1 WHERE product_id = %s", (product_id,))
                    conn.commit()
                    QMessageBox.information(self, "Покупка успешна", f"{product_name} куплен.")
                else:
                    QMessageBox.warning(self, "Недостаточно на складе", f"{product_name} нет в наличии.")
            self.cart.clear()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось завершить покупку: {e}")
        finally:
            cursor.close()
            conn.close()

    def view_purchase_history(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            user_id = 1
            cursor.execute(
                "SELECT Products.name, Purchases.purchase_date FROM Purchases JOIN Products ON Purchases.product_id = Products.product_id WHERE Purchases.user_id = %s",
                (user_id,))
            purchases = cursor.fetchall()

            history_message = "История покупок:\n"
            for name, date in purchases:
                history_message += f"{name} - Куплено: {date}\n"

            QMessageBox.information(self, "История покупок", history_message)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить историю покупок: {e}")
        finally:
            cursor.close()
            conn.close()
