from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QFrame, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt

from db.database import get_machine_tables
from ui.machine_window_no_ckick import MachineWindow
from ui.Extended_Layout import SecondPage
from db.database import get_equipment_info_by_table
from ui.Auth import AuthWindow


class MainWindowStart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главная страница")
        self.setGeometry(100, 100, 800, 600)
        self.cell_containers = []

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Верхняя панель
        top_frame = QFrame()
        top_frame.setFixedHeight(50)
        top_frame.setStyleSheet("background-color: #4CAF50;")

        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(10, 0, 10, 0)

        title_label = QLabel("Главная страница")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: white; font-size: 18px;")

        auth_button = QPushButton("Авторизоваться")
        auth_button.setFixedSize(120, 30)
        auth_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #4CAF50;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
            }
        """)
        auth_button.clicked.connect(self.open_auth_window)

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(auth_button)

        # Основная область с grid
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(20, 20, 20, 20)
        grid_layout.setSpacing(10)
        grid_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        tables = get_machine_tables()
        max_cells = 2 * 5

        for index in range(max_cells):
            container = QWidget()
            cell_layout = QVBoxLayout(container)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            container.setLayout(cell_layout)
            container.setFixedSize(200, 250)

            if index < len(tables):
                window = MachineWindow(table_name=tables[index])
                cell_layout.addWidget(window)
            elif index == len(tables):
                label = QLabel("Нет данных")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("color: #9E9E9E; font-style: italic;")
                cell_layout.addWidget(label)

            self.cell_containers.append(container)
            grid_layout.addWidget(container, index // 5, index % 5)

        # Собираем главный layout
        main_layout.addWidget(top_frame)
        main_layout.addWidget(grid_container)
        main_layout.addStretch()

        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def open_extended_layout(self, table_name):
        info = get_equipment_info_by_table(table_name)
        if info:
            extended_page = SecondPage(
                equipment_id=info["id"],
                table_name=table_name,
                name=info["name"],
                location=info["location"],
                parent=self
            )
            self.setCentralWidget(extended_page)
        else:
            print("Оборудование не найдено в базе.")

    def show_main_page(self):
        self.__init__()  # перезапуск главной страницы

    def open_auth_window(self):
        self.auth_window = AuthWindow(main_window_start=self)
        self.auth_window.exec()