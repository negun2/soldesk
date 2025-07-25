# onpremweb_aws/community/views_presigned.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import boto3
import uuid

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def s3_presigned_upload(request):
    file_name = request.data['file_name']
    file_type = request.data['file_type']
    s3_key = f"user_uploads/{request.user.id}/{uuid.uuid4()}_{file_name}"
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    url = s3.generate_presigned_url(
        ClientMethod='put_object',
        Params={
            'Bucket': settings.AWS_S3_BUCKET,
            'Key': s3_key,
            'ContentType': file_type,
            #'ACL': 'public-read'
        },
        ExpiresIn=300,
        HttpMethod='PUT'
    )
    return Response({'url': url, 's3_url': f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"})
