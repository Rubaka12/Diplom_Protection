import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QLineEdit, QFormLayout,
    QListWidget, QGridLayout, QGroupBox,
    QComboBox, QDateTimeEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QIntValidator, QCursor
import pyqtgraph as pg
from db.database import param_descr, get_title_graph, anomalis_count, chat_err

from functools import partial

import mysql.connector
from resources.config import DB_CONFIG


class SecondPage(QWidget):
    def __init__(self, equipment_id, table_name, name, location, parent=None):
        super().__init__(parent)
        self.equipment_id = equipment_id
        print("Данные об id оборудования self.equipment_id:", self.equipment_id)
        self.table_name = table_name
        print("Данные о названии таблицы self.table_name", self.table_name)
        self.equipment_name = name
        print("Данные об названии оборудования self.equipment_name", self.equipment_name)
        self.equipment_location = location
        print("Данные местоположении оборудования self.equipment_location", self.equipment_location)

        anomalis_count(table_name, equipment_id)
        self.plot_items = {}
        self.checkbox_map = {}
        self.param_colors = {}

        main_layout = QVBoxLayout(self)
        self.top_bar = QFrame()
        self.top_bar.setFixedHeight(50)
        self.top_bar.setStyleSheet("background-color: #4CAF50;")
        self.top_layout = QHBoxLayout(self.top_bar)

        self.title_label = QLabel(f"{self.equipment_name} ({self.equipment_location})")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        self.top_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)

        self.top_layout.addStretch()
        self.back_btn = QPushButton("← Назад")
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #388E3C;
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2E7D32;
            }
        """)
        if parent:
            self.back_btn.clicked.connect(parent.show_main_page)
            self.back_btn.clicked.connect(self.close)
        else:
            self.back_btn.clicked.connect(self.close)  # просто закрываем окно

        self.top_layout.addWidget(self.back_btn)
        main_layout.addWidget(self.top_bar)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        main_layout.addLayout(grid_layout)

        # === График ===
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.getPlotItem().showGrid(x=True, y=True)
        self.plot_widget.getPlotItem().setTitle("График показателей: данные за последнюю минуту")
        self.plot_widget.getPlotItem().getAxis('bottom').setPen(pg.mkPen(color='#4CAF50'))
        self.plot_widget.getPlotItem().getAxis('left').setPen(pg.mkPen(color='#4CAF50'))

        graph_frame = QGroupBox("График")
        graph_frame.setStyleSheet("QGroupBox { font-weight: bold; border: 2px solid #4CAF50; border-radius: 5px; margin-top: 0.5em; } QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 3px; }")
        graph_layout = QVBoxLayout(graph_frame)
        graph_layout.setContentsMargins(5, 5, 5, 5)
        graph_layout.addWidget(self.plot_widget)
        grid_layout.addWidget(graph_frame, 0, 0, 3, 3)

        # === Время и период ===
        controls_container = QGroupBox("Время и периодичность")
        controls_container.setStyleSheet(graph_frame.styleSheet())
        controls_layout = QVBoxLayout(controls_container)

        date_form_layout = QFormLayout()
        self.date_from = QDateTimeEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDateTime(QDateTime.currentDateTime())
        self.date_to = QDateTimeEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDateTime(QDateTime.currentDateTime())
        date_form_layout.addRow("От:", self.date_from)
        date_form_layout.addRow("До:", self.date_to)
        controls_layout.addLayout(date_form_layout)

        time_layout = QHBoxLayout()
        self.time_eu = QComboBox()
        self.time_eu.addItems(["минута", "час", "день"])
        self.last_time = QComboBox()
        self.last_time.addItems(["Последняя минута", "Последний час", "Последний день"])
        time_layout.addWidget(self.time_eu)
        time_layout.addWidget(self.last_time)
        controls_layout.addLayout(time_layout)

        button_layout = QHBoxLayout()
        self.custom_time_btn = QPushButton("Кастомное время")
        self.prepared_time_btn = QPushButton("Заготовленное время")
        button_layout.addWidget(self.custom_time_btn)
        button_layout.addWidget(self.prepared_time_btn)
        controls_layout.addLayout(button_layout)

        grid_layout.addWidget(controls_container, 3, 0, 1, 2)

        # === Легенда графика ===
        self.legend_container = QGroupBox("Легенда графика")
        self.legend_container.setStyleSheet(graph_frame.styleSheet())
        self.legend_layout = QVBoxLayout(self.legend_container)
        self.legend_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid_layout.addWidget(self.legend_container, 3, 2, 1, 1)

        '''
        # === Легенда графика ===
        self.legend_container = QGroupBox("Легенда графика")
        self.legend_container.setStyleSheet(graph_frame.styleSheet())
        legend_main_layout = QVBoxLayout(self.legend_container)  # основной layout легенды

        # Комбобокс-переключатель
        legend_selector_layout = QHBoxLayout()
        self.legend_mode_selector = QComboBox()
        self.legend_mode_selector.addItems(["Показатели", "Группы показателей"])
        self.legend_mode_selector.setFixedHeight(28)
        self.legend_mode_selector.currentTextChanged.connect(self.load_and_plot_data)

        legend_selector_layout.addWidget(QLabel("Тип:"))
        legend_selector_layout.addWidget(self.legend_mode_selector)

        legend_main_layout.addLayout(legend_selector_layout)

        # Layout для чекбоксов (внутренний)
        self.legend_layout = QVBoxLayout()
        self.legend_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        legend_main_layout.addLayout(self.legend_layout)

        # Добавляем контейнер на grid
        grid_layout.addWidget(self.legend_container, 3, 2, 1, 1)
        '''
        # === Чат сообщений ===
        chat_group = QGroupBox("Сообщения об ошибках")
        chat_group.setStyleSheet(graph_frame.styleSheet())
        self.messages_container = QVBoxLayout(chat_group)

        self.messages_list = QListWidget()
        self.messages_list.setStyleSheet("""
            QListWidget {
                background-color: #F5F5F5;
                border: none;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin: 2px;
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #F0F4F8;
                border: 1px solid #4CAF50;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                border: 1px solid #2196F3;
            }
        """)
        self.messages_container.addWidget(self.messages_list)

        # Поле ввода сообщения
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите текст сообщения об ошибке...")
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        self.messages_container.addWidget(self.message_input)

        # Кнопка добавления сообщения
        self.add_message_btn = QPushButton("Добавить сообщение")
        self.add_message_btn.clicked.connect(self.add_error_message)
        self.messages_container.addWidget(self.add_message_btn)

        grid_layout.addWidget(chat_group, 0, 3, 4, 2)

        # Загрузка сообщений из БД
        messages = chat_err(self.equipment_id)
            #[(A1, 'превышено', 150, '2025-06-01')
        for param, status, date, user in messages:
            self.messages_list.addItem(f"{param} {status}: {str(date)} {user.strftime('%d.%m.%Y')}")

        #for i in range(5):
        #    self.messages_list.addItem(f"А1 Ошибка {['обнаружена', 'в процессе устранения: Бражко П.П.', 'устранена: Бражко П.П.'][i % 3]} {['17.05.2025', '18.05.2025', '19.05.2025', '19.05.2025', '20.05.2025'][i % 5]}")

        # Загрузим данные и построим графики
        self.load_and_plot_data()

    def load_and_plot_data(self):
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            # Получаем список всех колонок таблицы
            cursor.execute(f"SHOW COLUMNS FROM {self.table_name}")
            all_columns = [col[0] for col in cursor.fetchall()]
            ignored = {"id", "equipment_id", "timestamp", "location"}
            parameter_columns = [col for col in all_columns if col not in ignored]

            # Формируем запрос
            columns_str = ", ".join(parameter_columns + ["timestamp"])
            query = f"""
                SELECT {columns_str}
                FROM {self.table_name}
                WHERE equipment_id = %s
                ORDER BY timestamp DESC
                LIMIT 6
            """
            cursor.execute(query, (self.equipment_id,))
            rows = cursor.fetchall()
            rows.reverse()  # Реверс для правильного порядка времени


            if not rows:
                self.plot_widget.plot([], [])
                return

            # Подготовка данных для графиков
            timestamps = [row[-1].strftime("%H:%M:%S") for row in rows]

            print(self.table_name)
            names = get_title_graph(self.table_name)[3]
            print("names", names)

            #print("parameter_columns перед: ", names)#parameter_columns
            data_by_param = {col: [] for col in names}
            #print("data_by_param после", data_by_param)

            print("parameter_columns", parameter_columns)
            for row in rows:
                for idx, col in enumerate(names):
                    data_by_param[col].append(row[idx])

            print("data_by_param", data_by_param)

            # Очистка предыдущих элементов
            self.plot_widget.clear()
            self.plot_items.clear()
            self.checkbox_map.clear()

            # Очистка легенды
            while self.legend_layout.count():
                child = self.legend_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            # Получаем описания параметров
            param_descriptions = param_descr(self.equipment_id)

            # Цветовая палитра
            color_pool = [
                "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
                "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe"
            ]

            # Создаем графики и чекбоксы

            for i, (param, values) in enumerate(data_by_param.items()):
                color = color_pool[i % len(color_pool)]
                pen = pg.mkPen(color=color, width=2)

                plot = self.plot_widget.plot(
                    list(range(len(values))),
                    values,
                    pen=pen,
                    name=param
                )
                self.plot_items[param] = plot
                self.param_colors[param] = color

                description = param_descriptions.get(param, param)
                checkbox = QCheckBox(description)
                checkbox.setChecked(True)
                checkbox.setStyleSheet(f"color: {color}; font-weight: bold;")
                checkbox.toggled.connect(partial(self.toggle_plot, param))
                self.legend_layout.addWidget(checkbox)
                self.checkbox_map[param] = checkbox

            #legend_mode = self.legend_mode_selector.currentText() if hasattr(self,
            #                                                                 "legend_mode_selector") else "Показатели"
            #if legend_mode == "Показатели":
                # for i, (param, values) in enumerate(data_by_param.items()):
                #     color = color_pool[i % len(color_pool)]
                #     pen = pg.mkPen(color=color, width=2)
                #
                #     plot = self.plot_widget.plot(
                #         list(range(len(values))),
                #         values,
                #         pen=pen,
                #         name=param
                #     )
                #     self.plot_items[param] = plot
                #     self.param_colors[param] = color
                #
                #     description = param_descriptions.get(param, param)
                #     checkbox = QCheckBox(description)
                #     checkbox.setChecked(True)
                #     checkbox.setStyleSheet(f"color: {color}; font-weight: bold;")
                #     checkbox.toggled.connect(partial(self.toggle_plot, param))
                #     self.legend_layout.addWidget(checkbox)
                #     self.checkbox_map[param] = checkbox

            # elif legend_mode == "Группы показателей":
            #     placeholder_label = QLabel("Пока нет кода для группировки параметров.")
            #     placeholder_label.setStyleSheet("color: gray; font-style: italic; padding: 5px;")
            #     self.legend_layout.addWidget(placeholder_label)

            # Устанавливаем метки времени на оси X
            self.plot_widget.getPlotItem().getAxis('bottom').setTicks([list(enumerate(timestamps))])

        except mysql.connector.Error as e:
            print("Ошибка при работе с БД:", e)
            self.messages_list.addItem(f"Ошибка загрузки данных: {e}")
        finally:
            cursor.close()
            conn.close()

    def toggle_plot(self, param, checked):
        if param in self.plot_items:
            print("param", param)
            self.plot_items[param].setVisible(checked)

    # def toggle_group(self, param_list, checked):
    #     for param in param_list:
    #         if param in self.plot_items:
    #             self.plot_items[param].setVisible(checked)
    #         if param in self.checkbox_map:
    #             self.checkbox_map[param].setChecked(checked)

    def add_error_message(self):

        message_text = self.message_input.text().strip()
        if message_text:
            self.messages_list.addItem(message_text)
            self.message_input.clear()
        else:
            # Если пусто, добавим автосообщение, как раньше
            count = self.messages_list.count() + 1
            self.messages_list.addItem(f"Ошибка {count}")

        if self.messages_list.count() >= 10:
            self.messages_list.scrollToBottom()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecondPage(
        equipment_id=0,
        table_name="",
        name="",
        location=""
    )
    window.setWindowTitle("Данные оборудования")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())