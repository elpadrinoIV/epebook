#!/usr/bin/env python

from epebook import creator

c = creator.Creator()


c.set_files(['test2/cover.html', 'test2/chapter1.html', 'test2/chapter2.html', 'test2/epilogue.html', 'test2/coversmall.png'])

c.create('test2.epub')

