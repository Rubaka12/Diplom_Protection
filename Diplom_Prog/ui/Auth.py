from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QHBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from db.database import find_user

class AuthWindow(QDialog):
    def __init__(self, main_window_start=None):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #F5F5F5;")
        self.main_window_start = main_window_start
        self.main_app_window = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)

        # Заголовок и кнопка "Назад"
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Авторизация")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #37474F;")

        back_button = QPushButton("Назад")
        back_button.setFixedSize(70, 30)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #4CAF50;
                border: 1px solid #4CAF50;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
        """)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(back_button)

        layout.addWidget(header_widget)

        # Форма авторизации
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        form_layout.addWidget(self.login_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        login_btn = QPushButton("Войти")
        login_btn.clicked.connect(self.authenticate)
        form_layout.addWidget(login_btn)

        layout.addWidget(form_frame)
        self.setLayout(layout)

    def authenticate(self):
        from ui.main_window import MainWindow
        from ui.main_window_admin import MainWindowA
        login = self.login_input.text()
        password = self.password_input.text()

        if find_user(login, password) == 1:
            if self.main_window_start:
                self.main_window_start.close()  # Закрываем стартовое окно
            self.accept()  # Закрываем окно авторизации

            self.main_app_window = MainWindowA()
            self.main_app_window.show()
        elif find_user(login, password) == 0:
            self.login_input.setStyleSheet("border: 2px solid red;")
            self.password_input.setStyleSheet("border: 2px solid red;")
        else:
            if self.main_window_start:
                self.main_window_start.close()  # Закрываем стартовое окно
            self.accept()  # Закрываем окно авторизации

            self.main_app_window = MainWindow()
            self.main_app_window.show()

    def go_back(self):
        # Показываем стартовое окно и закрываем авторизацию
        if self.main_window_start:
            self.main_window_start.show()
        self.close()
