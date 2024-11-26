from PyQt6.QtWidgets import QVBoxLayout, QWidget, QLabel, QListWidget
from src.db.database import get_db_connection

class PurchaseHistoryWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle("История покупок")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.history_label = QLabel("История покупок:")
        self.history_list = QListWidget()

        # Загрузите историю из базы данных
        self.load_purchase_history()

        layout.addWidget(self.history_label)
        layout.addWidget(self.history_list)

        self.setLayout(layout)

    def load_purchase_history(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT product_name FROM PurchaseHistory WHERE user_id = %s", (self.user_id,))
            purchases = cursor.fetchall()
            for purchase in purchases:
                self.history_list.addItem(purchase[0])  # Добавляем каждую покупку в список
        except Exception as e:
            print(f"Ошибка при загрузке истории покупок: {e}")
        finally:
            cursor.close()
            conn.close()
