# AWS Tools
파이썬 개발용 AWS 라이브러리입니다.

## Installation
```bash
pip install redis fastapi numpy tqdm boto3
pip install git+https://github.com/kr-eunil-jung/awstools.git
```

## Update Logs
- 2024.01.03

    - first commit
    - lambda_requests, question_dynamo, redis 탑재

- 2024.01.08

    - dynamodb, lambda endpoint 추가

- 2024.01.09

    - lambda timeout 재시도 비활성화

- 2024.03.12

    - lambda project template 생성 기능 추가

## Quick start
- lambda 프로젝트 생성

    1) 필수 인자
        - lambda_project_name: 생성할 프로젝트 이름
        ```bash
        awstools -lambda_project_name {prjoect_name}
        ```

    2) 옵션 인자
        - base_image: 빌드할 기본 컨테이너 이미지(기본값: amazon/aws-lambda-python:3.11)
        ```bash
        awstools -lambda_project_name {prjoect_name} -base_image {container_base_image}
        ```

- lambda_requests
    ```py
    from awstools import LambdaRequests

    requests = LambdaRequests(
        aws_access_key_id = {your_aws_secret_access_key},
        aws_secret_access_key = {your_aws_secret_access_key}
    )

    response = requests.get(
        function_name={function_name},
        http_path={http_path},
        params={params}
    )

    response = requests.post(
        function_name={function_name},
        http_path={http_path},
        data={data}
    )

    response = requests.put(
        function_name={function_name},
        http_path={http_path},
        data={data}
    )
    ```

- dynamo
    ```py
    from awstools import DynamoDB
    
    dynamo = DynamoDB(
        aws_access_key_id = {your_aws_secret_access_key},
        aws_secret_access_key = {your_aws_secret_access_key}
    )

    dynamo.put_item(
        item_id = {item_id},
        add_item = {add_item},
        table = {table},
        app = {app}
    )

    item = dynamo.get_item(
        item_id = {item_id},
        table = {table},
        app = {app}
    )

    items = dynamo.get_batch_items(
        item_id_list = {item_id_list},
        table = {table},
        app = {app}
    )
    ```

- redis
    ```py
    from awstools import RedisCache
    
    redis = RedisCache(
        host = {your_redis_host},
        port = {your_redis_port}
    )

    redis.init()

    redis.set_cache(
        key = {your_cache_key},
        value = {your_cache_value}
    )

    data = redis.get_cache(
        key = {your_cache_key},
        value = {your_cache_value}
    )

    redis.delete_cache(
        key = {youre_cache_key}
    )

    redis.delete_cache_by_pattern(
        pattern = {your_key_pattern_to_delete}
    )

    redis.shutdown()
    ```