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
import hashlib
import logging

import pydenticon
import supergenpass
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QPixmap, QIntValidator, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QRadioButton, QLabel, QPushButton, \
    QMainWindow, QFrame

logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    
    def __init__(self, config, cmdargs, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.config = config
        self.initial_domain = cmdargs.domain or ''
        
        self.master_password = None
        self.identicon_label = None
        self.secret_password = None
        self.domain = None
        self.chars = None
        self.radio_md5 = None
        self.radio_sha = None

        self.build_ui()
        self.show()

    def build_ui(self):
        self.setWindowTitle('eSGP')
        # self.setMinimumSize(300, 300)
        self.setFixedWidth(250)
        
        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.build_settings_ui(vbox)

        master_pwd_layout = QHBoxLayout()

        self.master_password = QLineEdit('', self)
        self.master_password.setPlaceholderText("Master password")
        self.master_password.setEchoMode(QLineEdit.Password)
        self.master_password.installEventFilter(self)
        self.master_password.setFocus()
        master_pwd_layout.addWidget(self.master_password)

        self.identicon_label = QLabel()
        self.identicon_label.setFixedWidth(16)
        self.identicon_label.setFixedHeight(16)
        self.identicon_label.setVisible(False)
        master_pwd_layout.addWidget(self.identicon_label)
        vbox.addLayout(master_pwd_layout)
        
        self.secret_password = QLineEdit('', self)
        self.secret_password.setPlaceholderText("Secret password")
        self.secret_password.setEchoMode(QLineEdit.Password)
        self.secret_password.installEventFilter(self)
        vbox.addWidget(self.secret_password)

        self.domain = QLineEdit(self.initial_domain, self)
        self.domain.setPlaceholderText("Domain")
        self.domain.installEventFilter(self)
        vbox.addWidget(self.domain)

        self.generate_button = QPushButton()
        self.generate_button.setText("&Generate")
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self.generate_password)
        vbox.addWidget(self.generate_button)

        self.generated_password = QLineEdit('', self)
        self.generated_password.setReadOnly(True)
        self.generated_password.setVisible(False)
        vbox.addWidget(self.generated_password)
        
        self.master_password.textChanged.connect(self.options_changed)
        self.secret_password.textChanged.connect(self.options_changed)
        self.domain.textChanged.connect(self.options_changed)
        self.radio_md5.toggled.connect(self.options_changed)
        self.radio_sha.toggled.connect(self.options_changed)
        self.chars.textChanged.connect(self.options_changed)

    def build_settings_ui(self, parent):
        
        settings = QHBoxLayout()
        
        self.chars = QLineEdit(str(self.config.length), self)
        self.chars.setValidator(QIntValidator(0, 99, self))
        settings.addWidget(self.chars)
        
        algo_layout = QHBoxLayout()
        self.radio_md5 = QRadioButton("&MD5")
        self.radio_md5.setChecked(self.config.algorithm == 'md5')
        algo_layout.addWidget(self.radio_md5)

        self.radio_sha = QRadioButton("&SHA")
        self.radio_sha.setChecked(self.config.algorithm == 'sha')
        algo_layout.addWidget(self.radio_sha)

        settings.addLayout(algo_layout)
        
        save_settings_button = QPushButton('')
        save_settings_button.setIcon(QIcon.fromTheme('document-save'))
        save_settings_button.clicked.connect(self.save_settings)
        save_settings_button.setToolTip("Save current settings as defaults")
        settings.addWidget(save_settings_button)

        parent.addLayout(settings)
        
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        parent.addWidget(hr)
        

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and \
                (source is self.master_password or source is self.secret_password or source is self.domain) and \
                event.text() == '\r':
            self.generate_password()
        return super(MainWindow, self).eventFilter(source, event)

    def options_changed(self):
        self.generate_identicon()
        self.generate_button.setEnabled(bool(self.master_password.text() or "") and bool(self.domain.text() or ""))
        self.generated_password.setVisible(False)
        
        self.config.algorithm = 'md5' if self.radio_md5.isChecked() else 'sha'
        self.config.length = int(self.chars.text())

    def get_pwd(self):
        return "%s%s" % (self.master_password.text() or "", self.secret_password.text() or "")

    def generate_identicon(self):
        pwd = self.get_pwd()
        
        if not pwd:
            return
        
        for i in range(0, 4):
            h = self.get_digest()()
            h.update(pwd.encode('utf-8'))
            pwd = h.hexdigest()

        foreground = ["rgb(45,79,255)",
                      "rgb(254,180,44)",
                      "rgb(226,121,234)",
                      "rgb(30,179,253)",
                      "rgb(232,77,65)",
                      "rgb(49,203,115)",
                      "rgb(141,69,170)"]
        
        img = QPixmap()
        identicon_generator = pydenticon.Generator(5, 5, digest=self.get_digest(), foreground=foreground, background="rgba(224,224,224,0)")
        img.loadFromData(identicon_generator.generate(pwd, 16, 16))
        self.identicon_label.setVisible(True)
        self.identicon_label.setPixmap(img)

    def get_digest(self):
        if self.radio_md5.isChecked():
            return hashlib.md5
        return hashlib.sha512

    def get_digest_name(self):
        if self.radio_md5.isChecked():
            return 'md5'
        return 'sha512'
        
    def generate_password(self):
        if self.master_password.text() and self.domain.text():
            text = supergenpass.generate(self.get_pwd(), self.domain.text(), int(self.chars.text()), self.get_digest_name())
            self.generated_password.setText(text)
            self.generated_password.setVisible(True)
            self.generated_password.selectAll()
            self.generated_password.setFocus()

    def save_settings(self):
        self.config.write()
