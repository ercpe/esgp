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
from io import BytesIO
from urllib.parse import urlparse

import supergenpass
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QPixmap, QIntValidator, QIcon
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QHBoxLayout, QRadioButton, QLabel, QPushButton, \
    QFrame, QDialog, QApplication

from esgp.settings import SettingsDialog
from pydenticon5 import Pydenticon5

logger = logging.getLogger(__name__)


class MainWindow(QDialog):
    
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
        self.set_default_settings()
        self.show()

    def build_ui(self):
        self.setWindowTitle('eSGP')
        self.setFixedWidth(250)

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self.build_settings_ui(vbox)

        master_pwd_layout = QHBoxLayout()

        self.master_password = QLineEdit('', self)
        self.master_password.setPlaceholderText("Master password")
        self.master_password.setEchoMode(QLineEdit.Password)
        self.master_password.textChanged.connect(self.options_changed)
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
        self.secret_password.textChanged.connect(self.options_changed)
        self.secret_password.installEventFilter(self)
        vbox.addWidget(self.secret_password)

        self.domain = QLineEdit(self.initial_domain, self)
        self.domain.setPlaceholderText("Domain")
        self.domain.textChanged.connect(self.options_changed)
        self.domain.textChanged.connect(self.domain_changed)
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

    def build_settings_ui(self, parent):
        
        settings = QHBoxLayout()
        
        self.chars = QLineEdit('', self)
        self.chars.setValidator(QIntValidator(0, 99, self))
        self.chars.textChanged.connect(self.options_changed)
        self.chars.installEventFilter(self)
        settings.addWidget(self.chars)
        
        algo_layout = QHBoxLayout()
        self.radio_md5 = QRadioButton("&MD5")
        self.radio_md5.toggled.connect(self.options_changed)
        algo_layout.addWidget(self.radio_md5)

        self.radio_sha = QRadioButton("&SHA")
        self.radio_sha.toggled.connect(self.options_changed)
        algo_layout.addWidget(self.radio_sha)

        settings.addLayout(algo_layout)
        
        # see https://standards.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        save_settings_button = QPushButton('')
        save_settings_button.setIcon(QIcon.fromTheme('document-save'))
        save_settings_button.clicked.connect(self.save_settings)
        save_settings_button.setToolTip("Save current settings as defaults")
        settings.addWidget(save_settings_button)

        advanced_settings_button = QPushButton('')
        advanced_settings_button.setIcon(QIcon.fromTheme('applications-other'))
        advanced_settings_button.clicked.connect(self.advanced_settings)
        advanced_settings_button.setToolTip("Show advanced settings")
        settings.addWidget(advanced_settings_button)

        parent.addLayout(settings)
        
        hr = QFrame()
        hr.setFrameShape(QFrame.HLine)
        parent.addWidget(hr)

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and event.text() == '\r'\
                and source in (self.master_password, self.secret_password, self.domain, self.chars):
            self.generate_password()
        return super(MainWindow, self).eventFilter(source, event)

    def options_changed(self):
        self.generate_identicon()
        self.generate_button.setEnabled(bool(self.master_password.text() or "") and bool(self.domain.text() or ""))
        self.generated_password.setVisible(False)
        
    def domain_changed(self, text):
        if QApplication.clipboard().text() == text and text:
            self.domain_pasted(text)
    
        domain_settings = self.config.get_domain_settings(self.domain.text())
        if domain_settings:
            self.chars.setText(str(domain_settings['length']))
            self.radio_md5.setChecked(domain_settings['algorithm'] == 'MD5')
            self.radio_sha.setChecked(domain_settings['algorithm'] == 'SHA')
        else:
            self.set_default_settings()

    def set_default_settings(self):
        self.chars.setText(str(self.config.length))
        self.radio_md5.setChecked(self.config.algorithm == 'MD5')
        self.radio_sha.setChecked(self.config.algorithm == 'SHA')

    def domain_pasted(self, text):
        try:
            chunks = urlparse(text)
            if chunks.netloc and chunks.netloc != text:
                self.domain.setText(chunks.netloc)
        except:
            pass

    def get_pwd(self):
        return "%s%s" % (self.master_password.text() or "", self.secret_password.text() or "")

    def generate_identicon(self):
        pwd = self.get_pwd()
        
        if not pwd:
            return
        
        s = pwd
        for i in range(0, 5):
            h = self.get_digest()()
            h.update(s.encode('utf-8'))
            s = h.hexdigest()

        img = QPixmap()
        identicon = Pydenticon5().draw(s, 16)
        img_bytes = BytesIO()
        identicon.save(img_bytes, 'PNG')
        img.loadFromData(img_bytes.getvalue())
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
        self.config.algorithm = 'MD5' if self.radio_md5.isChecked() else 'SHA'
        self.config.length = int(self.chars.text())
        self.config.write()

    def advanced_settings(self):
        settings_dialog = SettingsDialog(config=self.config)
        settings_dialog.exec_()
