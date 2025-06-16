from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QHBoxLayout, QWidget, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
import re
from db.database import insert_user


class RegistrationWindow_U(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация/Редактирование")
        self.setFixedSize(500, 480)
        self.setStyleSheet("""
            background-color: #F5F5F5;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)
        self.init_ui()

    def init_ui(self):
        # Основной вертикальный макет окна
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(25)
        layout.setContentsMargins(20, 20, 20, 20)

        # === Заголовок и кнопка "Назад" ===
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)



        title_label = QLabel("Реактор пользователей")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #37474F;
            padding: 10px 0;
        """)

        back_button = QPushButton("Удалить")
        back_button.setFixedSize(80, 35)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: red;
                border: 1px solid red;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E8F5E9;
            }
            QPushButton:pressed {
                background-color: #C8E6C9;
            }
        """)
        back_button.clicked.connect(self.go_back)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(back_button)
        layout.addWidget(header_widget)

        user_combobox = QComboBox()
        user_combobox.addItems(["", "Бражко П.П.", "Администратор"])
        user_combobox.setStyleSheet("""
                    QComboBox {
                        font-weight: bold;
                        padding: 5px;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                    }
                """)
        layout.addWidget(user_combobox)

        # === Форма регистрации (белая панель) ===
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

        # Поле ввода ФИО
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ФИО")
        form_layout.addWidget(self.name_input)

        # Поле ввода места работы
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Место работы")
        form_layout.addWidget(self.location_input)

        # Поле ввода должности
        self.post_input = QLineEdit()
        self.post_input.setPlaceholderText("Должность")
        form_layout.addWidget(self.post_input)

        # === Перенесённые вниз поля логина и пароля ===

        # Поле ввода логина
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")
        form_layout.addWidget(self.login_input)

        # Поле ввода пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        # Подтверждение пароля
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Подтверждение пароля")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.confirm_input)

        # === Кнопка регистрации ===
        register_btn = QPushButton("Зарегистрировать/Обновить")
        register_btn.setFixedHeight(45)
        register_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: #FFFFFF;
                        border: none;
                        border-radius: 5px;
                        height: 60px;   
                        font-weight: bold;
                        font-size: 16px;
                    }
                    QPushButton:hover {
                        background-color: #388E3C;
                         color: #FFFFFF;
                    }
                    QPushButton:disabled {
                        background-color: #A5D6A7;
                         color: #FFFFFF;
                    }
                """)
        register_btn.clicked.connect(self.register)
        #register_btn.setText("Тест")
        print(register_btn.text())  # вывод текста в консоль
        form_layout.addWidget(register_btn)

        layout.addWidget(form_frame)
        self.setLayout(layout)

    # === Валидация данных ===
    def validate_inputs(self):
        name = self.name_input.text().strip()
        login = self.login_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not name or len(name.split()) < 2:
            self.show_error("Пожалуйста, введите полное имя (ФИО)")
            return False

        if len(login) < 4:
            self.show_error("Логин должен содержать минимум 4 символа")
            return False

        if len(password) < 8:
            self.show_error("Пароль должен быть не менее 8 символов")
            return False

        if password != confirm:
            self.show_error("Пароли не совпадают")
            return False

        return True
    def clear_inputs(self):
        self.login_input.clear()
        self.password_input.clear()
        self.FIO_input.clear()
        self.Location_input.clear()
        self.post_input.clear()

    # === Показ окна с ошибкой ===
    def show_error(self, message):
        QMessageBox.warning(self, "Ошибка", message)

    # === Показ окна с успешной регистрацией ===
    def show_success(self):
        QMessageBox.information(
            self,
            "Успешная регистрация",
            "Регистрация прошла успешно!\n"
            "Теперь вы можете войти в систему."
        )

    # === Обработка кнопки регистрации ===
    def register(self):
        if not self.validate_inputs():
            return

        # Здесь может быть сохранение данных в базу данных

        insert_user(self.name_input,self.location_input, self.post_input, self.login_input, self.password_input)
        self.show_success()

        self.clear_inputs()


    # === Обработка кнопки "Назад" ===
    def go_back(self):
        self.reject()
        self.parent().show()  # Показываем родителя
        self.close()  # Закрываем окно регистрации

