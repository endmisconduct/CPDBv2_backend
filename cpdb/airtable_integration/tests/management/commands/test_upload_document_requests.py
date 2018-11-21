from django.core import management
from django.test import TestCase

from mock import patch, call
from robber import expect

from data.factories import (
    OfficerFactory, OfficerAllegationFactory, AttachmentRequestFactory,
    AllegationFactory, InvestigatorAllegationFactory, InvestigatorFactory
)
from trr.factories import TRRFactory, TRRAttachmentRequestFactory


class UpdateDocumentsCommandTestCase(TestCase):
    @patch('django.conf.settings.AIRTABLE_CPD_AGENCY_ID', 'CPD_AGENCY_ID')
    @patch('django.conf.settings.AIRTABLE_COPA_AGENCY_ID', 'COPA_AGENCY_ID')
    @patch('airtable_integration.services.document_request_service.AirTableUploader._lazy_airtable')
    def test_upload_document_requests(self, airtable_mock):
        allegation123 = AllegationFactory(crid='123')
        officer_1 = OfficerFactory(id=1, first_name='Marry', last_name='Jane')
        officer_2 = OfficerFactory(id=2, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation123, officer=officer_1)
        OfficerAllegationFactory(allegation=allegation123, officer=officer_2)
        investigator = InvestigatorFactory(officer=officer_1)
        InvestigatorAllegationFactory(allegation=allegation123, investigator=investigator)
        cr_request_1 = AttachmentRequestFactory(
            allegation=allegation123,
            email='requester1@example.com',
            added_to_foia_airtable=False)
        cr_request_2 = AttachmentRequestFactory(
            allegation=allegation123,
            email='requester2@example.com',
            added_to_foia_airtable=True)

        allegation456 = AllegationFactory(crid='456')
        officer_3 = OfficerFactory(id=3, first_name='Marry', last_name='Jane')
        officer_4 = OfficerFactory(id=4, first_name='John', last_name='Henry')
        OfficerAllegationFactory(allegation=allegation456, officer=officer_3)
        OfficerAllegationFactory(allegation=allegation456, officer=officer_4)
        cr_request_3 = AttachmentRequestFactory(
            allegation=allegation456,
            email='requester3@example.com',
            added_to_foia_airtable=False)
        cr_request_4 = AttachmentRequestFactory(
            allegation=allegation456,
            email='requester4@example.com',
            added_to_foia_airtable=True)

        trr = TRRFactory(id='123456', officer=officer_1)
        trr_request_1 = TRRAttachmentRequestFactory(
            trr=trr,
            email='requester@example1.com',
            added_to_foia_airtable=False)
        trr_request_2 = TRRAttachmentRequestFactory(
            trr=trr,
            email='requester@example2.com',
            added_to_foia_airtable=True)

        expect(cr_request_1.added_to_foia_airtable).to.be.false()
        expect(cr_request_2.added_to_foia_airtable).to.be.true()
        expect(cr_request_3.added_to_foia_airtable).to.be.false()
        expect(cr_request_4.added_to_foia_airtable).to.be.true()
        expect(trr_request_1.added_to_foia_airtable).to.be.false()
        expect(trr_request_2.added_to_foia_airtable).to.be.true()

        management.call_command('upload_document_requests')
        cr_request_1.refresh_from_db()
        cr_request_2.refresh_from_db()
        cr_request_3.refresh_from_db()
        cr_request_4.refresh_from_db()
        trr_request_1.refresh_from_db()
        trr_request_2.refresh_from_db()

        expected_calls = [
            call({
                'Explanation': 'Officers: John Henry(ID 2), Marry Jane(ID 1)',
                'Project': [
                    'CPDP'
                ],
                'Agency': ['CPD_AGENCY_ID'],
                'Requested For': 'CR 123',
                'Requestor': [
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            }),
            call({
                'Explanation': 'Officers: John Henry(ID 4), Marry Jane(ID 3)',
                'Project': [
                    'CPDP'
                ],
                'Agency': ['COPA_AGENCY_ID'],
                'Requested For': 'CR 456',
                'Requestor': [
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            }),
            call({
                'Explanation':  'Officer: Marry Jane(ID 1)',
                'Project': [
                  'CPDP'
                ],
                'Agency': [],
                'Requested For': 'TRR 123456',
                'Requestor': [
                    {
                        'id': 'usrGiZFcyZ6wHTYWd',
                        'email': 'rajiv@invisibleinstitute.com',
                        'name': 'Rajiv Sinclair'
                    }
                ]
            })
        ]

        airtable_mock.insert.assert_has_calls(expected_calls, any_order=True)

        expect(cr_request_1.added_to_foia_airtable).to.be.true()
        expect(cr_request_2.added_to_foia_airtable).to.be.true()
        expect(cr_request_3.added_to_foia_airtable).to.be.true()
        expect(cr_request_4.added_to_foia_airtable).to.be.true()
        expect(trr_request_1.added_to_foia_airtable).to.be.true()
        expect(trr_request_2.added_to_foia_airtable).to.be.true()