import csv
from itertools import combinations

from es_index import register_indexer
from es_index.indexers import BaseIndexer
from data.models import Officer, OfficerAllegation, OfficerHistory, Allegation
from officers.doc_types import OfficerPercentileDocType
from .doc_types import (
    OfficerSummaryDocType, OfficerTimelineEventDocType, OfficerSocialGraphDocType
)
from .index_aliases import officers_index_alias
from .serializers import (
    OfficerSummarySerializer, CRTimelineSerializer, UnitChangeTimelineSerializer, JoinedTimelineSerializer
)

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class OfficersIndexer(BaseIndexer):
    doc_type_klass = OfficerSummaryDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Officer.objects.all()

    def extract_datum(self, datum):
        return OfficerSummarySerializer(datum).data


@register_indexer(app_name)
class CRTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return OfficerAllegation.objects.filter(start_date__isnull=False)

    def extract_datum(self, datum):
        return CRTimelineSerializer(datum).data


@register_indexer(app_name)
class UnitChangeTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return OfficerHistory.objects.filter(effective_date__isnull=False)

    def extract_datum(self, datum):
        return UnitChangeTimelineSerializer(datum).data


@register_indexer(app_name)
class JoinedTimelineEventIndexer(BaseIndexer):
    doc_type_klass = OfficerTimelineEventDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Officer.objects.filter(appointed_date__isnull=False)

    def extract_datum(self, officer):
        return JoinedTimelineSerializer(officer).data


@register_indexer(app_name)
class SocialGraphIndexer(BaseIndexer):
    doc_type_klass = OfficerSocialGraphDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        return Officer.objects.all()

    def _cr_years(self, officer):
        dates = officer.officerallegation_set.values_list('allegation__incident_date', flat=True)
        return sorted([_date.year if _date is not None else None for _date in dates])

    def _node(self, officer):
        return {
            "id": officer.id,
            "name": officer.full_name,
            "cr_years": self._cr_years(officer)
        }

    def _links(self, officers):
        links = []
        for o1, o2 in combinations(officers, 2):
            qs = Allegation.objects.filter(officerallegation__officer=o1) \
                .filter(officerallegation__officer=o2).distinct()
            if qs.exists():
                link = {
                    'source': o1.id,
                    'target': o2.id,
                    'cr_years': sorted([
                        _date.year if _date is not None else None
                        for _date in qs.values_list('incident_date', flat=True)
                    ])
                }
                links.append(link)
        return links

    def extract_datum(self, officer):
        coaccuseds = Officer.objects.filter(
            officerallegation__allegation__officerallegation__officer=officer).distinct().order_by('id')

        return {'officer_id': officer.pk, 'graph': {
            'links': self._links(coaccuseds),
            'nodes': [self._node(coaccused) for coaccused in coaccuseds]
        }}


@register_indexer(app_name)
class OfficerPercentileIndexer(BaseIndexer):
    doc_type_klass = OfficerPercentileDocType
    index_alias = officers_index_alias

    def get_queryset(self):
        try:
            results = []
            # TODO: compute from db when TRR is ready
            with open('all_yearly_officer_percentile.csv') as csv_file:
                reader = csv.DictReader(csv_file)
                for row in reader:
                    results.append(row)
            return results
        except IOError:
            return []

    def extract_datum(self, datum):
        return {
            'officer_id': int(float(datum['UID'])),
            'year': int(float(datum['TRR_date'])),
            'percentile_alL_trr': float(datum['ALL_TRR']) * 100,
            'percentile_civilian': float(datum['CIVILLIAN']) * 100,
            'percentile_internal': float(datum['INTERNAL']) * 100,
            'percentile_shooting': float(datum['SHOOTING']) * 100,
            'percentile_taser': float(datum['TASER']) * 100,
            'percentile_others': float(datum['OTHERS']) * 100
        }
