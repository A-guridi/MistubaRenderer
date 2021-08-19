import numpy as np
import xml.etree.ElementTree as et

class XML_Parser():
    def __init__(self, xml_file):
        self.tree=et.parse(xml_file)
        self.root=self.tree.getroot()