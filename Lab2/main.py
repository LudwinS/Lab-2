import sys
from PyQt5.QtWidgets import QApplication
from ui import DataAnalyzer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = DataAnalyzer()
    ventana.show()
    sys.exit(app.exec_())
