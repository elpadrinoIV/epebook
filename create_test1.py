#!/usr/bin/env python

from epebook import creator

c = creator.Creator()


#c.set_files(['test1/index.html'])

c.set_files([{ 'src': 'test1/index.html', 'nav_label': 'Just a test', 'class': 'chapter'}])
c.create('test1.epub')
