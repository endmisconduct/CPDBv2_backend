from mock import patch

from django.core.urlresolvers import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from robber import expect


class SearchV2ViewSetTestCase(APITestCase):
    @patch('search.views.SearchManager.suggest_sample')
    def test_list_ok(self, suggest_sample):
        suggest_sample.return_value = 'anything_suggester_returns'

        url = reverse('api-v2:search-mobile-list', kwargs={})
        response = self.client.get(url, {})

        expect(response.status_code).to.equal(status.HTTP_200_OK)
        expect(response.data).to.equal('anything_suggester_returns')
        suggest_sample.assert_called_with()