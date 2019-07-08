from rest_framework import serializers

from shared.serializer import NoNullSerializer
from social_graph.serializers.victim_serializer import VictimSerializer
from social_graph.serializers.officer_percentile_serializer import OfficerPercentileSerializer


class AllegationCategorySerializer(NoNullSerializer):
    category = serializers.CharField()
    allegation_name = serializers.CharField()


class AttachmentFileSerializer(NoNullSerializer):
    title = serializers.CharField()
    url = serializers.CharField()
    preview_image_url = serializers.CharField()
    file_type = serializers.CharField()
    id = serializers.CharField()


class CoaccusedSerializer(NoNullSerializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    complaint_count = serializers.IntegerField(source='officer.allegation_count')
    sustained_count = serializers.IntegerField(source='officer.sustained_count')
    birth_year = serializers.IntegerField(source='officer.birth_year')
    complaint_percentile = serializers.FloatField(
        read_only=True, allow_null=True, source='officer.complaint_percentile'
    )
    recommended_outcome = serializers.CharField(source='recc_outcome')
    final_outcome = serializers.CharField()
    final_finding = serializers.CharField(source='final_finding_display')
    category = serializers.CharField()
    disciplined = serializers.NullBooleanField()
    race = serializers.CharField(source='officer.race')
    gender = serializers.CharField(source='officer.gender_display')
    rank = serializers.CharField(source='officer.rank')
    percentile = serializers.SerializerMethodField()

    def get_percentile(self, obj):
        return OfficerPercentileSerializer(obj.officer).data


class AllegationSerializer(NoNullSerializer):
    kind = serializers.SerializerMethodField()
    crid = serializers.CharField()
    to = serializers.CharField(source='v2_to')
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    address = serializers.CharField()
    victims = VictimSerializer(many=True)
    coaccused = CoaccusedSerializer(source='officer_allegations', many=True)
    attachments = AttachmentFileSerializer(source='prefetch_filtered_attachment_files', many=True)
    officer_ids = serializers.SerializerMethodField()

    def get_officer_ids(self, obj):
        return [officer_allegation.officer_id for officer_allegation in obj.officer_allegations]

    def get_kind(self, obj):
        return 'CR'

    def get_category(self, obj):
        return obj.most_common_category.category if obj.most_common_category else 'Unknown'

    def get_subcategory(self, obj):
        return obj.most_common_category.allegation_name if obj.most_common_category else 'Unknown'
