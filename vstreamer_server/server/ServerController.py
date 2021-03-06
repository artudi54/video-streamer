from PySide2 import QtCore
import dbus.service
import vstreamer_utils
from vstreamer_server import server, config, communication
from vstreamer_utils import model
from vstreamer_server.communication import ErrorHandler


class ServerController(dbus.service.Object):
    def __init__(self, session_bus):
        dbus.service.Object.__init__(self, session_bus, "/ServerController")
        QtCore.QCoreApplication.instance().aboutToQuit.connect(self._on_application_quit)
        try:
            app_name = QtCore.QCoreApplication.applicationName()
            self.object = QtCore.QObject()
            self.configuration = config.Configuration(config.get_config_directory(app_name))
            self.configuration.write_config()

            self.directory_tree = model.DirectoryTree(self.configuration.config.base_directory)
            self.communication_server = server.CommunicationServer(self.configuration.config.starting_port,
                                                                   self.directory_tree, self.object)
            self.video_server = server.VideoServer(self.configuration.config.starting_port + 1,
                                                   self.directory_tree, self.object)
        except Exception as exc:
            ErrorHandler.handle_exception(exc)
            return
        self.communication_server.error_occurred.connect(ErrorHandler.handle_error)

    def start(self):
        try:
            self.communication_server.start()
            self.video_server.start()
        except Exception as exc:
            ErrorHandler.handle_exception(exc)

    @dbus.service.method(vstreamer_utils.DBUS_NAME, in_signature='', out_signature='b')
    def set_additional_properties(self, file, title, description, image_path):
        try:
            with open(image_path, "rb") as image_file:
                image = bytearray(image_file.read())
            self.directory_tree.add_additional_properties(
                file, model.AdditionalEntryProperties(title, description, image))
            return True
        except RuntimeError as exc:
            ErrorHandler.handle_error(vstreamer_utils.Error(str(exc), vstreamer_utils.ErrorLevel.ERROR))
            return False

    def _on_application_quit(self):
        try:
            self.configuration.write_config()
            self.directory_tree.store_info()
            vstreamer_utils.log_info("Application is closing")
        except Exception as exc:
            ErrorHandler.handle_exception(exc)
