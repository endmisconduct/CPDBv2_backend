from tqdm import tqdm

from cms.models import FAQPage, ReportPage
from data.models import Officer, PoliceUnit, Area, OfficerHistory, Allegation
from search.doc_types import (
    FAQDocType, ReportDocType, OfficerDocType,
    UnitDocType, NeighborhoodsDocType, CommunityDocType,
    UnitOfficerDocType, CrDocType
)
from .indices import autocompletes


def extract_text_from_value(value):
    return '\n'.join([block['text'] for block in value['blocks']])


class BaseIndexer(object):
    doc_type_klass = None

    def get_queryset(self):
        raise NotImplementedError

    def extract_datum(self, datum):
        raise NotImplementedError

    def extract_datum_with_id(self, datum):
        '''
        Ensure that the indexed document has the same ID as its corresponding database record.
        We can't do this to indexer classes where extract_datum() returns a list because
        multiple documents cannot share the same ID.
        '''
        extracted_data = self.extract_datum(datum)
        if not isinstance(extracted_data, list):
            extracted_data['meta'] = {'id': datum.pk}
        return extracted_data

    def save_doc(self, extracted_data):
        doc = self.doc_type_klass(**extracted_data)
        doc.save()

    def index_datum(self, datum):
        extracted_data = self.extract_datum_with_id(datum)
        if isinstance(extracted_data, list):
            [self.save_doc(entry) for entry in extracted_data]
        else:
            self.save_doc(extracted_data)

    def index_data(self):
        for datum in tqdm(
            self.get_queryset(),
            desc='Indexing {doc_type_name}'.format(
                doc_type_name=self.doc_type_klass._doc_type.name)):
            self.index_datum(datum)


class FAQIndexer(BaseIndexer):
    doc_type_klass = FAQDocType

    def get_queryset(self):
        return FAQPage.objects.all()

    def extract_datum(self, datum):
        fields = datum.fields

        return {
            'question': extract_text_from_value(fields['question_value']),
            'answer': extract_text_from_value(fields['answer_value']),
            'tags': datum.tags
        }


class ReportIndexer(BaseIndexer):
    doc_type_klass = ReportDocType

    def get_queryset(self):
        return ReportPage.objects.all()

    def extract_datum(self, datum):
        fields = datum.fields

        return {
            'publication': fields['publication_value'],
            'author': fields['author_value'],
            'excerpt': extract_text_from_value(fields['excerpt_value']),
            'title': extract_text_from_value(fields['title_value']),
            'publish_date': fields['publish_date_value'],
            'tags': datum.tags
        }


class OfficerIndexer(BaseIndexer):
    doc_type_klass = OfficerDocType

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return {
            'allegation_count': datum.allegation_count,
            'full_name': datum.full_name,
            'badge': datum.current_badge,
            'to': datum.v2_to,
            'visual_token_background_color': datum.visual_token_background_color,
            'tags': datum.tags,
            'sustained_count': datum.sustained_count,
            'birth_year': datum.birth_year,
            'unit': datum.last_unit,
            'rank': datum.rank,
            'race': datum.race,
            'sex': datum.gender_display
        }


class UnitIndexer(BaseIndexer):
    doc_type_klass = UnitDocType

    def get_queryset(self):
        return PoliceUnit.objects.all()

    def extract_datum(self, datum):
        return {
            'name': datum.unit_name,
            'description': datum.description,
            'url': datum.v1_url,
            'to': datum.v2_to,
            'active_member_count': datum.active_member_count,
            'member_count': datum.member_count
        }


class UnitOfficerIndexer(BaseIndexer):
    doc_type_klass = UnitOfficerDocType

    def get_queryset(self):
        return OfficerHistory.objects.all()

    def extract_datum(self, datum):
        return {
            'full_name': datum.officer.full_name,
            'badge': datum.officer.current_badge,
            'to': datum.officer.v2_to,
            'allegation_count': datum.officer.allegation_count,
            'visual_token_background_color': datum.officer.visual_token_background_color,
            'unit_name': datum.unit.unit_name,
            'unit_description': datum.unit.description,
            'sustained_count': datum.officer.sustained_count,
            'birth_year': datum.officer.birth_year,
            'unit': datum.officer.last_unit,
            'rank': datum.officer.rank,
            'race': datum.officer.race,
            'sex': datum.officer.gender_display
        }


class AreaTypeIndexer(BaseIndexer):
    doc_type_klass = None
    area_type = None

    def get_queryset(self):
        return Area.objects.filter(area_type=self.area_type)

    def extract_datum(self, datum):
        return {
            'name': datum.name,
            'url': datum.v1_url,
            'tags': datum.tags
        }


class NeighborhoodsIndexer(AreaTypeIndexer):
    doc_type_klass = NeighborhoodsDocType
    area_type = 'neighborhoods'


class CommunityIndexer(AreaTypeIndexer):
    doc_type_klass = CommunityDocType
    area_type = 'community'


class IndexerManager(object):
    def __init__(self, indexers=None):
        self.indexers = indexers or []

    def _build_mapping(self):
        autocompletes.delete(ignore=404)
        autocompletes.create()

    def _index_data(self):
        for indexer_klass in self.indexers:
            indexer_klass().index_data()

    def rebuild_index(self):
        self._build_mapping()
        self._index_data()


class CrIndexer(BaseIndexer):
    doc_type_klass = CrDocType

    def get_queryset(self):
        return Allegation.objects.all()

    def extract_datum(self, datum):
        return {
            'crid': datum.crid,
            'to': datum.v2_to
        }
