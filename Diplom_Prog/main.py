from PyQt6.QtWidgets import QApplication
import sys
from ui.main_window import MainWindow
from ui.main_window_start import MainWindowStart
from ui.registr_eq import RegistrationWindow
from ui.Auth import AuthWindow
from ui.Registr_user import RegistrationWindow_U
#from ui.Registr_user import RegistrationWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowStart()
    window.show()
    sys.exit(app.exec())