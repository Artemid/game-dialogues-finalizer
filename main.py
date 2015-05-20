__author__ = 'Artem Nurgaliev artem.nurgaliev@signuslabs.com'


import os
import sys
import xml.sax


class Entry:
    """
    Basic entry
    """

    def __init__(self, key="", value="", section="", file=""):
        self.value = value
        self.key = key
        self.section = section
        self.file = file


class Collection:
    """
    Class to store intermediate scripts. Supposed that the translation keys are unique.
    """

    def __init__(self):
        # self.slots = Set()
        self.sections = {"ROOT": []}
        self.entries = {}

    def append(self, file, section, attributes=None):
        if section not in self.sections.keys():
            self.sections[section] = []

        if attributes:
            new_key = attributes["KEY"]
            new_value = attributes["VALUE"]

            new_entry = Entry(key=new_key, value=new_value, section=section, file=file)
            self.sections[section].append(new_entry)
            # self.slots.add(new_key)

            if new_key not in self.entries.keys():
                self.entries[new_key] = new_entry

    def merge(self, collection):
        """
        Simple merge method based on Set arithmetic. We are interested in A = A disjunction B.
        Remove all records from current collection (A) that are not exist in given collection (B).
        Take values of entries from (B) by keys from (A).
        """
        pass

    @staticmethod
    def group_by_sheets(entries):
        sheets = {}
        for entry in entries:
            new_key = entry
            head, sheet_name = os.path.split(entries[new_key].file)

            if sheet_name not in sheets.keys():
                sheets[sheet_name] = {}

            new_entries = sheets[sheet_name]
            if new_key not in new_entries.keys():
                new_entries[new_key] = entries[new_key]

        return sheets

    @staticmethod
    def group_by_sections(entries):
        sections = {}
        for entry in entries:
            new_key = entry
            section_name = entries[new_key].section
            if section_name not in sections.keys():
                sections[section_name] = {}

            new_entries = sections[section_name]
            if new_key not in new_entries.keys():
                new_entries[new_key] = entries[new_key]

        return sections


class TEXTHandler(xml.sax.ContentHandler):
    def __init__(self, collection):
        self.collection = collection
        self.cur_section = "ROOT"
        self.linked_files = []

    def startElement(self, tag, attributes):
        """SAX callback Handles all SECTION and TEXT tags"""

        cur_file = self._locator.getSystemId()

        # print("Opened: ", tag)
        if tag == "SECTION":
            self.cur_section = attributes["NAME"]
            self.collection.append(cur_file, self.cur_section)
        elif tag == "TEXT":
            if "KEY" in attributes.keys():
                self.collection.append(cur_file, self.cur_section, attributes)
            elif "FILE" in attributes.keys():
                self.linked_files.append(attributes["FILE"])

    def endElement(self, tag):
        """This called after tag was processed. Handles SECTION"""
        if tag == "SECTION":
            self.cur_section = "ROOT"


def load_from_xml(inp_filename, collection):
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    handler = TEXTHandler(collection)
    parser.setContentHandler(handler)
    parser.parse(inp_filename)

    # and all the remaining sections in files referenced from main
    if handler.linked_files:
        for fName in handler.linked_files:
            if os.path.exists(fName):
                print("Processing linked file: %s" % fName)
                linked_handler = TEXTHandler(collection)
                parser.setContentHandler(linked_handler)
                parser.parse(fName)
            else:
                print("File does not exists: %s" % fName)


def main():
    print("Application started")

    os.chdir("C:\\projects\\PAPG\\build\\papgG5\\cdimage\\data")
    print("Current dir: %s" % os.getcwd())

    collection = Collection()
    load_from_xml("translator_en.xml", collection)

    for key in collection.entries:
        print("%s: %s" % (collection.entries[key].key, collection.entries[key].value))


if __name__ == "__main__":
    main()
