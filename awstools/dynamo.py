from typing import List, Dict, Any
import boto3
import math
import numpy as np
from tqdm import tqdm


class DynamoDB():
    def __init__(
        self,
        aws_access_key_id:str,
        aws_secret_access_key: str,
        region_name: str = "ap-northeast-2",
        use_endpoint: bool = False
    ):
        if use_endpoint:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                endpoint_url='https://dynamodb.ap-northeast-2.amazonaws.com'
            )
        else:
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
    
    def put_item(
        self,
        item_id: int,
        add_item: Dict[str, Any],
        table: str,
        app: str
    ):
        table = self.dynamodb.Table(table)
        item = {
            'app': app,
            'num': item_id
        }
        item.update(add_item)
        table.put_item(
            Item=item
        )
    
    def get_item(
        self,
        item_id: int,
        table: str,
        app: str
    ):
        table = self.dynamodb.Table(table)
        response = table.get_item(
            Key={
                'app': app,
                'num': item_id
            }
        )
        if 'Item' in response:
            question = response['Item']
            self._post_process(question)
            return question
        else:
            return None
    
    def get_batch_items(
        self,
        item_id_list: List[int],
        table: str,
        app: str,
        use_tqdm: bool = False
    ):
        jobs = np.array_split(
            item_id_list, math.ceil(len(item_id_list)/100)
        )
        results = list()
        if use_tqdm:
            jobs = tqdm(jobs)
        for job in jobs:
            batch_keys = {
                table: {
                    'Keys': [{'app': app, 'num': int(item_id)} for item_id in job]
                }
            }
            response = self.dynamodb.batch_get_item(
                RequestItems=batch_keys
            )
            response = response['Responses'][table]
            for question in response:
                self._post_process(question)
            results.extend(response)
        return results

    def _post_process(self, question: Dict[str, Any]):
        if 'num' in question.keys():
            question['num'] = int(question['num'])