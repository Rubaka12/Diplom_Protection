from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QApplication, QHeaderView, QMessageBox, QComboBox
)
from functools import partial
from PyQt6.QtCore import Qt
import sys

from db.database import register_equipment, find_names
# a; d; 123; 1234; d

# Функция для преобразования текста в верхний регистр с сохранением позиции курсора
def to_uppercase_lineedit(lineedit):
    cursor_pos = lineedit.cursorPosition()
    text = lineedit.text()
    new_text = text.upper()

    if text != new_text:
        lineedit.setText(new_text)
        lineedit.setCursorPosition(cursor_pos)

class RegistrationWindowA(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Регистрация/Редактирование")
        self.setFixedWidth(389)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.header = QLabel("Регистрация/Редактирование")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                border-radius: 6px;
            }
        """)
        self.layout.addWidget(self.header)
        self.name = find_names()
        self.user_combobox = QComboBox()
        self.user_combobox.addItems([""])
        for i in self.name:
            self.user_combobox.addItems(i)
        self.user_combobox.setStyleSheet("""
                    QComboBox {
                        font-weight: bold;
                        padding: 5px;
                        border: 1px solid #4CAF50;
                        border-radius: 4px;
                    }
                """)
        self.layout.addWidget(self.user_combobox)

        self.name_label = QLabel("Имя")
        self.name_label.setStyleSheet("font-weight: bold; border-bottom: 2px solid #4CAF50;")
        self.name_input = QLineEdit()
        self.name_input.textChanged.connect(lambda: to_uppercase_lineedit(self.name_input))
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        self.model_label = QLabel("Модель")
        self.model_label.setStyleSheet("font-weight: bold; border-bottom: 2px solid #4CAF50;")
        self.model_input = QLineEdit()
        self.model_input.textChanged.connect(lambda: to_uppercase_lineedit(self.model_input))
        self.layout.addWidget(self.model_label)
        self.layout.addWidget(self.model_input)

        self.location_label = QLabel("Местонахождения")
        self.location_label.setStyleSheet("font-weight: bold; border-bottom: 2px solid #4CAF50;")
        self.location_input = QLineEdit()
        self.location_input.textChanged.connect(lambda: to_uppercase_lineedit(self.location_input))
        self.layout.addWidget(self.location_label)
        self.layout.addWidget(self.location_input)

        self.data_label = QLabel("Показатель; ЕИ; Мин; Макс; Группа")
        self.data_label.setStyleSheet("font-weight: bold; border-bottom: 2px solid #4CAF50;")
        self.data_input = QLineEdit()
        self.data_input.textChanged.connect(lambda: to_uppercase_lineedit(self.data_input))
        self.data_button = QPushButton("Подтвердить")
        self.data_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.data_button.clicked.connect(self.add_data_entry)

        self.layout.addWidget(self.data_label)
        self.layout.addWidget(self.data_input)
        self.layout.addWidget(self.data_button)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Показатель", "ЕИ", "Мин", "Макс", "Группа"])
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setDefaultSectionSize(70)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.layout.addWidget(self.table)

        self.button_layout = QHBoxLayout()

        self.delete_button = QPushButton("Удалить")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.delete_button.clicked.connect(self.delete_row)
        self.button_layout.addWidget(self.delete_button)

        self.layout.addLayout(self.button_layout)

        self.register_button = QPushButton("Зарегистрировать/Обновить")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.register_button.clicked.connect(self.register_data)
        self.layout.addWidget(self.register_button)

    def add_data_entry(self):
        raw = self.data_input.text()
        parts = [p.strip().upper() if i == 0 else p.strip() for i, p in enumerate(raw.split(';'))]

        if len(parts) != 5:
            QMessageBox.warning(self, "Ошибка",
                                "Неверный формат строки. Используйте: показатель; ЕИ; Мин; Макс; Группа.")
            return

        try:
            min_val = float(parts[2])
            max_val = float(parts[3])

            if min_val > max_val:
                QMessageBox.warning(self, "Ошибка", "Значение 'Мин' не может быть больше 'Макс'.")
                return
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Мин и Макс должны быть числовыми значениями.")
            return

        # Проверка на дубликаты показателей (в т.ч. с разным регистром)
        for row in range(self.table.rowCount()):
            existing_indicator = self.table.item(row, 0).text().strip().upper()
            if existing_indicator == parts[0]:
                QMessageBox.warning(self, "Ошибка", f"Показатель '{parts[0]}' уже добавлен в таблицу.")
                return

        row = self.table.rowCount()
        self.table.insertRow(row)
        for i, value in enumerate(parts):
            self.table.setItem(row, i, QTableWidgetItem(value))

        self.data_input.clear()

    def delete_row(self):
        selected = self.table.currentRow()
        if selected >= 0:
            self.table.removeRow(selected)

    def register_data(self):
        name = self.name_input.text().strip()
        model = self.model_input.text().strip()
        location = self.location_input.text().strip()
        parameters = []

        if not name or not model or not location:
            QMessageBox.warning(self, "Ошибка", "Имя, Модель и Место дислокации обязательны для заполнения.")
            return

        indicator_names = set()

        for row in range(self.table.rowCount()):
            try:
                parts = [self.table.item(row, col).text().strip() for col in range(5)]

                # Проверка на пустые значения
                if not all(parts):
                    QMessageBox.warning(self, "Ошибка", f"Строка {row + 1} содержит пустые поля.")
                    return

                indicator = parts[0].upper()
                if indicator in indicator_names:
                    QMessageBox.warning(self, "Ошибка", f"Показатель '{indicator}' в строке {row + 1} уже использован.")
                    return
                indicator_names.add(indicator)

                min_val = float(parts[2])
                max_val = float(parts[3])
                if min_val > max_val:
                    QMessageBox.warning(self, "Ошибка", f"В строке {row + 1} значение 'Мин' больше, чем 'Макс'.")
                    return

                # Приводим к верхнему регистру только показатель
                parts[0] = indicator
                parameters.append(parts)

            except Exception:

                QMessageBox.warning(self, "Ошибка", f"Строка {row + 1} содержит недопустимые значения.")
                return

        try:
            print("parameters", parameters)
            register_equipment(name, model, location, parameters)
            QMessageBox.information(self, "Успех", "Оборудование успешно зарегистрировано.")

            # Очистка формы
            self.name_input.clear()
            self.model_input.clear()
            self.location_input.clear()
            self.table.setRowCount(0)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при регистрации:\n{str(e)}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = RegistrationWindow()
#     window.show()
#     sys.exit(app.exec())