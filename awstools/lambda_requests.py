from typing import Dict, Any, Optional
import boto3
from botocore.config import Config
import json


class RequestsOutput:
    def __init__(
        self,
        status_code: int,
        body: Any
    ):
        self.status_code = status_code
        self.body = body
    
    def json(self):
        return self.body


class LambdaRequests:
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str = 'ap-northeast-2',
        use_endpoint: bool = False
    ):
        no_retry_config = Config(
            read_timeout=900,
            connect_timeout=900,
            retries = {
                'max_attempts': 0,  # 재시도 비활성화
            }
        )
        if use_endpoint:
            self.lambda_client = boto3.client(
                'lambda',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
                endpoint_url='https://lambda.ap-northeast-2.amazonaws.com',
                config=no_retry_config
            )
        else:
            self.lambda_client = boto3.client(
                'lambda',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=region_name,
                config=no_retry_config
            )

    def _requests(
        self,
        function_name: str,
        event: Dict[str, Any],
        invocation_type: str = 'RequestResponse'
    ) -> RequestsOutput:
        if invocation_type == 'RequestResponse':
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(event)
            )['Payload'].read()
            response = json.loads(response)
            status_code = response['statusCode']
            try:
                body = json.loads(response['body'])
            except:
                body = response['body']
            return RequestsOutput(
                status_code=status_code,
                body=body
            )
        elif invocation_type == 'Event':
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType=invocation_type,
                Payload=json.dumps(event)
            )
            return RequestsOutput(
                status_code=201,
                body=''
            )
        else:
            raise Exception('invocation_type error')
    
    def get(
        self,
        function_name: str,
        http_path: str,
        params: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        invocation_type: str = 'RequestResponse'
    ) -> RequestsOutput:
        event = {
            "requestContext": {
                "http": {
                    "method": "GET",
                    "path": http_path
                }
            },
            "queryStringParameters": params
        }
        if headers is not None:
            event['headers'] = headers
        response = self._requests(
            function_name=function_name,
            event=event,
            invocation_type=invocation_type
        )
        return response
    
    def post(
        self,
        function_name: str,
        http_path: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        invocation_type: str = 'RequestResponse'
    ) -> RequestsOutput:
        event = {
            "requestContext": {
                "http": {
                    "method": "POST",
                    "path": http_path
                }
            },
            "body": json.dumps(data)
        }
        if headers is not None:
            event['headers'] = headers
        response = self._requests(
            function_name=function_name,
            event=event,
            invocation_type=invocation_type
        )
        return response
    
    def put(
        self,
        function_name: str,
        http_path: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, Any]] = None,
        invocation_type: str = 'RequestResponse'
    ) -> RequestsOutput:
        event = {
            "requestContext": {
                "http": {
                    "method": "PUT",
                    "path": http_path
                }
            },
            "body": json.dumps(data)
        }
        if headers is not None:
            event['headers'] = headers
        response = self._requests(
            function_name=function_name,
            event=event,
            invocation_type=invocation_type
        )
        return response