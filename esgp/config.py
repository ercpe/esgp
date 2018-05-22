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

import os
from configparser import ConfigParser

PATH = os.path.abspath(os.path.expanduser("~/.esgp.cfg"))


class Configuration(object):
    
    def __init__(self):
        self.algorithm = 'md5'
        self.length = 10
    
    def read(self):
        
        parser = ConfigParser()
        parser.read(PATH)
        
        if parser.has_section('esgp'):
            self.algorithm = parser.get('esgp', 'algorithm', fallback=self.algorithm)
            self.length = int(parser.get('esgp', 'length', fallback=self.length))
    
    def write(self):
        
        parser = ConfigParser()
        
        parser.add_section('esgp')
        parser.set('esgp', 'algorithm', self.algorithm)
        parser.set('esgp', 'length', str(self.length))
        
        with open(PATH, 'w') as o:
            parser.write(o)
