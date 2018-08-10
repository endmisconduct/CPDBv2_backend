import inflect

from .workers import (
    OfficerWorker, UnitWorker, CommunityWorker, NeighborhoodsWorker)
from .formatters import SimpleFormatter


p = inflect.engine()

DEFAULT_SEARCH_WORKERS = {
    'OFFICER': OfficerWorker(),
    'UNIT': UnitWorker(),
    'COMMUNITY': CommunityWorker(),
    'NEIGHBORHOOD': NeighborhoodsWorker()
}


class SearchManager(object):
    def __init__(self, formatters=None, workers=None, fixed_name_workers=None, hooks=None):
        self.formatters = formatters or {}
        self.workers = workers or DEFAULT_SEARCH_WORKERS
        self.fixed_name_workers = fixed_name_workers
        self.hooks = hooks or []

    def singularize_content_type(self, content_type):
        if content_type not in self.fixed_name_workers:
            singular_form = p.singular_noun(content_type)
            if singular_form is False:
                return content_type
            else:
                return singular_form
        return content_type

    def search(self, term, content_type=None, limit=10000):
        response = {}

        if content_type:
            search_results = self.workers[content_type].search(term, size=limit)
            response[self.singularize_content_type(content_type)] = self._formatter_for(content_type)().format(
                search_results
            )

        else:
            for _content_type, worker in self.workers.items():
                search_results = worker.search(term)
                response[self.singularize_content_type(_content_type)] = self._formatter_for(_content_type)().format(
                    search_results
                )

        for hook in self.hooks:
            hook.execute(term, content_type, response)

        return response

    def get_search_query_for_type(self, term, content_type):
        return self.workers[content_type].query(term)

    def get_formatted_results(self, documents, content_type):
        return self._formatter_for(content_type)().serialize(documents)

    def suggest_sample(self):
        '''
        Return 1 random item that has tags from each content type.
        '''
        response = {}

        for content_type, worker in self.workers.items():
            search_results = worker.get_sample()
            response[content_type] = self._formatter_for(content_type)().format(search_results)

        return response

    def _formatter_for(self, content_type):
        return self.formatters.get(content_type, SimpleFormatter)
