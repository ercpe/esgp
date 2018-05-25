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
        self.algorithm = 'MD5'
        self.length = 10
        self.domain_settings = []
    
    def read(self):
        
        parser = ConfigParser()
        parser.read(PATH)
        
        if parser.has_section('defaults'):
            self.algorithm = parser.get('defaults', 'algorithm', fallback=self.algorithm)
            self.length = int(parser.get('defaults', 'length', fallback=self.length))
    
        for section in parser.sections():
            if section == "defaults":
                continue
            
            self.domain_settings.append({
                'domain': section,
                'algorithm': parser.get(section, 'algorithm', fallback=self.algorithm),
                'length': parser.get(section, 'length', fallback=self.length)
            })

    def write(self):
        
        parser = ConfigParser()
        
        parser.add_section('defaults')
        parser.set('defaults', 'algorithm', self.algorithm)
        parser.set('defaults', 'length', str(self.length))

        for settings in self.domain_settings:
            domain = settings['domain']
            if not domain:
                continue
            parser.add_section(domain)
            parser.set(domain, 'algorithm', settings['algorithm'])
            parser.set(domain, 'length', str(settings['length']))
        
        with open(PATH, 'w') as o:
            parser.write(o)
    
    def get_domain_settings(self, domain):
        for d in self.domain_settings:
            if d.get('domain', '') == domain:
                return d
