"""Backend for All OpenAI Compatable API"""

import json
import logging
import time
import os
from .utils import FunctionSpec, OutputType, opt_messages_to_list, backoff_create
from funcy import notnone, once, select_values
import openai
# from pprint import pprint

logger = logging.getLogger(__name__)

_client: openai.OpenAI = None  # type: ignore
api_key = os.getenv("API_KEY") # set openai api key
base_url = os.getenv("BASE_URL")
# api_key = os.environ['API_KEY']
# base_url = os.environ['BASE_URL']

OPENAI_TIMEOUT_EXCEPTIONS = (
    openai.RateLimitError,
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.InternalServerError,
)

def _setup_openai_client(base_url, api_key=api_key):
    global _client
    _client = openai.OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

def clean_json_response(response_text: str) -> str:
    # 移除 markdown 的 ```json 和 ``` 标记
    response_text = response_text.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    elif response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    return response_text.strip()


def query(
    system_message: str | None,
    user_message: str | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> dict:
    _setup_openai_client(api_key=api_key, base_url=base_url)
    filtered_kwargs: dict = select_values(notnone, model_kwargs)
    response = _client.chat.completions.create(
        model=model_kwargs["model"],
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": system_message}
        ]
    )
    reasoning_content = response.choices[0].message.reasoning_content
    content = response.choices[0].message.content
    output = {
        "reasoning": reasoning_content,
        "content": content
    }
    return  output["content"]


def batch_query(
    system_messages: list[str] | None,
    user_messages: list[str] | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> list[dict]:
    """
    Batch query the DeepSeek API.
    """
    if system_messages and user_messages and len(system_messages) != len(user_messages):
        raise ValueError("system_messages and user_messages must have the same length")
    
    num_queries = len(system_messages) if system_messages else len(user_messages)
    
    results = []
    for i in range(num_queries):
        system_msg = system_messages[i] if system_messages else None
        user_msg = user_messages[i] if user_messages else None
        
        # 循环调用单次查询
        result = query(
            system_message=system_msg,
            user_message=user_msg,
            func_spec=func_spec,
            **model_kwargs
        )
        results.append(result)
        
    return results
