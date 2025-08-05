from Windows.Show_tab import ShowTab
from PyQt5.QtWidgets import QApplication
import sys
import os
os.environ["QT_LOGGING_RULES"] = "qt.qpa.*=false"
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ShowTab()
    widget.show()
    sys.exit(app.exec_())
