from lxml import etree

import datetime
import re

BASE_NS = 'http://www.idpf.org/2007/opf'
DC_NS = 'http://purl.org/dc/elements/1.1/'
OPF_NS = 'http://www.idpf.org/2007/opf'
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'

BASE = "{%s}" % BASE_NS
DC = "{%s}" % DC_NS
OPF_PFX = "{%s}" % OPF_NS

NSMAP = {None : BASE_NS}
NSMAP2 = {'dc' : DC_NS, 'opf' : OPF_NS, 'xsi': XSI_NS}

class OPF:
    TEXT_RE = re.compile('(\.html|\.xhtml|\.htm)$', re.I)
    CSS_RE = re.compile('\.css$', re.I)
    NCX_RE = re.compile('\.ncx$', re.I)
    JPEG_RE = re.compile('\.jpg$', re.I)
    PNG_RE = re.compile('\.png$', re.I)
    GIF_RE = re.compile('\.gif$', re.I)
    SVG_RE = re.compile('\.svg$', re.I)

    def __init__(self, title='NoTitle',  language='en'):
        self.title = title
        self.authors = []
        self.contributors = []
        self.language = language
        self.id = None
        self.id_type = None
        self.rights = None
        self.date = None
        self.description = None
        self.publisher = None
        self.cover_image = None
        self.cover_page = None
        self.files = []
        self.text = []
        self.images = []
        self.css = []
        self.ncx = None
        self.toc_page = None

    def set_files(self, files):
        self.files = files

    def set_cover(self, cover_image, cover_page):
        self.cover_image = cover_image
        self.cover_page = cover_page

    def set_toc_page(self, toc_page):
        self.toc_page = toc_page

    def set_title(self, title):
        self.title = title

    def set_language(self, language):
        self.language = language

    def set_id(self, id, id_type):
        self.id = id
        self.id_type = id_type

    def add_author(self, author):
        if type(author) == str:
            self.authors.append(author)
        elif type(author) == list:
            self.authors = self.authors + author

    def add_contributor(self, contributor):
        if type(contributor) == str:
            self.contributors.append(contributor)
        elif type(contributor) == list:
            self.contributors = self.contributors + contributor

    def set_rights(self, rights):
        self.rights = rights

    def set_date(self, date):
        self.date = date

    def set_description(self, description):
        self.description = description

    def set_publisher(self, publisher):
        self.publisher = publisher

    def write_file(self, path):
        opf_file = open(path, 'w')

        package = etree.Element(BASE + "package",
                                nsmap=NSMAP,
                                version='2.0')
        package.attrib['unique-identifier'] = 'BookId'
        package.append(self.metadata())
        package.append(self.manifest())
        package.append(self.spine())
        package.append(self.guide())

        opf_file.write(etree.tostring(package, pretty_print=True, encoding='UTF-8', xml_declaration=True))
        opf_file.close()

    def metadata(self):
        metadata = etree.Element(BASE + 'metadata', nsmap=NSMAP2)

        # title, identifier and language must be included
        title = etree.SubElement(metadata, DC + 'title')
        title.text = self.title

        language = etree.SubElement(metadata, DC + 'language')
        language.text = self.language


        identifier = etree.SubElement(metadata, DC + 'identifier', id='BookId')
        identifier.attrib[OPF_PFX + 'scheme'] = self.id_type
        identifier.text = self.id

        for author in self.authors:
            a = etree.SubElement(metadata, DC + 'creator')
            a.attrib[OPF_PFX + 'role'] = 'aut'
            a.text = author

        for contributor in self.contributors:
            c = etree.SubElement(metadata, DC + 'contributor')
            c.text = contributor

        if self.rights is not None:
            rights = etree.SubElement(metadata, DC + 'rights')
            rights.text = self.rights

        if self.date is not None:
            if type(self.date) == str:
                date = etree.SubElement(metadata, DC + 'date')
                date.text = self.date
            elif type(self.date) == datetime.datetime:
                date = etree.SubElement(metadata, DC + 'date')
                date.text = self.date.strftime("%Y-%m-%d")

        if self.description is not None:
            description = etree.SubElement(metadata, DC + 'description')
            description.text = self.description

        if self.publisher is not None:
            publisher = etree.SubElement(metadata, DC + 'publisher')
            publisher.text = self.publisher

        if self.cover_image is not None:
            cover = etree.SubElement(metadata, BASE + 'meta')
            cover.attrib['name'] = 'cover'
            cover.attrib['content'] = 'cover'


        return metadata

    def manifest(self):
        manifest = etree.Element(BASE + 'manifest')

        IMAGES_RE = re.compile('(\.jpg|\.gif|\.png|\.svg)$', re.I)
        TEXT_RE = re.compile('(\.html|\.xhtml|\.htm)$', re.I)
        CSS_RE = re.compile('\.css$', re.I)
        NCX_RE = re.compile('\.ncx$', re.I)
        for file in self.files:
            filename = file['src']
            if IMAGES_RE.search(filename):
                self.images.append(file)
            elif TEXT_RE.search(filename):
                self.text.append(file)
            elif CSS_RE.search(filename):
                self.css.append(file)
            elif NCX_RE.search(filename):
                self.ncx = file

        # Cover
        if self.cover_image is not None:
            item = etree.SubElement(manifest, BASE + 'item', id = 'cover', href = self.cover_image)
            item.attrib['media-type'] = self.__get_media_type(self.cover_image)

        if self.cover_page is not None:
            item = etree.SubElement(manifest, BASE + 'item', id = self.cover_page['id'], href = self.cover_page['src'])
            item.attrib['media-type'] = self.__get_media_type(self.cover_page['src'])

        # Text
        for file in self.text:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            item.attrib['media-type'] = self.__get_media_type(file['src'])

        # Images
        for file in self.images:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            item.attrib['media-type'] = self.__get_media_type(file['src'])

        # CSS
        for file in self.css:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            item.attrib['media-type'] = self.__get_media_type(file['src'])

        # NCX
        if self.ncx is not None:
            item = etree.SubElement(manifest, BASE + 'item', id = self.ncx['id'], href = self.ncx['src'])
            item.attrib['media-type'] = self.__get_media_type(self.ncx['src'])

        # TOC page
        if self.toc_page is not None:
            item = etree.SubElement(manifest, BASE + 'item', id = self.toc_page['id'], href = self.toc_page['src'])
            item.attrib['media-type'] = self.__get_media_type(self.toc_page['src'])

        return manifest

    def spine(self):
        spine = etree.Element(BASE + 'spine', toc='ncx')

        if self.toc_page is not None:
            itemref = etree.SubElement(spine, BASE + 'itemref', idref = self.toc_page['id'])

        for file in self.text:
            itemref = etree.SubElement(spine, BASE + 'itemref', idref = file['id'])

        return spine

    def guide(self):
        guide = etree.Element(BASE + 'guide')

        if self.cover_page is not None:
            reference = etree.SubElement(guide, BASE + 'reference', type = 'cover', title = 'Cover', href = self.cover_page['src'])

        if self.toc_page is not None:
            reference = etree.SubElement(guide, BASE + 'reference', type = 'toc', title = 'Table of contents', href = self.toc_page['src'])

        return guide

    def __get_media_type(self, filename):

        if self.TEXT_RE.search(filename):
            return 'application/xhtml+xml'
        elif self.CSS_RE.search(filename):
            return 'text/css'
        elif self.NCX_RE.search(filename):
            return 'application/x-dtbncx+xml'
        elif self.JPEG_RE.search(filename):
            return 'image/jpeg'
        elif self.PNG_RE.search(filename):
            return 'image/png'
        elif self.GIF_RE.search(filename):
            return 'image/gif'
        elif self.SVG_RE.search(filename):
            return 'image/svg+xml'
        else:
            return 'unknown'
