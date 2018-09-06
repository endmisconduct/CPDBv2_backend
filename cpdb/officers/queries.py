from es_index.queries import (
    AggregateQuery, RowArrayQueryField, DistinctQuery, Subquery, CountQueryField
)
from data.models import (
    Officer, OfficerHistory, OfficerBadgeNumber, OfficerAllegation, AllegationCategory,
    Allegation, Complainant, PoliceUnit, Award, Salary
)
from trr.models import TRR


class OfficerAllegationQuery(DistinctQuery):
    base_table = OfficerAllegation

    joins = {
        'category': AllegationCategory
    }

    fields = {
        'id': 'id',
        'allegation_id': 'allegation_id',
        'officer_id': 'officer_id',
        'start_date': 'start_date',
        'category': 'category.category',
        'final_finding': 'final_finding',
    }


class AllegationQuery(AggregateQuery):
    base_table = Allegation

    joins = {
        'complainants': Complainant,
        'complaints': Subquery(OfficerAllegationQuery(), on='allegation_id')
    }

    fields = {
        'id': 'id',
        'crid': 'crid',
        'complainants': RowArrayQueryField('complainants'),
        'complaints': RowArrayQueryField('complaints')
    }


class OfficerHistoryQuery(DistinctQuery):
    base_table = OfficerHistory

    joins = {
        'unit': PoliceUnit
    }

    fields = {
        'officer_id': 'officer_id',
        'unit_id': 'unit_id',
        'unit_name': 'unit.unit_name',
        'description': 'unit.description',
        'end_date': 'end_date',
        'effective_date': 'effective_date'
    }


class OfficerQuery(AggregateQuery):
    base_table = Officer

    joins = {
        'history': Subquery(OfficerHistoryQuery(), on='officer_id'),
        'badgenumber': OfficerBadgeNumber,
        'awards': Award,
        'salaries': Salary
    }

    fields = {
        'id': 'id',
        'date_of_appt': 'appointed_date',
        'date_of_resignation': 'resignation_date',
        'active': 'active',
        'rank': 'rank',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'middle_initial': 'middle_initial',
        'middle_initial2': 'middle_initial2',
        'suffix_name': 'suffix_name',
        'race': 'race',
        'gender': 'gender',
        'birth_year': 'birth_year',
        'history': RowArrayQueryField('history'),
        'badgenumber': RowArrayQueryField('badgenumber'),
        'allegation_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table'),
        'sustained_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table', where={'final_finding': 'SU'}),
        'complaint_percentile': 'complaint_percentile',
        'honorable_mention_percentile': 'honorable_mention_percentile',
        'awards': RowArrayQueryField('awards'),
        'discipline_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table', where={'disciplined': True}),
        'civilian_allegation_percentile': 'civilian_allegation_percentile',
        'internal_allegation_percentile': 'internal_allegation_percentile',
        'trr_percentile': 'trr_percentile',
        'trr_count': CountQueryField(
            from_table=TRR, related_to='base_table'),
        'tags': 'tags',
        'unsustained_count': CountQueryField(
            from_table=OfficerAllegation, related_to='base_table', where={'final_finding': 'NS'}),
        'salaries': RowArrayQueryField('salaries')
    }
