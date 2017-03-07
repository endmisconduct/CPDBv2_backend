from datetime import date

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from robber import expect

from data.factories import (
    OfficerFactory, AllegationFactory, OfficerAllegationFactory, PoliceUnitFactory,
    ComplainantFactory, AllegationCategoryFactory, OfficerHistoryFactory, OfficerBadgeNumberFactory
)
from .mixins import OfficerSummaryTestCaseMixin


class OfficersViewSetTestCase(OfficerSummaryTestCaseMixin, APITestCase):
    def test_summary(self):
        officer = OfficerFactory(
            first_name='Kevin', last_name='Kerl', id=123, race='White', gender='M',
            appointed_date=date(2017, 2, 27), rank='PO'
        )
        allegation = AllegationFactory()
        allegation_category = AllegationCategoryFactory(category='Use of Force')
        OfficerHistoryFactory(officer=officer, unit=PoliceUnitFactory(unit_name='CAND'))
        ComplainantFactory(allegation=allegation, race='White', age=18, gender='F')
        OfficerBadgeNumberFactory(officer=officer, star='123456', current=True)
        OfficerAllegationFactory(officer=officer, allegation=allegation, allegation_category=allegation_category)
        self.refresh_index()

        response = self.client.get(reverse('api-v2:officers-summary', kwargs={
            'pk': 123
        }))
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        expect(response.data).to.eq({
            'id': 123,
            'unit': 'CAND',
            'date_of_appt': '2017-02-27',
            'rank': 'PO',
            'full_name': 'Kevin Kerl',
            'race': 'White',
            'badge': '123456',
            'gender': 'Male',
            'complaint_records': {
                'count': 1,
                'categories': [
                    {
                        'name': 'Use of Force',
                        'count': 1
                    }
                ],
                'races': [
                    {
                        'name': 'White',
                        'count': 1
                    }
                ],
                'ages': [
                    {
                        'value': 18,
                        'count': 1
                    }
                ],
                'genders': [
                    {
                        'name': 'Female',
                        'count': 1
                    }
                ]
            }
        })

    def test_summary_no_match(self):
        response = self.client.get(reverse('api-v2:officers-summary', kwargs={
            'pk': 456
        }))
        expect(response.status_code).to.eq(status.HTTP_404_NOT_FOUND)