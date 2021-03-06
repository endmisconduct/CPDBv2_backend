from copy import deepcopy
from collections import OrderedDict

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F

from cr.doc_types import CRDocType
from cr.serializers.cr_response_serializers import (
    CRSerializer, CRSummarySerializer, AttachmentRequestSerializer,
    AllegationWithNewDocumentsSerializer, CRRelatedComplaintRequestSerializer, CRRelatedComplaintSerializer
)
from cr.serializers.cr_response_mobile_serializers import CRMobileSerializer
from email_service.constants import CR_ATTACHMENT_REQUEST
from es_index.pagination import ESQueryPagination
from data.models import Allegation
from cr.queries import LatestDocumentsQuery
from email_service.service import send_attachment_request_email


class NoCategoryError(Exception):
    pass


class NoOfficerError(Exception):
    pass


class CRViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Allegation.objects.select_related('beat', 'most_common_category')
        allegation = get_object_or_404(queryset, crid=pk)
        serializer = CRSerializer(allegation)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='complaint-summaries')
    def complaint_summaries(self, request):
        query = Allegation.objects.filter(
            summary__isnull=False
        ).exclude(
            summary__exact=''
        ).annotate(
            categories=ArrayAgg('officerallegation__allegation_category__category')
        ).only(
            'crid', 'summary', 'incident_date'
        ).order_by(F('incident_date').desc(nulls_last=True), '-crid')[:40]
        return Response(CRSummarySerializer(query, many=True).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], url_path='request-document')
    def request_document(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)
        data = deepcopy(request.data)
        data['allegation'] = allegation.pk
        serializer = AttachmentRequestSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response({'message': 'Email already added', 'crid': pk}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)
        send_attachment_request_email(data['email'], attachment_type=CR_ATTACHMENT_REQUEST, pk=pk)
        return Response({'message': 'Thanks for subscribing', 'crid': pk})

    @action(detail=False, methods=['GET'], url_path='list-by-new-document', url_name='list-by-new-document')
    def allegations_with_new_documents(self, request):
        limit = int(request.GET.get('limit', 40))
        latest_documents = LatestDocumentsQuery.execute(limit)
        serializer = AllegationWithNewDocumentsSerializer(latest_documents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='related-complaints')
    def related_complaints(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)

        request_serializer = CRRelatedComplaintRequestSerializer(data=request.GET)
        if not request_serializer.is_valid():
            return Response({'message': request_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            query_filter = {
                'geo_distance': {
                    'distance': request_serializer.validated_data['distance'],
                    'point': {
                        'lat': allegation.point.y,
                        'lon': allegation.point.x
                    }
                }
            }

            if request_serializer.validated_data['match'] == 'categories':
                categories = list(filter(None, [
                    obj.category
                    for obj in allegation.officerallegation_set.all()
                ]))
                if len(categories) == 0:
                    raise NoCategoryError()

                query = CRDocType().search().query(
                    'bool',
                    must={
                        'terms': {
                            'category_names': categories
                        }
                    },
                    must_not={
                        'terms': {'crid': [pk]}
                    },
                    filter=query_filter
                )
            elif request_serializer.validated_data['match'] == 'officers':
                officers = list(filter(None, [
                    obj.officer_id
                    for obj in allegation.officerallegation_set.all()
                ]))
                if len(officers) == 0:
                    raise NoOfficerError()

                query = CRDocType().search().query(
                    'bool',
                    must={
                        'nested': {
                            'path': 'coaccused',
                            'query': {
                                'terms': {
                                    'coaccused.id': officers
                                }
                            }
                        }
                    },
                    must_not={
                        'terms': {'crid': [pk]}
                    },
                    filter=query_filter
                )

            paginator = ESQueryPagination()
            paginated_query = paginator.paginate_es_query(query, request)
            related_complaint_serializer = CRRelatedComplaintSerializer(paginated_query, many=True)
            return paginator.get_paginated_response(related_complaint_serializer.data)

        except (NoCategoryError, NoOfficerError, AttributeError):
            return Response(OrderedDict([
                ('count', 0),
                ('next', None),
                ('previous', None),
                ('results', [])
            ]))


class CRMobileViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        queryset = Allegation.objects.select_related('beat', 'most_common_category')
        allegation = get_object_or_404(queryset, crid=pk)
        serializer = CRMobileSerializer(allegation)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], url_path='request-document', url_name='request-document')
    def request_document(self, request, pk):
        allegation = get_object_or_404(Allegation, crid=pk)
        data = deepcopy(request.data)
        data['allegation'] = allegation.pk
        serializer = AttachmentRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            send_attachment_request_email(data['email'], attachment_type=CR_ATTACHMENT_REQUEST, pk=pk)
            return Response({'message': 'Thanks for subscribing', 'crid': pk})

        except ValidationError as e:
            if e.get_codes() == {'non_field_errors': ['unique']}:
                return Response(
                    {'message': 'Email already added', 'crid': pk},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({'message': 'Please enter a valid email'}, status=status.HTTP_400_BAD_REQUEST)
