from django.contrib.gis.db import models
from django.core.exceptions import MultipleObjectsReturned
from django.utils.text import slugify

from data.constants import (
    ACTIVE_CHOICES, ACTIVE_UNKNOWN_CHOICE, CITIZEN_DEPTS, CITIZEN_CHOICE, LOCATION_CHOICES, AREA_CHOICES,
    LINE_AREA_CHOICES, AGENCY_CHOICES, OUTCOMES, FINDINGS, CPDB_V1_OFFICER_PATH)
from suggestion.autocomplete_types import AutoCompleteType


AREA_CHOICES_DICT = dict(AREA_CHOICES)


class PoliceUnit(models.Model):
    unit_name = models.CharField(max_length=5)

    def __str__(self):
        return self.unit_name

    @property
    def index_args(self):
        return [
            (
                self.unit_name,
                {
                    'url': self.v1_url,
                    'result_text': self.unit_name
                },
                {
                    'content_type': AutoCompleteType.OFFICER_UNIT
                }
            )
        ]

    @property
    def v1_url(self):
        return 'not implemented'  # pragma: no cover


class Officer(models.Model):
    first_name = models.CharField(
        max_length=255, null=True, db_index=True, blank=True)
    last_name = models.CharField(
        max_length=255, null=True, db_index=True, blank=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
    appointed_date = models.DateField(null=True)
    rank = models.CharField(max_length=50, blank=True)
    birth_year = models.IntegerField(null=True)
    active = models.CharField(choices=ACTIVE_CHOICES, max_length=10, default=ACTIVE_UNKNOWN_CHOICE)

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name,)

    @property
    def current_badge(self):
        try:
            return self.officerbadgenumber_set.get(current=True).star
        except (OfficerBadgeNumber.DoesNotExist, MultipleObjectsReturned):
            return ''

    @property
    def index_args(self):
        return [
            (
                self.full_name,
                {
                    'url': self.v1_url,
                    'result_text': self.full_name,
                    'result_extra_information':
                        self.current_badge and 'Badge {badge}'.format(badge=self.current_badge)
                },
                {
                    'content_type': AutoCompleteType.OFFICER
                }
            ),
            (
                self.current_badge,
                {
                    'url': self.v1_url,
                    'result_text': self.full_name,
                    'result_extra_information':
                        self.current_badge and 'Badge {badge}'.format(badge=self.current_badge)
                },
                {
                    'content_type': AutoCompleteType.OFFICER
                }
            )
        ]

    @property
    def v1_url(self):
        return '{url}/{slug}/{pk}'.format(url=CPDB_V1_OFFICER_PATH, slug=slugify(self.full_name), pk=self.pk)


class OfficerBadgeNumber(models.Model):
    officer = models.ForeignKey(Officer, null=True)
    star = models.CharField(max_length=10)
    current = models.BooleanField(default=False)

    def __str__(self):
        return '%s - %s' % (self.officer, self.star)

    @property
    def index_args(self):
        return (
            (self.star, {
                'type': AutoCompleteType.OFFICER_BADGE,
                'url': self.v1_url
                }, {
                'content_type': 'officer_badge'
            },),)

    @property
    def v1_url(self):
        return 'not implemented'  # pragma: no cover


class OfficerHistory(models.Model):
    officer = models.ForeignKey(Officer, null=True)
    unit = models.ForeignKey(PoliceUnit, null=True)
    effective_date = models.DateField(null=True)
    end_date = models.DateField(null=True)


class Area(models.Model):
    name = models.CharField(max_length=100)
    area_type = models.CharField(max_length=30, choices=AREA_CHOICES)
    polygon = models.MultiPolygonField(srid=4326, null=True)
    objects = models.GeoManager()

    @property
    def index_args(self):
        if self.area_type == 'neighborhoods':
            return [
                (
                    self.name,
                    {
                        'url': self.v1_url,
                        'result_text': self.name,
                    },
                    {
                        'content_type': AutoCompleteType.NEIGHBORHOODS
                    }
                )
            ]

        return []

    @property
    def v1_url(self):
        return 'not implemented'  # pragma: no cover


class LineArea(models.Model):
    name = models.CharField(max_length=100)
    linearea_type = models.CharField(max_length=30, choices=LINE_AREA_CHOICES)
    geom = models.MultiLineStringField(srid=4326, blank=True)
    objects = models.GeoManager()


class Investigator(models.Model):
    raw_name = models.CharField(max_length=160)
    name = models.CharField(max_length=160)
    current_rank = models.CharField(max_length=50, blank=True)
    current_report = models.CharField(max_length=4, blank=True)
    unit = models.ForeignKey(PoliceUnit, null=True)
    agency = models.CharField(choices=AGENCY_CHOICES, max_length=10)


class Allegation(models.Model):
    crid = models.CharField(max_length=30, blank=True)
    summary = models.TextField(blank=True)

    location = models.CharField(
        max_length=20, blank=True, choices=LOCATION_CHOICES)
    add1 = models.IntegerField(null=True)
    add2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    incident_date = models.DateTimeField(null=True)
    investigator = models.ForeignKey(Investigator, null=True)
    areas = models.ManyToManyField(Area)
    line_areas = models.ManyToManyField(LineArea)
    point = models.PointField(srid=4326, null=True)
    beat = models.ForeignKey(Area, null=True, related_name='beats')
    source = models.CharField(blank=True, max_length=20)


class AllegationCategory(models.Model):
    category_code = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True)
    allegation_name = models.CharField(max_length=255, blank=True)
    on_duty = models.BooleanField(default=False)
    citizen_dept = models.CharField(max_length=50, default=CITIZEN_CHOICE, choices=CITIZEN_DEPTS)


class OfficerAllegation(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    allegation_category = models.ForeignKey(AllegationCategory, to_field='id', null=True)
    officer = models.ForeignKey(Officer, null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    officer_age = models.IntegerField(null=True)

    recc_finding = models.CharField(
        choices=FINDINGS, max_length=2, blank=True)
    recc_outcome = models.CharField(
        choices=OUTCOMES, max_length=3, blank=True)
    final_finding = models.CharField(
        choices=FINDINGS, max_length=2, blank=True)
    final_outcome = models.CharField(
        choices=OUTCOMES, max_length=3, blank=True)
    final_outcome_class = models.CharField(max_length=20, blank=True)


class PoliceWitness(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
    officer = models.ForeignKey(Officer, null=True)


class Complainant(models.Model):
    allegation = models.ForeignKey(Allegation, null=True)
    gender = models.CharField(max_length=1, blank=True)
    race = models.CharField(max_length=50, blank=True)
    age = models.IntegerField(null=True)


class OfficerAlias(models.Model):
    old_officer_id = models.IntegerField()
    new_officer = models.ForeignKey(Officer)

    class Meta:
        unique_together = ('old_officer_id', 'new_officer')
