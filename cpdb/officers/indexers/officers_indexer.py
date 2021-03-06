import itertools

from django.db import models
from django.contrib.postgres.aggregates import ArrayAgg

from data import officer_percentile
from data.constants import (
    MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR,
    PERCENTILE_TRR_GROUP, PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP, PERCENTILE_ALLEGATION_GROUP
)
from data.models import (
    Officer, Award, OfficerAllegation, Complainant, Allegation, OfficerHistory,
    OfficerBadgeNumber, Salary
)
from data.utils.subqueries import SQCount
from es_index import register_indexer
from es_index.utils import timing_validate
from es_index.indexers import BaseIndexer
from es_index.serializers import get_gender, get_age_range
from officers.doc_types import OfficerInfoDocType
from officers.index_aliases import officers_index_alias
from officers.serializers.officer_serializer import OfficerSerializer
from trr.models import TRR

app_name = __name__.split('.')[0]


@register_indexer(app_name)
class OfficersIndexer(BaseIndexer):
    doc_type_klass = OfficerInfoDocType
    index_alias = officers_index_alias
    serializer = OfficerSerializer()
    percentile_groups = [
        PERCENTILE_ALLEGATION_GROUP,
        PERCENTILE_ALLEGATION_INTERNAL_CIVILIAN_GROUP,
        PERCENTILE_TRR_GROUP
    ]

    def __del__(self):
        del self.allegation_dict
        del self.award_dict
        del self.coaccusals
        del self.yearly_top_percentile
        del self.history_dict
        del self.badgenumber_dict
        del self.salary_dict

    @timing_validate('OfficersIndexer: Preparing percentile data...')
    def populate_top_percentile_dict(self):
        self.yearly_top_percentile = dict()
        for yr in range(MIN_VISUAL_TOKEN_YEAR, MAX_VISUAL_TOKEN_YEAR + 1):
            for officer in officer_percentile.top_percentile(yr, percentile_groups=self.percentile_groups):
                if officer.resignation_date and yr > officer.resignation_date.year:
                    continue
                officer_list = self.yearly_top_percentile.setdefault(officer.id, [])
                officer_dict = {
                    'id': officer.id,
                    'year': yr
                }
                for attr in [
                        'percentile_trr',
                        'percentile_allegation',
                        'percentile_allegation_civilian',
                        'percentile_allegation_internal']:
                    if hasattr(officer, attr):
                        officer_dict[attr] = f'{getattr(officer, attr):.4f}'
                officer_list.append(officer_dict)

    def get_complainant_dict(self):
        complainant_dict = dict()
        complainant_queryset = Complainant.objects.all().values(
            'allegation_id', 'gender', 'race', 'age'
        )
        for obj in complainant_queryset:
            complainant_dict.setdefault(obj['allegation_id'], []).append(obj)
        return complainant_dict

    def get_officer_allegation_dict(self):
        officer_allegation_dict = dict()
        officer_allegation_queryset = OfficerAllegation.objects.all().select_related('allegation_category').values(
            'id', 'allegation_id', 'officer_id', 'start_date', 'allegation_category__category', 'final_finding'
        )
        for obj in officer_allegation_queryset:
            officer_allegation_dict.setdefault(obj['allegation_id'], []).append(obj)
        return officer_allegation_dict

    def transform_demographic(self, allegation):
        transform_gender = get_gender('gender', 'Unknown')
        transform_age = get_age_range([20, 30, 40, 50], 'age', 'Unknown')
        for complainant in allegation['complainants']:
            complainant['gender'] = transform_gender(complainant)
            complainant['age'] = transform_age(complainant)
            if complainant['race'] == '':
                complainant['race'] = 'Unknown'

    def populate_coaccusal(self, allegation):
        for complaint_a, complaint_b in itertools.combinations(allegation['complaints'], 2):
            officer_id_a = complaint_a['officer_id']
            officer_id_b = complaint_b['officer_id']
            dict_a = self.coaccusals.setdefault(officer_id_a, dict())
            dict_a[officer_id_b] = dict_a.get(officer_id_b, 0) + 1
            dict_b = self.coaccusals.setdefault(officer_id_b, dict())
            dict_b[officer_id_a] = dict_b.get(officer_id_a, 0) + 1

    @timing_validate('OfficersIndexer: Populating allegation dict...')
    def populate_allegation_dict(self):
        complainant_dict = self.get_complainant_dict()
        officer_allegation_dict = self.get_officer_allegation_dict()
        allegations = Allegation.objects.all().values('crid')
        self.allegation_dict = dict()
        self.coaccusals = dict()
        for allegation in allegations:
            allegation['complainants'] = complainant_dict.get(allegation['crid'], [])
            allegation['complaints'] = officer_allegation_dict.get(allegation['crid'], [])
            self.transform_demographic(allegation)
            for complaint in allegation['complaints']:
                self.allegation_dict.setdefault(complaint['officer_id'], []).append(allegation)
            self.populate_coaccusal(allegation)

    @timing_validate('OfficersIndexer: Populating award dict...')
    def populate_award_dict(self):
        self.award_dict = dict()
        queryset = Award.objects.all().values('officer_id', 'award_type')
        for award in queryset:
            self.award_dict.setdefault(award['officer_id'], []).append(award)

    @timing_validate('OfficersIndexer: Populating history dict...')
    def populate_history_dict(self):
        self.history_dict = dict()
        queryset = OfficerHistory.objects.all().select_related('unit').values(
            'officer_id', 'unit_id', 'unit__unit_name', 'unit__description', 'end_date', 'effective_date'
        )
        for obj in queryset:
            self.history_dict.setdefault(obj['officer_id'], []).append(obj)

    @timing_validate('OfficersIndexer: Populating badgenumber dict...')
    def populate_badgenumber_dict(self):
        self.badgenumber_dict = dict()
        queryset = OfficerBadgeNumber.objects.all().values(
            'officer_id', 'star', 'current'
        )
        for obj in queryset:
            self.badgenumber_dict.setdefault(obj['officer_id'], []).append(obj)

    @timing_validate('OfficersIndexer: Populating salary dict...')
    def populate_salary_dict(self):
        self.salary_dict = dict()
        queryset = Salary.objects.all().values(
            'officer_id', 'salary', 'year'
        )
        for obj in queryset:
            self.salary_dict.setdefault(obj['officer_id'], []).append(obj)

    @timing_validate('OfficersIndexer: Populating tags dict...')
    def populate_tags_dict(self):
        self.tags_dict = dict()
        for officer in Officer.objects.exclude(tags__isnull=True).prefetch_related('tags'):
            self.tags_dict[officer.id] = [tag.name for tag in officer.tags.all()]

    def get_queryset(self):
        self.populate_top_percentile_dict()
        self.populate_allegation_dict()
        self.populate_award_dict()
        self.populate_history_dict()
        self.populate_badgenumber_dict()
        self.populate_salary_dict()
        self.populate_tags_dict()
        allegation_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('id')
        )
        sustained_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('id'),
            final_finding='SU'
        )
        unsustained_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('id'),
            final_finding='NS'
        )
        discipline_count = OfficerAllegation.objects.filter(
            officer=models.OuterRef('id'),
            disciplined=True
        )
        trr_count = TRR.objects.filter(
            officer=models.OuterRef('id')
        )
        return Officer.objects.all()\
            .annotate(complaint_count=SQCount(allegation_count.values('id')))\
            .annotate(sustained_complaint_count=SQCount(sustained_count.values('id')))\
            .annotate(discipline_complaint_count=SQCount(discipline_count.values('id')))\
            .annotate(annotated_trr_count=SQCount(trr_count.values('id')))\
            .annotate(unsustained_complaint_count=SQCount(unsustained_count.values('id')))\
            .annotate(trr_datetimes=ArrayAgg('trr__trr_datetime'))\
            .annotate(cr_incident_dates=ArrayAgg('officerallegation__allegation__incident_date'))

    def extract_datum(self, obj):
        datum = obj.__dict__
        datum['allegations'] = self.allegation_dict.get(datum['id'], [])
        datum['awards'] = self.award_dict.get(datum['id'], [])
        datum['coaccusals'] = self.coaccusals.get(datum['id'], dict())
        datum['percentiles'] = self.yearly_top_percentile.get(datum['id'], [])
        datum['history'] = self.history_dict.get(datum['id'], [])
        datum['badgenumber'] = self.badgenumber_dict.get(datum['id'], [])
        datum['salaries'] = self.salary_dict.get(datum['id'], [])
        datum['tags'] = self.tags_dict.get(datum['id'], [])

        return self.serializer.serialize(datum)
