# -*- coding: utf-8 -*-
# Copyright (C) 2018 Johann Schmitz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QModelIndex, QRegExp
from PyQt5.QtGui import QIntValidator, QRegExpValidator
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFrame, QLabel, QTableView, QLineEdit, \
    QStyledItemDelegate, QPushButton, QComboBox, QHBoxLayout, QTableWidget, QAbstractItemView, QHeaderView


class DomainSettingsTableModel(QAbstractTableModel):
    
    properties = ['domain', 'length', 'algorithm']
    
    def __init__(self, config, parent):
        self._data = config.domain_settings
        self.default_length = config.length
        self.default_algorithm = config.algorithm
        super(DomainSettingsTableModel, self).__init__(parent)

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)
    
    def columnCount(self, parent=None, *args, **kwargs):
        return 3
    
    def data(self, index, role=None):
        if not index.isValid() or role not in (Qt.DisplayRole, Qt.EditRole):
            return QVariant()

        value = self._data[index.row()][self.properties[index.column()]]
        if index.column() == 2 and role == Qt.EditRole:
            value = value.upper()
        return value

    def headerData(self, col, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if col == 0:
                return "Domain"
            if col == 1:
                return "Length"
            if col == 2:
                return "Algorithm"
            return ""

    def setData(self, index, value, role=None):
        if index.isValid() and 0 <= index.row() <= self.rowCount():
            self._data[index.row()][self.properties[index.column()]] = value
            return True
        return False

    def flags(self, index):
        defaultFlags = super(DomainSettingsTableModel, self).flags(index)
        if index.isValid():
            return defaultFlags | Qt.ItemIsEditable
        return defaultFlags

    def insertRow(self, p_int, parent=None, *args, **kwargs):
        self.beginInsertRows(QModelIndex(), p_int, p_int)
        self._data.insert(p_int, {
            'domain': '',
            'length': self.default_length,
            'algorithm': self.default_algorithm
        })
        self.endInsertRows()

    def removeRow(self, p_int, parent=None, *args, **kwargs):
        self.beginRemoveRows(QModelIndex(), p_int, p_int)
        self._data.remove(self._data[p_int])
        self.endRemoveRows()


class SettingsItemDelegate(QStyledItemDelegate):

    def createEditor(self, widget, option, index):
        if not index.isValid():
            return None

        if index.column() == 0:
            editor = QLineEdit(widget)
            editor.setValidator(QRegExpValidator(QRegExp('.+'), self))
            editor.setText(index.model().data(index, Qt.EditRole))
            return editor

        if index.column() == 1:
            editor = QLineEdit(widget)
            editor.setValidator(QIntValidator(0, 99, self))
            editor.setText(str(index.model().data(index, Qt.EditRole)))
            return editor

        if index.column() == 2:
            editor = QComboBox(parent=widget)
            editor.addItem("MD5")
            editor.addItem("SHA")
            editor.setCurrentIndex(editor.findText(index.model().data(index, Qt.EditRole)))
            return editor

        return super(SettingsItemDelegate, self).createEditor(widget, option, index)


class SettingsDialog(QDialog):
    
    def __init__(self, config, *args, **kwargs):
        self.config = config
        super(SettingsDialog, self).__init__(*args, **kwargs)
        self.domain_settings_model = None
        self.del_button = None
        self.build_ui()
    
    def build_ui(self):
        self.setWindowTitle("Advanced settings")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.build_domain_settings_ui())
        
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_and_close)
        layout.addWidget(save_button)
        
    def build_domain_settings_ui(self):
        # per-domain settings
        domain_settings_layout = QVBoxLayout()
        domain_settings_layout.addWidget(QLabel("Per-domain settings"))

        self.domain_settings_model = DomainSettingsTableModel(self.config, self)

        self.domain_settings_table = QTableView()
        self.domain_settings_table.setItemDelegate(SettingsItemDelegate())
        self.domain_settings_table.setModel(self.domain_settings_model)
        self.domain_settings_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.domain_settings_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.domain_settings_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.domain_settings_table.clicked.connect(self.selected)
        domain_settings_layout.addWidget(self.domain_settings_table)
        
        add_button = QPushButton('+')
        add_button.clicked.connect(self.add_domain_settings_row)
        self.del_button = QPushButton('-')
        self.del_button.clicked.connect(self.delete_domain_settings_row)
        self.del_button.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(add_button)
        hbox.addWidget(self.del_button)
        domain_settings_layout.addLayout(hbox)

        domain_settings_frame = QFrame(self)
        domain_settings_frame.setLayout(domain_settings_layout)
        return domain_settings_frame

    def add_domain_settings_row(self):
        self.domain_settings_model.insertRow(self.domain_settings_model.rowCount())

    def delete_domain_settings_row(self, *args):
        selected = self.domain_settings_table.selectedIndexes()
        if selected:
            rows = set([i.row() for i in selected])
            for row in rows:
                self.domain_settings_model.removeRow(row)

    def save_and_close(self):
        self.config.write()
        self.close()

    def selected(self, index):
        self.del_button.setEnabled(index.isValid())
