import math
from PySide2 import QtWidgets, QtGui, QtCore
from PySide2.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy

from vstreamer.client import list
import vstreamer_utils
from vstreamer.client.list import FileEntryVM


class DirectoryInfoItemModel(QtCore.QAbstractTableModel):
    def __init__(self, file_entries, parent):
        super().__init__(parent)
        self._column_count = 0
        self._file_entries = file_entries

    def set_column_count(self, column_count):
        if column_count != self._column_count:
            self.beginResetModel()
            self._column_count = column_count
            self.endResetModel()

    def set_entries(self, file_entries):
        self.beginResetModel()
        self._file_entries = file_entries
        self.endResetModel()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self._file_entries is None or self._column_count == 0:
            return 0
        return math.ceil(len(self._file_entries) / self._column_count)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if self._file_entries is None:
            return 0
        return self._column_count

    def flags(self, index):
        array_idx = self._array_idx(index)
        if array_idx is None or array_idx >= len(self._file_entries):
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled

    def data(self, index, role=QtCore.Qt.DisplayRole):
        array_idx = self._array_idx(index)
        if array_idx is None or array_idx >= len(self._file_entries):
            return None
        if role == QtCore.Qt.DisplayRole:
            return self._file_entries[array_idx]
        if role == QtCore.Qt.ToolTipRole:
            return self._file_entries[array_idx].filename
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
            QtWidgets.QApplication.style().drawPrimitive(QtWidgets.QStyle.PE_FrameFocusRect, focus,
                                                         painter)
        widget.render(painter, painter.deviceTransform().map(option.rect.topLeft()),
                      renderFlags=QtWidgets.QWidget.DrawChildren)
        painter.restore()


class DirectoryInfoView(QtWidgets.QWidget):
    path_requested = QtCore.Signal(str)  # TODO - selection

    def __init__(self, directory_info=None, parent=None):
        super().__init__(parent)
        vstreamer_utils.load_ui("DirectoryInfoView.ui", self)
        self.table_view.setModel(DirectoryInfoItemModel(directory_info, self))
        self.table_view.setItemDelegate(ImageDelegate(self.table_view))
        self.table_view.resizeColumnsToContents()
        self.table_view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.table_view.horizontalHeader().setDefaultSectionSize(
            list.FileEntryWidget.FIXED_SIZE.width())
        self.table_view.verticalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeToContents)
        self.table_view.verticalHeader().setDefaultSectionSize(
            list.FileEntryWidget.FIXED_SIZE.height())
        self.setup_properties(FileEntryVM.FileEntryVM("testowy folder 1", False, dict(
            prop1="test1",
            prop2="test2"
        )))

    def set_entries(self, directory_info):
        self.table_view.model().set_entries(directory_info)

    def resizeEvent(self, event):
        column_count = self.table_view.size().width() // list.FileEntryWidget.FIXED_SIZE.width()
        self.table_view.model().set_column_count(column_count)
        super().resizeEvent(event)

    def setup_properties(self, fileEntryVM: FileEntryVM):
        # todo clear layout before adding new widget
        # self.properties_widget_layout.remove
        for key, value in fileEntryVM.properties.items():
            line = QWidget()
            vstreamer_utils.load_ui("properties_item.ui", line)
            line.left_label.setText(key)
            line.right_label.setText(value)
            self.properties_widget_layout.addWidget(line)
        # todo not working
        # self.properties_widget_layout.addStretch(1)