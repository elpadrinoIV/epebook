#! /usr/bin/env python

import datetime
import os
import random
import re
import shutil
import zipfile
from lxml import etree
from lxml import html

import opf
import ncx

class Creator():
    FILENAME_RE= re.compile('(.*/)?([^/]+)')
    IMAGES_RE = re.compile('(\.jpg|\.gif|\.png|\.svg)$', re.I)
    TEXT_RE = re.compile('(\.html|\.xhtml|\.htm)$', re.I)
    CSS_RE = re.compile('\.css$', re.I)

    BASE_XHTML_NS = 'http://www.w3.org/1999/xhtml'

    BASE_XHTML = "{%s}" % BASE_XHTML_NS

    NSMAP = {None : BASE_XHTML_NS}

    def __init__(self):
        self.root_dir = 'ebook_root'
        self.original_files = []
        self.final_files = []
        self.title = "NoTitle"
        self.authors = []
        self.contributors = []
        self.rights = None
        self.date = None
        self.description = None
        self.id = None
        self.id_type = None
        self.publisher = None
        self.cover = None
        self.final_cover_image = None
        self.final_cover_page = None
        self.toc_page = None
        self.create_toc = True

    def set_files(self, files):
        self.original_files = files

    def set_cover(self, cover):
        self.cover = cover

    def set_title(self, title):
        self.title = title

    def set_language(self, language):
        self.language = language

    def set_id(self, id, id_type):
        self.id = id
        self.id_type = id_type

    def add_author(self, author):
        self.authors.append(author)

    def add_contributor(self, contributor):
        self.contributors.append(contributor)

    def set_rights(self, rights):
        self.rights = rights

    def set_date(self, date):
        self.date = date

    def set_description(self, description):
        self.description = description

    def set_publisher(self, publisher):
        self.publisher = publisher

    def create(self, path, create_toc = True):
        self.create_toc = create_toc
        self.create_basic_structure()
        self.copy_files()

        if self.id is None:
            id = datetime.datetime.now().isoformat() + '-' + str(random.randint(0, 1000000))
            self.id = id
            self.id_type = 'DOI'

        self.create_ncx()
        self.create_opf()

        epub = zipfile.ZipFile(path, 'w')
        epub.writestr('mimetype', 'application/epub+zip')
        epub.write(self.root_dir + '/META-INF/container.xml', 'META-INF/container.xml')
        epub.write(self.root_dir + '/OEBPS/book.opf', 'OEBPS/book.opf')
        epub.write(self.root_dir + '/OEBPS/toc.ncx', 'OEBPS/toc.ncx')

        for file in os.listdir(self.root_dir + '/OEBPS/text'):
            epub.write(self.root_dir + '/OEBPS/text/' + file, 'OEBPS/text/' + file)

        for file in os.listdir(self.root_dir + '/OEBPS/images'):
            epub.write(self.root_dir + '/OEBPS/images/' + file, 'OEBPS/images/' + file)

        for file in os.listdir(self.root_dir + '/OEBPS/css'):
            epub.write(self.root_dir + '/OEBPS/css/' + file, 'OEBPS/css/' + file)

        epub.close()



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
            <rootfile full-path="OEBPS/book.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
</container>''')

        container.close()


    def copy_files(self):
        imgs_counter = 1
        text_counter = 1
        css_counter = 1
        if self.cover is not None:
            filename = re.sub(self.FILENAME_RE, r'\2', self.cover)
            shutil.copy(self.cover, self.root_dir + '/OEBPS/images/')
            self.final_cover_image = 'images/' + filename
            self.final_cover_page = self.__create_cover_page()

        for file in self.original_files:
            final_file = self.__file_with_metadata(file)
            filename = re.sub(self.FILENAME_RE, r'\2', final_file['src'])
            if self.IMAGES_RE.search(filename):
                shutil.copy(final_file['src'], self.root_dir + '/OEBPS/images/')
                final_file['src'] = 'images/' + filename
                final_file['id'] = "img_%s" % imgs_counter
                self.final_files.append(final_file)
                imgs_counter += 1
            elif self.TEXT_RE.search(filename):
                shutil.copy(final_file['src'], self.root_dir + '/OEBPS/text/')
                final_file['src'] = 'text/' + filename
                final_file['navigation'] = True
                final_file['id'] = "text_%s" % text_counter
                self.final_files.append(final_file)
                text_counter += 1
            elif self.CSS_RE.search(filename):
                shutil.copy(final_file['src'], self.root_dir + '/OEBPS/css/')
                final_file['src'] = 'css/' + filename
                final_file['id'] = "css_%s" % css_counter
                self.final_files.append(final_file)
                css_counter += 1

        if self.create_toc:
            self.toc_page = self.__create_toc_page()

        self.final_files.append({'src': 'toc.ncx', 'id': 'ncx', 'navigation': False})

    def create_opf(self):
        opf_creator = opf.OPF()
        opf_creator.set_title(self.title)
        opf_creator.add_author(self.authors)
        opf_creator.add_contributor(self.contributors)
        opf_creator.set_rights(self.rights)
        opf_creator.set_date(self.date)
        opf_creator.set_description(self.description)
        opf_creator.set_id(self.id, self.id_type)
        opf_creator.set_publisher(self.publisher)

        opf_creator.set_cover(self.final_cover_image, self.final_cover_page)
        opf_creator.set_toc_page(self.toc_page)
        opf_creator.set_files(self.final_files)
        opf_creator.write_file(self.root_dir + '/OEBPS/book.opf')

    def create_ncx(self):
        ncx_creator = ncx.NCX()
        ncx_creator.set_title(self.title)
        if len(self.authors) > 0:
            ncx_creator.set_author(self.authors[0])
        ncx_creator.set_id(self.id)

        ncx_creator.set_files(self.final_files)
        ncx_creator.write_file(self.root_dir + '/OEBPS/toc.ncx')

    def __file_with_metadata(self, file):
        final_file = {'navigation': False}
        if type(file) is str:
            final_file['src'] = file
            final_file['class'] = 'other'
            final_file['nav_label'] = self.__guess_nav_label(final_file['src'])
        elif type(file) is dict:
            final_file['src'] = file['src']
            if 'class' in file:
                final_file['class'] = file['class']
            else:
                final_file['class'] = 'other'

            if 'nav_label' in file:
                final_file['nav_label'] = file['nav_label']
            else:
                final_file['nav_label'] = self.__guess_nav_label(final_file['src'])

        return final_file

    def __guess_nav_label(self, file):
        filename = re.sub(self.FILENAME_RE, r'\2', file)
        nav_label = filename
        if self.TEXT_RE.search(file):
            tree = html.parse(file)
            title = tree.xpath('/html/head/title')
            if len(title) == 1:
                nav_label = title[0].text
            else:
                for h in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    headers = tree.xpath('/html/body/' + h)
                    if len(headers == 1):
                        nav_label = headers[0].text
                        break


        return nav_label

    def __create_basic_page(self):
        root = etree.Element(self.BASE_XHTML + "html")
        root.attrib['xmlns'] = self.BASE_XHTML_NS

        head = etree.SubElement(root, 'head')

        body = etree.SubElement(root, 'body')

        return root

    def __create_cover_page(self):
        if self.final_cover_image is None:
            return None

        page = self.__create_basic_page()
        head = page.xpath('//head')[0]
        title = etree.SubElement(head, 'title')
        title.text = 'Cover'

        body = page.xpath('//body')[0]

        div = etree.SubElement(body, 'div')

        img = etree.SubElement(div, 'img')
        img.attrib['src'] = '../' + self.final_cover_image
        img.attrib['alt'] = 'Cover'

        file = open(self.root_dir + '/OEBPS/text/cover.xhtml', 'wb')
        file.write(etree.tostring(page, pretty_print=True, encoding='UTF-8', xml_declaration=True))
        file.close

        final_file = {
                'src': 'text/cover.xhtml',
                'navigation': False,
                'id': 'page-cover'}

        return final_file

    def __create_toc_page(self):
        page = self.__create_basic_page()
        head = page.xpath('//head')[0]
        title = etree.SubElement(head, 'title')
        title.text = 'Table of contents'

        body = page.xpath('//body')[0]

        h = etree.SubElement(body, 'h1')
        h.text = 'Contents'

        list = etree.SubElement(body, 'ul')

        for file in self.final_files:
            filename = re.sub(self.FILENAME_RE, r'\2', file['src'])

            li = etree.SubElement(list, 'li')
            link = etree.SubElement(li, 'a')
            link.attrib['href'] = filename
            link.text = file['nav_label']


        file = open(self.root_dir + '/OEBPS/text/toc.xhtml', 'wb')
        file.write(etree.tostring(page, pretty_print=True, encoding='UTF-8', xml_declaration=True))
        file.close

        final_file = {
                'src': 'text/toc.xhtml',
                'navigation': True,
                'class': 'other',
                'nav_label': 'Table of contents',
                'id': 'page-toc'}

        return final_file
