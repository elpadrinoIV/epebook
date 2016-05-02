from lxml import etree

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
    def __init__(self, title='NoTitle', author='NoAuthor', language='en', id=None, creator=None, rights=None, date=None, description=None, publisher=None):
        self.title = title
        self.author = author
        self.language = language
        self.id = id
        self.creator = creator
        self.rights = rights
        self.date = None
        self.description = description
        self.publisher = publisher
        self.files = []
        self.text = []
        self.images = []
        self.css = []
        self.ncx = None
        self.other = []

    def set_files(self, files):
        self.files = files

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

        if self.id is None:
            # TODO: create random ID
            self.id = '123456789x'

        identifier = etree.SubElement(metadata, DC + 'identifier', id='BookId')
        identifier.attrib[OPF_PFX + 'scheme'] = 'ISBN'
        identifier.text = self.id



        return metadata

    def manifest(self):
        manifest = etree.Element(BASE + 'manifest')
        # <item href="" id="" media-type="">

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
                ncx = file
            else:
                other.append(file)

        # Text
        for file in self.text:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            item.attrib['media-type'] = 'application/xhtml+xml'

        # Images
        PNG_RE = re.compile('\.png$', re.I)
        JPEG_RE = re.compile('\.jpg$', re.I)
        GIF_RE = re.compile('\.gif$', re.I)
        SVG_RE = re.compile('\.svg$', re.I)

        for file in self.images:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            if PNG_RE.match(file):
                item.attrib['media-type'] = 'image/png'
            elif JPEG_RE.match(file):
                item.attrib['media-type'] = 'image/jpeg'
            elif GIF_RE.match(file):
                item.attrib['media-type'] = 'image/gif'
            elif SVG_RE.match(file):
                item.attrib['media-type'] = 'image/svg+xml'

        # CSS
        for file in self.css:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            item.attrib['media-type'] = 'text/css'

        # NCX
        if self.ncx is not None:
            item = etree.SubElement(manifest, BASE + 'item', id = file['id'], href = file['src'])
            item.attrib['media-type'] = 'application/x-dtbncx+xml'

        return manifest

    def spine(self):
        spine = etree.Element(BASE + 'spine', toc='ncx')
        for file in self.text:
            itemref = etree.SubElement(spine, BASE + 'itemref', idref = file['id'])

        return spine

    def guide(self):
        guide = etree.Element(BASE + 'guide')
        return guide


