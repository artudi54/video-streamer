from PySide2 import QtCore, QtWidgets, QtGui
from vstreamer_utils import libraries
import pkg_resources


class VideoStreamerApplication(QtWidgets.QApplication):
    def __init__(self, args):
        # Qt WebEngine init fix
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

        super().__init__(args)

        # use libraries within package (vlc and mediainfo)
        libraries.init_libraries()

        # resources
        rcc_path = str(pkg_resources.resource_filename("vstreamer", "resources/resources.rcc"))
        QtCore.QResource.registerResource(rcc_path)

        # application properties
        self.setApplicationName("video_streamer")
        self.setWindowIcon(QtGui.QIcon(":/icons/Avatar.png"))