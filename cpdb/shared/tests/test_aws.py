import importlib

from django.test import SimpleTestCase

from robber import expect
from moto import mock_s3, mock_lambda

from shared import aws


class AWSTestCase(SimpleTestCase):
    @mock_s3
    @mock_lambda
    def test_aws_lazy_init_s3_and_lambda_client(self):
        importlib.reload(aws)
        aws_object = aws.aws
        expect(aws_object._s3).to.be.none()
        expect(aws_object._lambda_client).to.be.none()

        s3 = aws_object.s3
        lambda_client = aws_object.lambda_client

        expect(aws_object._s3).to.be.eq(s3)
        expect(aws_object._lambda_client).to.be.eq(lambda_client)

        s3_2 = aws_object.s3
        lambda_client_2 = aws_object.lambda_client
        expect(id(s3_2)).to.be.eq(id(s3))
        expect(id(lambda_client_2)).to.be.eq(id(lambda_client))
