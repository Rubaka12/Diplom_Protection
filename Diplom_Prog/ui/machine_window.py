from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from db.database import get_latest_data, get_equipment_name, get_title_graph
from resources.config import PARAM_LIMITS

class MachineWindow(QFrame):
    clicked = pyqtSignal(str)  # передаём имя таблицы

    def __init__(self, table_name):
        super().__init__()
        self.table_name = table_name
        # на подпись
        # для поиска
        # для словаря
        self.params_L = get_title_graph(table_name)[0]
        self.params = get_title_graph(table_name)[1]
        self.PARAM_LIM = get_title_graph(table_name)[2]
        #self.params = ['A1', 'A2', 'A3']
        self.current_param_index = 0

        self.setStyleSheet("border: 2px solid #4CAF50; border-radius: 5px; background-color: white;")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.status_label = QLabel("Status: OK")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.param_label = QLabel("Показатель: A1")
        self.param_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.param_label)

        self.figure = Figure(figsize=(2, 1.5))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.canvas)

        # 👇 Подключаем клик по графику
        self.canvas.mpl_connect("button_press_event", self.on_canvas_clicked)

        equipment_name, equipment_location = get_equipment_name(self.table_name)
        self.name_label = QLabel(f"Оборудование: {equipment_name}")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.name_label)

        self.info_label = QLabel(f"Местоположение: {equipment_location}")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.info_label)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(5000)

        self.draw_initial_graph()
        self.update_graph()

    def mousePressEvent(self, event):
        # 👇 Клик по всей области MachineWindow
        self.clicked.emit(self.table_name)

    def on_canvas_clicked(self, event):
        # 👇 Клик по графику (canvas)
        if event.button == 1:  # Левая кнопка мыши
            self.clicked.emit(self.table_name)

    def draw_initial_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot([], color='#4CAF50')
        ax.set_ylim(0, 300)
        ax.set_facecolor('#FAFAFA')
        ax.tick_params(axis='both', labelsize=7)
        for label in ax.get_yticklabels():
            label.set_rotation(45)
        ax.set_xlabel("t", fontsize=8)
        ax.set_ylabel("V", fontsize=8)
        self.figure.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.2)
        self.canvas.draw()

    def update_graph(self):
        param = self.params[self.current_param_index]
        #print("param", param)
        param_L = self.params_L[self.current_param_index]  # для подписи
        #print("param_L", param_L)
        values = get_latest_data(self.table_name, param)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(values, color='#4CAF50')
        ax.set_ylim(0, 300)
        ax.set_facecolor('#FAFAFA')
        ax.tick_params(axis='both', labelsize=7)
        for label in ax.get_yticklabels():
            label.set_rotation(45)
        ax.set_xlabel("t", fontsize=8)
        ax.set_ylabel("V", fontsize=8)
        self.figure.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.2)
        self.canvas.draw()

        self.update_status(values, param, self.PARAM_LIM)
        self.param_label.setText(f"Показатель: {param_L}")
        self.current_param_index = (self.current_param_index + 1) % len(self.params)
        #print("param", param)
        #print("len(param)", len(param))
        #print("Отслеживание", self.current_param_index)

    def update_status(self, values, param, PARAM_LIM):
        #print("values", values[0], type(values))
       # print("param", param, type(param))
        #print("PARAM_LIMITS.get(param, (None, None))", PARAM_LIM,type(PARAM_LIM.get(param, (None, None))))
        low, high = PARAM_LIM.get(param, (None, None))
        #print("low", low, type(low))
        #print("high", high, type(high))
        last_value = values[-1] if values else None
        is_alert = last_value is not None and (last_value < low or last_value > high)

        if is_alert:
            self.setStyleSheet("border: 2px solid #F44336; border-radius: 5px; background-color: white;")
            self.status_label.setText("Статус: Not OK")
            self.status_label.setStyleSheet("color: #F44336;")
        else:
            self.setStyleSheet("border: 2px solid #4CAF50; border-radius: 5px; background-color: white;")
            self.status_label.setText("Статус: OK")
            self.status_label.setStyleSheet("color: #4CAF50;")