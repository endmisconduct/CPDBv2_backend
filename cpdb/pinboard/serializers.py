from rest_framework import serializers

from shared.serializer import NoNullSerializer, OfficerPercentileSerializer
from data.models import Officer, Allegation, AttachmentFile
from trr.models import TRR
from .models import Pinboard


class OfficerCardSerializer(serializers.ModelSerializer):
    coaccusal_count = serializers.IntegerField(allow_null=True)
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj).data

    class Meta:
        model = Officer
        fields = (
            'id',
            'rank',
            'full_name',
            'coaccusal_count',
            'percentile',
        )


class AllegationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='most_common_category.category')
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    officers = serializers.SerializerMethodField()

    def get_officers(self, obj):
        officers = [officer_allegation.officer for officer_allegation in obj.prefetch_officer_allegations]
        return OfficerCardSerializer(officers, many=True).data

    class Meta:
        model = Allegation
        fields = (
            'crid',
            'incident_date',
            'v2_to',
            'category',
            'officers',
        )


class DocumentCardSerializer(serializers.ModelSerializer):
    allegation = serializers.SerializerMethodField()

    def get_allegation(self, obj):
        return AllegationSerializer(obj.allegation).data

    class Meta:
        model = AttachmentFile
        fields = (
            'id',
            'preview_image_url',
            'url',
            'allegation',
        )


class PinboardSerializer(serializers.ModelSerializer):
    id = serializers.CharField(
        min_length=8,
        max_length=8,
        read_only=True
    )
    crids = serializers.PrimaryKeyRelatedField(
        source='allegations',
        many=True,
        queryset=Allegation.objects.all()
    )
    officer_ids = serializers.PrimaryKeyRelatedField(
        source='officers',
        many=True,
        queryset=Officer.objects.all()
    )
    trr_ids = serializers.PrimaryKeyRelatedField(
        source='trrs',
        many=True,
        queryset=TRR.objects.all()
    )
    relevant_coaccusals = serializers.SerializerMethodField()
    relevant_documents = serializers.SerializerMethodField()

    def get_relevant_coaccusals(self, obj):
        return OfficerCardSerializer(obj.relevant_coaccusals, many=True).data

    def get_relevant_documents(self, obj):
        return DocumentCardSerializer(obj.relevant_documents, many=True).data

    class Meta:
        model = Pinboard
        fields = (
            'id',
            'title',
            'officer_ids',
            'crids',
            'trr_ids',
            'description',
            'relevant_coaccusals',
            'relevant_documents',
        )


class CRPinboardSerializer(NoNullSerializer):
    date = serializers.SerializerMethodField()
    crid = serializers.CharField()
    category = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_date(self, obj):
        return obj.incident_date.date().strftime(format='%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None


class TRRPinboardSerializer(NoNullSerializer):
    trr_id = serializers.IntegerField(source='id')
    date = serializers.SerializerMethodField()
    kind = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_kind(self, obj):
        return 'FORCE'

    def get_date(self, obj):
        return obj.trr_datetime.date().strftime(format='%Y-%m-%d')

    def get_point(self, obj):
        try:
            return {
                'lon': obj.point.x,
                'lat': obj.point.y
            }
        except AttributeError:
            return None
