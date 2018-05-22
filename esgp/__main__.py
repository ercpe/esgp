#!/usr/bin/env python3
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
import logging
from argparse import ArgumentParser
import daiquiri
import sys

from PyQt5.QtWidgets import QApplication

from esgp.config import Configuration
from esgp.ui import MainWindow

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-d', '--domain')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='Enable verbose logging (default: %(default)s)')

    args = parser.parse_args()

    daiquiri.setup(level=logging.DEBUG if args.verbose else logging.WARNING)

    config = Configuration()
    config.read()

    app = QApplication(sys.argv)
    main_window = MainWindow(config, args)
    main_window.show()

    sys.exit(app.exec_())
