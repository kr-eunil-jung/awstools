error_script = '''class CustomError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)'''

lambda_function_script = '''import json
import traceback

from modules.error import CustomError
from router.api import (
    healthcheck
)

get_router = {
    "/": healthcheck
}

post_router = {
}

put_router = {
}

routers = list(get_router.keys()) + list(post_router.keys()) + list(put_router.keys())

def handler(event, context):
    print(event)
    try:
        http = event['requestContext']['http']
        method = http['method']
        path = http['path']
        if path[-1] != '/':
            path += '/'
        try:
            if path not in routers:
                raise CustomError(405, "Method Not Allowed")
        except CustomError as ce:
            return {
                "statusCode": ce.status_code,
                "body": ce.message
            }
        except Exception as e:
            print(traceback.format_exc())
            return {
                "statusCode": 400,
                "body": str(traceback.format_exc())
            }
        if method == 'GET':
            res = get_router[path](event, context)
            return {
                "statusCode": 200,
                "body": json.dumps(res)
            }
        elif method == 'POST':
            res = post_router[path](event, context)
            return {
                "statusCode": 201,
                "body": json.dumps(res)
            }
        elif method == 'PUT':
            res = put_router[path](event, context)
            return {
                "statusCode": 200,
                "body": json.dumps(res)
            }
    except CustomError as ce:
        return {
            "statusCode": ce.status_code,
            "body": ce.message
        }
    except Exception as e:
        print(traceback.format_exc())
        return {
            "statusCode": 400,
            "body": str(traceback.format_exc())
        }'''

utils_script = '''import os
import boto3

AWS_LAMBDA_ACCESS_KEY = os.environ.get('AWS_LAMBDA_ACCESS_KEY')
AWS_LAMBDA_SECRET_KEY = os.environ.get('AWS_LAMBDA_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('DEFAULT_REGION')
AWS_S3_ACCESS_KEY = os.environ.get('AWS_S3_ACCESS_KEY')
AWS_S3_SECRET_KEY = os.environ.get('AWS_S3_SECRET_KEY')
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')

lambda_client = boto3.client(
    'lambda',
    aws_access_key_id = AWS_LAMBDA_ACCESS_KEY,
    aws_secret_access_key = AWS_LAMBDA_SECRET_KEY,
    region_name = AWS_DEFAULT_REGION,
    endpoint_url='https://lambda.ap-northeast-2.amazonaws.com'
)

s3_client = boto3.client(
    's3', 
    aws_access_key_id=AWS_S3_ACCESS_KEY,
    aws_secret_access_key=AWS_S3_SECRET_KEY,
    region_name=AWS_DEFAULT_REGION,
    endpoint_url='https://s3.ap-northeast-2.amazonaws.com'
)
'''

api_script = '''

def healthcheck(event, context):
    return 'hello world'
'''

setup_script = '''import boto3
import os

AWS_DEFAULT_REGION = os.environ.get('DEFAULT_REGION')
AWS_S3_ACCESS_KEY = os.environ.get('AWS_S3_ACCESS_KEY')
AWS_S3_SECRET_KEY = os.environ.get('AWS_S3_SECRET_KEY')
AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')

"""
example:
    download_list = [
        dict(
            object_path=os.environ.get('DETECT_MODEL_BEST_WEIGHTS_PATH'),
            save_name= './weights/best.onnx'
        )
    ]
"""
download_list = [
]

def download_file_from_s3():
    if download_list:
        s3_client = boto3.client(
            's3', 
            aws_access_key_id=AWS_S3_ACCESS_KEY,
            aws_secret_access_key=AWS_S3_SECRET_KEY,
            region_name=AWS_DEFAULT_REGION
        )
        for download_target in download_list:
            if len(download_target['save_name'].split('/')) > 1:
                os.makdirs('/'.join(download_target['save_name'].split('/')[:-1]), exist_ok=True)
            s3_client.download_file(AWS_S3_BUCKET, download_target['object_path'], download_target['save_name'])

if __name__ == "__main__":
    download_file_from_s3()'''

docker_file_script = '''FROM {}

ARG AWS_LAMBDA_ACCESS_KEY
ARG AWS_LAMBDA_SECRET_ACCESS_KEY
ARG DEFAULT_REGION
ARG AWS_S3_ACCESS_KEY
ARG AWS_S3_SECRET_KEY
ARG AWS_S3_BUCKET

ENV AWS_LAMBDA_ACCESS_KEY ${{AWS_LAMBDA_ACCESS_KEY}}
ENV AWS_LAMBDA_SECRET_ACCESS_KEY ${{AWS_LAMBDA_SECRET_ACCESS_KEY}}
ENV DEFAULT_REGION ${{DEFAULT_REGION}}
ENV AWS_S3_ACCESS_KEY ${{AWS_S3_ACCESS_KEY}}
ENV AWS_S3_SECRET_KEY ${{AWS_S3_SECRET_KEY}}
ENV AWS_S3_BUCKET ${{AWS_S3_BUCKET}}

RUN pip install --upgrade pip
RUN pip install boto3

WORKDIR /var/task/
COPY . /var/task/

RUN python ./modules/setup.py

CMD ["lambda_function.handler"]'''

github_actions_script = '''name: Deploy to Amazon ECR

on:
  push:
    branches: [ "main" ]

env:
  DEFAULT_REGION: ${{{{ secrets.DEFAULT_REGION}}}}
  AWS_S3_ACCESS_KEY: ${{{{ secrets.AWS_S3_ACCESS_KEY}}}}
  AWS_S3_SECRET_KEY: ${{{{ secrets.AWS_S3_SECRET_KEY}}}}
  AWS_S3_BUCKET: ${{{{ secrets.AWS_S3_BUCKET}}}}
  AWS_ECR_ACCESS_KEY: ${{{{ secrets.AWS_ECR_ACCESS_KEY}}}}
  AWS_ECR_SECRET_ACCESS_KEY: ${{{{ secrets.AWS_ECR_SECRET_ACCESS_KEY}}}}
  AWS_LAMBDA_ACCESS_KEY_ID: ${{{{ secrets.AWS_LAMBDA_ACCESS_KEY_ID}}}}
  AWS_LAMBDA_SECRET_ACCESS_KEY: ${{{{ secrets.AWS_LAMBDA_SECRET_ACCESS_KEY}}}}
  LAMBDA_FUNCTION: ${{{{ secrets.LAMBDA_FUNCTION}}}}
  
  AWS_REGION: ap-northeast-2
  ECR_REPOSITORY: {}

permissions:
  contents: read

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    environment: production

    steps:
    - name: Checkout
      uses: actions/checkout@v3

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{{{ secrets.AWS_ECR_ACCESS_KEY }}}}
        aws-secret-access-key: ${{{{ secrets.AWS_ECR_SECRET_ACCESS_KEY }}}}
        aws-region: ${{{{ env.DEFAULT_REGION }}}}

    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1

    - name: Build, tag, and push image to Amazon ECR
      id: build-image
      env:
        ECR_REGISTRY: ${{{{ steps.login-ecr.outputs.registry }}}}
        IMAGE_TAG: ${{{{ github.sha }}}}
      run: |
        # Build a docker container and
        # push it to ECR so that it can
        # be deployed to ECS.
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG . \\
        --build-arg DEFAULT_REGION=$DEFAULT_REGION \\
        --build-arg AWS_S3_ACCESS_KEY=$AWS_S3_ACCESS_KEY \\
        --build-arg AWS_S3_SECRET_KEY=$AWS_S3_SECRET_KEY \\
        --build-arg AWS_S3_BUCKET=$AWS_S3_BUCKET \\
        --build-arg AWS_LAMBDA_ACCESS_KEY=$AWS_LAMBDA_ACCESS_KEY_ID \\
        --build-arg AWS_LAMBDA_SECRET_ACCESS_KEY=$AWS_LAMBDA_SECRET_ACCESS_KEY
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        echo "image=$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" >> $GITHUB_OUTPUT

    - name: Deploy to Lambda
      env:
        AWS_REGION: ${{{{ env.AWS_REGION }}}}
        AWS_ACCESS_KEY_ID: ${{{{ env.AWS_LAMBDA_ACCESS_KEY_ID }}}}
        AWS_SECRET_ACCESS_KEY: ${{{{ env.AWS_LAMBDA_SECRET_ACCESS_KEY }}}}
      run: |
        aws lambda update-function-code --function-name ${{{{ env.LAMBDA_FUNCTION }}}} --image-uri ${{{{ steps.build-image.outputs.image }}}}'''

gitignore_script = '''*.pyc
__pycache__/'''