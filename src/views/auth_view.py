# src/views/auth_view.py
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QIcon, QIconEngine  # Исправленный импорт

from src.views.models.models import create_user, verify_user, get_user_role
from src.views.admin_view import AdminWindow
from src.views.buyer_view import BuyerWindow

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setWindowIcon(QIcon('./auth.png'))


        self.username_label = QLabel("Логин:")
        self.username_input = QLineEdit()

        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Войти")
        self.register_button = QPushButton("Зарегистрироваться")

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.handle_register)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        is_verified, role = verify_user(username, password)

        if is_verified:
            if role == 'admin':
                self.open_admin_window()
            elif role == 'buyer':
                self.open_buyer_window()
            else:
                QMessageBox.warning(self, "Ошибка", "Неизвестная роль пользователя.")
        else:
            QMessageBox.warning(self, "Ошибка", "Неверные учетные данные.")

    def handle_register(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if create_user(username, password):
            QMessageBox.information(self, "Регистрация", "Регистрация успешна")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким именем уже существует")

    def open_admin_window(self):
        self.admin_window = AdminWindow()
        self.admin_window.show()
        self.close()

    def open_buyer_window(self):
        self.buyer_window = BuyerWindow()
        self.buyer_window.show()
        self.close()
