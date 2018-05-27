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
import json
import logging
import struct
from argparse import ArgumentParser
import daiquiri
import sys

from PyQt5.QtWidgets import QApplication

from esgp.config import Configuration
from esgp.ui import MainWindow


def _read_chrome_native_message():
    logger = logging.getLogger(__file__)
    text_length_bytes = sys.stdin.read(4)
    text_length = struct.unpack("i", bytes(text_length_bytes, 'utf-8'))[0]
    text_decoded = sys.stdin.read(text_length)
    return json.loads(text_decoded)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-d', '--domain')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Enable verbose logging (default: %(default)s)')
    parser.add_argument('arg', nargs='?')

    args = parser.parse_args()

    daiquiri.setup(level=logging.DEBUG if args.verbose else logging.WARNING)
    
    url = None
    
    if (args.arg or "").startswith('chrome-extension://'):
        # started from chrome extension
        url = _read_chrome_native_message()['url']

    config = Configuration()
    config.read()

    app = QApplication(sys.argv)
    main_window = MainWindow(config, url, args)
    main_window.show()

    sys.exit(app.exec_())
