__version__ = '0.2.8'
import os
from typing import Optional

import argparse
from .lambda_requests import LambdaRequests
from .dynamo import DynamoDB
from .redis_cache import RedisCache

def main():
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-lambda_project_name', '--lambda_project_name', default=None, type=str, help='arg1')
    parser.add_argument('-base_image', '--base_image', default='amazon/aws-lambda-python:3.11', type=str, help='arg1')
    args = parser.parse_args()
    lambda_project_name = args.lambda_project_name
    if lambda_project_name is not None:
        create_lambda_project(lambda_project_name, args)

def create_lambda_project(lambda_project_name, args):
    from .templates.lambda_template import (
        error_script,
        lambda_function_script,
        api_script,
        docker_file_script,
        setup_script,
        github_actions_script,
        gitignore_script,
        utils_script
    )
    base_image = args.base_image
    os.makedirs(f'./{lambda_project_name}', exist_ok=True)
    os.makedirs(f'./{lambda_project_name}/modules', exist_ok=True)
    os.makedirs(f'./{lambda_project_name}/router', exist_ok=True)
    os.makedirs(f'./{lambda_project_name}/.github/workflows', exist_ok=True)
    with open(f'./{lambda_project_name}/README.md', 'w') as f:
        f.write(f'# {lambda_project_name}\n')
    with open(f'./{lambda_project_name}/lambda_function.py', 'w') as f:
        f.write(lambda_function_script)
    with open(f'./{lambda_project_name}/modules/error.py', 'w') as f:
        f.write(error_script)
    with open(f'./{lambda_project_name}/modules/utils.py', 'w') as f:
        f.write(utils_script)
    with open(f'./{lambda_project_name}/router/api.py', 'w') as f:
        f.write(api_script)
    with open(f'./{lambda_project_name}/Dockerfile', 'w') as f:
        f.write(docker_file_script.format(base_image))
    with open(f'./{lambda_project_name}/modules/setup.py', 'w') as f:
        f.write(setup_script)
    with open(f'./{lambda_project_name}/.github/workflows/aws.yml', 'w') as f:
        f.write(github_actions_script.format(lambda_project_name))
    with open(f'./{lambda_project_name}/.gitignore', 'w') as f:
        f.write(gitignore_script)