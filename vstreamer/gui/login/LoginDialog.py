from PySide2 import QtWidgets, QtCore
import vstreamer_utils


class LoginDialog(QtWidgets.QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("LoginDialog.ui", self)

        self.controller = controller
        self.controller.view = self

        self.button.clicked.connect(self.controller.accept_server)

