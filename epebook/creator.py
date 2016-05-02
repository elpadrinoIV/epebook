#! /usr/bin/env python

import os
import re
import shutil
from lxml import etree
import opf
import ncx

class Creator():
    def __init__(self):
        self.root_dir = 'ebook_root'
        self.original_files = []
        self.final_files = []

    def set_files(self, files):
        self.original_files = files

    def create(self, path):
        self.create_basic_structure()
        self.copy_files()
        self.create_ncx()
        self.create_opf()


    def create_basic_structure(self):
        # Basic dir structure
        if os.path.exists(self.root_dir):
            shutil.rmtree(self.root_dir)

        os.makedirs(self.root_dir)
        os.makedirs(self.root_dir + '/OEBPS')
        os.makedirs(self.root_dir + '/META-INF')

        os.makedirs(self.root_dir + '/OEBPS/images')
        os.makedirs(self.root_dir + '/OEBPS/text')
        os.makedirs(self.root_dir + '/OEBPS/css')

        # mimetype file is fixed
        mimetype = open(self.root_dir + '/mimetype', 'w')
        mimetype.write('application/epub+zip')
        mimetype.close()

        # container.xml file is also fixed
        container = open(self.root_dir + '/META-INF/container.xml', 'w')
        container.write('''<?xml version="1.0"?>
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
            <rootfile full-path="OEBPS/ebook.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
</container>''')

        container.close()


    def copy_files(self):
        FILENAME_RE= re.compile('(.*/)?([^/]+)')
        IMAGES_RE = re.compile('(\.jpg|\.gif|\.png|\.svg)$', re.I)
        TEXT_RE = re.compile('(\.html|\.xhtml|\.htm)$', re.I)
        CSS_RE = re.compile('\.css$', re.I)
        imgs_counter = 1
        text_counter = 1
        css_counter = 1
        for file in self.original_files:
            final_file = self.__file_with_metadata(file)
            filename = re.sub(FILENAME_RE, r'\2', final_file['src'])
            if IMAGES_RE.search(filename):
                shutil.copy(final_file['src'], self.root_dir + '/OEBPS/images/')
                final_file['src'] = 'OEBPS/images/' + filename
                final_file['id'] = "img_%s" % imgs_counter
                self.final_files.append(final_file)
                imgs_counter += 1
            elif TEXT_RE.search(filename):
                shutil.copy(final_file['src'], self.root_dir + '/OEBPS/text/')
                final_file['src'] = 'OEBPS/text/' + filename
                final_file['navigation'] = True
                final_file['id'] = "text_%s" % text_counter
                self.final_files.append(final_file)
                text_counter += 1
            elif CSS_RE.search(filename):
                shutil.copy(final_file['src'], self.root_dir + '/OEBPS/css/')
                final_file['src'] = 'OEBPS/css/' + filename
                final_file['id'] = "css_%s" % css_counter
                self.final_files.append(final_file)
                css_counter += 1

        self.final_files.append({'src': 'OEBPS/toc.ncx', 'id': 'ncx', 'navigation': False})

    def create_opf(self):
        opf_creator = opf.OPF()
        opf_creator.set_files(self.final_files)
        opf_creator.write_file(self.root_dir + '/OEBPS/book.opf')

    def create_ncx(self):
        ncx_creator = ncx.NCX()
        ncx_creator.set_files(self.final_files)
        ncx_creator.write_file(self.root_dir + '/OEBPS/toc.ncx')

    def __file_with_metadata(self, file):
        final_file = {'navigation': False}
        if type(file) is str:
            final_file['src'] = file
            final_file['class'] = 'other'
            final_file['nav_label'] = 'TODO: GUESS NAV LABEL'
        elif type(file) is dict:
            final_file['src'] = file['src']
            if 'class' in file:
                final_file['class'] = file['class']
            else:
                final_file['class'] = 'other'

            if 'nav_label' in file:
                final_file['nav_label'] = file['nav_label']
            else:
                final_file['nav_label'] = 'TODO: GUESS NAV LABEL'

        return final_file
