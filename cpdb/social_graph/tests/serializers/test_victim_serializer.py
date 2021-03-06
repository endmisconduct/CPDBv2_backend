from django.test import TestCase
from robber import expect

from data.factories import VictimFactory

from social_graph.serializers.victim_serializer import VictimSerializer


class VictimSerializerTestCase(TestCase):
    def test_serialization(self):
        victim = VictimFactory(race='Black', gender='M', age=53)
        expect(VictimSerializer(victim).data).to.eq({
            'race': 'Black',
            'gender': 'Male',
            'age': 53,
        })
