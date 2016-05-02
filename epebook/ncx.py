from lxml import etree

BASE_NS = 'http://www.daisy.org/z3986/2005/ncx/'

BASE = "{%s}" % BASE_NS

NSMAP = {None : BASE_NS}


class NCX:
    def __init__(self, title='NoTitle', author=None):
        self.title = title
        self.author = author
        self.files = []

    def set_files(self, files):
        self.files = files

    def write_file(self, path):
        ncx_file = open(path, 'w')

        root = etree.Element(BASE + "ncx",
                                nsmap=NSMAP,
                                version='2005-1')
        root.append(self.head())

        # Title
        doc_title = etree.SubElement(root, BASE + 'docTitle')
        title_text = etree.SubElement(doc_title, BASE + 'text')
        title_text.text = self.title

        # Author
        if self.author is not None:
            doc_author = etree.SubElement(root, BASE + 'docAuthor')
            author_text = etree.SubElement(doc_author, BASE + 'text')
            author_text.text = self.author

        root.append(self.nav_map())

        ncx_file.write(etree.tostring(root, pretty_print=True, encoding='UTF-8', xml_declaration=True))
        ncx_file.close()

    def head(self):
        head = etree.Element(BASE + 'head')
        return head

    def nav_map(self):
        nav_map = etree.Element(BASE + 'navMap')
        play_order = 1
        for file in self.files:
            if not file['navigation']:
                continue
            nav_point = etree.SubElement(nav_map, 'navPoint', playOrder = str(play_order))
            nav_point.attrib['class'] = file['class']
            nav_point.attrib['id'] = file['id']

            nav_label = etree.SubElement(nav_point, 'navLabel')
            nav_label_text = etree.SubElement(nav_label, 'text')
            nav_label_text.text = file['nav_label']

            content = etree.SubElement(nav_point, 'content', src = file['src'])

            play_order += 1


        return nav_map
