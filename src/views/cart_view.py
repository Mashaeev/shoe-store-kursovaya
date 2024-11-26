from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from src.db.database import get_db_connection
from datetime import datetime

class CartWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("Корзина")
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()
        self.load_cart_items()

    def init_ui(self):
        layout = QVBoxLayout()

        self.cart_label = QLabel("Товары в корзине")
        self.cart_list = QListWidget()  # Отображение товаров в корзине

        self.checkout_button = QPushButton("Оформить заказ")
        self.checkout_button.clicked.connect(self.checkout)

        layout.addWidget(self.cart_label)
        layout.addWidget(self.cart_list)
        layout.addWidget(self.checkout_button)

        self.setLayout(layout)

    def load_cart_items(self):
        """Загружает товары из корзины пользователя."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT p.name, p.price, c.quantity
                FROM Cart c
                JOIN Products p ON c.product_id = p.product_id
                WHERE c.user_id = %s
            """, (self.user_id,))
            items = cursor.fetchall()
            self.cart_list.clear()
            for name, price, quantity in items:
                self.cart_list.addItem(f"{name} - {price} руб. x {quantity}")
        except Exception as e:
            print(f"Ошибка при загрузке товаров корзины: {e}")
        finally:
            cursor.close()
            conn.close()

    def checkout(self):
        """Оформляет заказ и создает чек."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Orders (user_id, order_date) VALUES (%s, %s) RETURNING order_id
            """, (self.user_id, datetime.now()))
            order_id = cursor.fetchone()[0]

            # Переносим товары из корзины в заказ
            cursor.execute("""
                INSERT INTO OrderItems (order_id, product_id, quantity, price)
                SELECT %s, c.product_id, c.quantity, p.price
                FROM Cart c
                JOIN Products p ON c.product_id = p.product_id
                WHERE c.user_id = %s
            """, (order_id, self.user_id))

            # Создаем чек
            cursor.execute("""
                INSERT INTO Receipts (order_id, receipt_date) VALUES (%s, %s)
            """, (order_id, datetime.now()))

            # Очищаем корзину
            cursor.execute("DELETE FROM Cart WHERE user_id = %s", (self.user_id,))

            conn.commit()
            QMessageBox.information(self, "Заказ оформлен", "Ваш заказ успешно оформлен!")
            self.close()  # Закрываем окно корзины после оформления заказа
        except Exception as e:
            conn.rollback()
            print(f"Ошибка при оформлении заказа: {e}")
            QMessageBox.warning(self, "Ошибка", "Не удалось оформить заказ.")
        finally:
            cursor.close()
            conn.close()
