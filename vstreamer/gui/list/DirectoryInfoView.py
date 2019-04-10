import math
from PySide2 import QtWidgets, QtGui, QtCore
from vstreamer.gui import list
import vstreamer_utils
from vstreamer_utils import model


class DirectoryInfoItemModel(QtCore.QAbstractTableModel):
    def __init__(self, directory_info, parent):
        super().__init__(parent)
        self._column_count = 0
        self._directory_info = directory_info

    def set_column_count(self, column_count):
        if column_count != self._column_count:
            self.beginResetModel()
            self._column_count = column_count
            self.endResetModel()

    def set_directory_info(self, directory_info):
        self.beginResetModel()
        self._directory_info = directory_info
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self._directory_info is None or self._column_count == 0:
            return 0
        return math.ceil(len(self._directory_info.entries) / self._column_count)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self._directory_info is None:
            return 0
        return self._column_count

    def flags(self, index):
        array_idx = self._array_idx(index)
        if array_idx is None or array_idx >= len(self._directory_info.entries):
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def data(self, index, role=QtCore.Qt.DisplayRole):
        array_idx = self._array_idx(index)
        if array_idx is None or array_idx >= len(self._directory_info.entries):
            return None
        if role == QtCore.Qt.DisplayRole:
            return self._directory_info.entries[array_idx]
        if role == QtCore.Qt.ToolTipRole:
            return self._directory_info.entries[array_idx].filename
        if role == QtCore.Qt.SizeHintRole:
            return list.FileEntryWidget.FIXED_SIZE
        return None

    def headerData(self, section, orientation, role=...):
        return None

    def _array_idx(self, index):
        if not index.isValid():
            return None
        return index.row() * self._column_count + index.column()


class ImageDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent):
        super().__init__(parent)

    def paint(self, painter, option, index):
        if not index.isValid() or index.data() is None:
            painter.save()
            painter.eraseRect(option.rect)
            painter.restore()
            return
        widget = list.FileEntryWidget(index.data())
        painter.save()
        painter.eraseRect(option.rect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if option.state & QtWidgets.QStyle.State_Selected != 0:
            rounded_rect = option.rect.translated(1, 1)
            rounded_rect.setWidth(rounded_rect.width() - 2)
            rounded_rect.setHeight(rounded_rect.height() - 2)
            path = QtGui.QPainterPath()
            path.addRoundedRect(rounded_rect, 3, 3)
            painter.setPen(QtGui.QPen(option.palette.highlight().color(), 2))
            painter.fillPath(path, option.palette.highlight().color())
            painter.drawPath(path)
        if option.state & QtWidgets.QStyle.State_Selected != 0:
            focus = QtWidgets.QStyleOptionFocusRect()
            focus.rect = option.rect
            QtWidgets.QApplication.style().drawPrimitive(QtWidgets.QStyle.PE_FrameFocusRect, focus, painter)
        widget.render(painter, painter.deviceTransform().map(option.rect.topLeft()),
                      renderFlags=QtWidgets.QWidget.DrawChildren)
        painter.restore()


class DirectoryInfoView(QtWidgets.QWidget):
    # TODO
    path_requested = QtCore.Signal(str)

    def __init__(self, directory_info=None, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("DirectoryInfoView.ui", self)
        self.table_view.setModel(DirectoryInfoItemModel(directory_info, self))
        self.table_view.setItemDelegate(ImageDelegate(self.table_view))
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setDefaultSectionSize(list.FileEntryWidget.FIXED_SIZE.width())
        self.table_view.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.table_view.verticalHeader().setDefaultSectionSize(list.FileEntryWidget.FIXED_SIZE.height())

    def set_directory_info(self, directory_info):
        self.table_view.model().set_directory_info(directory_info)

    def resizeEvent(self, event):
        column_count = self.table_view.size().width() // list.FileEntryWidget.FIXED_SIZE.width()
        self.table_view.model().set_column_count(column_count)
        super().resizeEvent(event)
