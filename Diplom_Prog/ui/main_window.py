from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QFrame, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt

from ui.machine_window import MachineWindow
from ui.Registr_user import RegistrationWindow_U
from ui.registr_eq import RegistrationWindow
from ui.Extended_Layout import SecondPage
from ui.main_window_start import MainWindowStart

from db.database import get_machine_tables
from db.database import get_equipment_info_by_table

#container.setStyleSheet("border: 1px dashed gray;")  # Добавлено отображение ячеек

class MainWindow(QMainWindow):
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

        # Кнопки регистрации
        register_user_button = QPushButton("Зарегистрировать пользователя")
        register_user_button.setFixedSize(200, 30)
        register_user_button.setStyleSheet("""
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

        register_equipment_button = QPushButton("Зарегистрировать оборудование")
        register_equipment_button.setFixedSize(220, 30)
        register_equipment_button.setStyleSheet("""
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

        auth_button = QPushButton("Выйти из аккаунта")#выйти из аккаунта или авторизоваться
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

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(register_user_button)
        top_layout.addWidget(register_equipment_button)
        top_layout.addWidget(auth_button)

        auth_button.clicked.connect(self.open_start_window)
        register_user_button.clicked.connect(self.open_register_user_window)
        register_equipment_button.clicked.connect(self.open_register_equipment_window)

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
            #container.setStyleSheet("border: 1px dashed gray;")  # Добавлено отображение ячеек
            container.setLayout(cell_layout)
            container.setFixedSize(200, 250)

            if index < len(tables):
                window = MachineWindow(table_name=tables[index])
                window.clicked.connect(self.open_extended_layout)
                cell_layout.addWidget(window)
            elif index == len(tables):
                label = QLabel("Нет данных")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setStyleSheet("color: #9E9E9E; font-style: italic;")
                cell_layout.addWidget(label)

            self.cell_containers.append(container)
            grid_layout.addWidget(container, index // 5, index % 5)

        main_layout.addWidget(top_frame)
        main_layout.addWidget(grid_container)
        main_layout.addStretch()  # Подталкивает сетку вверх

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

    def open_register_user_window(self):
        self.user_window = RegistrationWindow_U(parent=self)
        self.user_window.show()

    def open_register_equipment_window(self):
        self.eq_window = RegistrationWindow(parent=self)
        # Устанавливаем флаг независимого окна
        self.eq_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.eq_window.setWindowFlag(Qt.WindowType.Window)
        print("Открываем окно регистрации оборудования")
        self.eq_window.show()

    def open_start_window(self):
        # Создаем новое окно
        self.start_window = MainWindowStart()

        # Устанавливаем флаги окна (если нужно)
        self.start_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.start_window.setWindowFlag(Qt.WindowType.Window)

        # Закрываем текущее окно
        self.close()

        # Показываем новое окно
        print("Открываем стартовое окно")
        self.start_window.show()

    def show_main_page(self):
        #self.__init__()  # перезапуск главной страницы
        #self.show()
        main_widget = MainWindow()  # Замени на реальный главный виджет
        self.setCentralWidget(main_widget)