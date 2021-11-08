import os
from pathlib import Path
import tarfile

from ...services.datasources import XMLDataSource

class OrcidDataSource(XMLDataSource):

    def __init__(self, source):
        self.source = source

    def iter_entries(self, *args, **kwargs):

        for subdir, dirs, files in os.walk(self.source):
            for filename in files:
                if filename.endswith('.xml'):
                    filepath = os.path.join(subdir, filename)

                    try:
                        yield self.transform_entry(filepath)
                    except Exception:
                        print('Invalid researcher format')
                        pass

    def transform_entry(self, filepath, *args, **kwargs) -> dict:
        try:
            # import ipdb
            # ipdb.set_trace()
            tree = self._xml_to_etree(filepath)

            researcher = self._etree_to_dict(tree=tree, only_child=True)
            return researcher
            return {
                'given_name': researcher[''],
                'family_name': researcher['family_name'],
                'identifiers': researcher['identifiers'],
                'affiliations': researcher['affiliations'],
            }
        except Exception:
            pass


class OrcidTarDataSource(XMLDataSource):

    def __init__(self, source):
        self.source = source

    def iter_entries(self, *args, **kwargs):
        for subdir, dirs, files in os.walk(self.source):
            for filename in files:
                if filename.endswith('.xml'):
                    filepath = os.path.join(subdir, filename)

                    try:
                        yield self.transform_entry(filepath)
                    except Exception:
                        print('Invalid researcher format')
                        pass

    def transform_entry(self, filepath, *args, **kwargs) -> dict:
        try:
            tree = self._xml_to_etree(filepath)

            researcher = self._etree_to_dict(tree=tree, only_child=True)
            return researcher
            return {
                'given_name': researcher[''],
                'family_name': researcher['family_name'],
                'identifiers': researcher['identifiers'],
                'affiliations': researcher['affiliations'],
            }
        except Exception:
            pass
