from officers.index_aliases import officers_index_alias
from officers.indexers import (
    OfficersIndexer,
    OfficerCoaccusalsIndexer,
)


class OfficerSummaryTestCaseMixin(object):
    def setUp(self):
        officers_index_alias.write_index.delete(ignore=404)
        officers_index_alias.read_index.create(ignore=400)

    def refresh_index(self):
        with officers_index_alias.indexing():
            OfficersIndexer().reindex()
            OfficerCoaccusalsIndexer().reindex()

        officers_index_alias.write_index.refresh()

    def refresh_read_index(self):
        officers_index_alias.read_index.refresh()
