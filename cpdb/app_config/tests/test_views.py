from robber import expect
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_config.factories import VisualTokenColorFactory, AppConfigFactory


class AppConfigTestCase(APITestCase):

    def test_should_return_correct_configs(self):
        VisualTokenColorFactory(lower_range=0, upper_range=34, color='#123456', text_color='#f82ab9')
        VisualTokenColorFactory(lower_range=34, upper_range=49, color='#f78f98', text_color='#89f123')
        VisualTokenColorFactory(lower_range=49, upper_range=49, color='#f87ab3', text_color='#abf123')
        AppConfigFactory(name='CONFIG_1', value='VALUE 1')
        AppConfigFactory(name='CONFIG_2', value='VALUE 2')
        AppConfigFactory(name='CONFIG_3', value='VALUE 3')

        url = reverse('api-v2:app-config-list')
        response = self.client.get(url)
        expect(response.status_code).to.eq(status.HTTP_200_OK)
        response_visual_token_colors = response.data['VISUAL_TOKEN_COLORS']
        expect(len(response_visual_token_colors)).to.eq(3)
        expect(response_visual_token_colors).to.eq([
            {
                'lower_range': 0,
                'upper_range': 34,
                'color': '#123456',
                'text_color': '#f82ab9'
            },
            {
                'lower_range': 34,
                'upper_range': 49,
                'color': '#f78f98',
                'text_color': '#89f123'
            },
            {
                'lower_range': 49,
                'upper_range': 49,
                'color': '#f87ab3',
                'text_color': '#abf123'
            }
        ])

        expect(response.data['CONFIG_1']).to.eq('VALUE 1')
        expect(response.data['CONFIG_2']).to.eq('VALUE 2')
        expect(response.data['CONFIG_3']).to.eq('VALUE 3')
