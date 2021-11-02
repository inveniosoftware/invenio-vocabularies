import os
from pathlib import Path
import tarfile
from lxml import etree

from ...services.datasources import BaseDataSource


class OrcidTarDataSource(BaseDataSource):

    def __init__(self, source, *args, **kwargs):
        self.source = source

    @staticmethod
    def _xml_to_etree(xml_input):
        """Converts xml to a lxml etree."""
        f = open(xml_input, 'r')
        xml = f.read()
        f.close()

        return etree.HTML(xml)

    @staticmethod
    def _etree_to_dict(cls, tree, only_child):
        """Converts an lxml etree into a dictionary."""
        mydict = dict([(item[0], item[1]) for item in tree.items()])
        children = tree.getchildren()
        if children:
            if len(children) > 1:
                mydict['children'] = [cls._etree_to_dict(child, False) for child in children]
            else:
                child = children[0]
                mydict[child.tag] = cls._etree_to_dict(child, True)
        if only_child:
            return mydict
        else:
            return {tree.tag: mydict}

    def iter_entries(self, *args, **kwargs):
        for subdir, dirs, files in os.walk(self.source):
            for filename in files:
                if filename.endswith('.xml'):
                    filepath = os.path.join(subdir, filename)

                    try:
                        yield self.transform_entry(filepath)
                        # Import researcher to DB
                    except Exception:
                        print
                        'Invalid researcher format'
                        pass

    def transform_entry(self, filepath, *args, **kwargs) -> dict:
        try:
            tree = self._xml_to_etree(filepath)
            # researcher = self._etree_to_dict(tree, True)
            return "test"
            # return self._etree_to_dict(tree, True)
            return {
                'given_name': researcher['given_name'],
                'family_name': researcher['family_name'],
                'identifiers': researcher['identifiers'],
                'affiliations': researcher['affiliations'],
            }
        except Exception:
            pass


