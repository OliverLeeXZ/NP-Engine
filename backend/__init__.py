from . import backend_api_all, backend_api_ds
from .utils import FunctionSpec, OutputType, PromptType, compile_prompt_to_md


def query(
    system_message: PromptType | None,
    user_message: PromptType | None,
    model: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
) -> OutputType:
    """
    General LLM query for various backends with a single system and user message.
    Supports function calling for some backends.

    Args:
        system_message (PromptType | None): Uncompiled system message (will generate a message following the OpenAI/Anthropic format)
        user_message (PromptType | None): Uncompiled user message (will generate a message following the OpenAI/Anthropic format)
        model (str): string identifier for the model to use (e.g. "gpt-4-turbo")
        temperature (float | None, optional): Temperature to sample at. Defaults to the model-specific default.
        max_tokens (int | None, optional): Maximum number of tokens to generate. Defaults to the model-specific max tokens.
        func_spec (FunctionSpec | None, optional): Optional FunctionSpec object defining a function call. If given, the return value will be a dict.

    Returns:
        OutputType: A string completion if func_spec is None, otherwise a dict with the function call details.
    """

    model_kwargs = model_kwargs | {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # Handle models with beta limitations
    # ref: https://platform.openai.com/docs/guides/reasoning/beta-limitations
    if model.startswith("o"):
        if system_message:
            user_message = system_message
        system_message = None
        model_kwargs["temperature"] = 1

    if "deepseek" in model.lower() or "qwen3" in model.lower():
        query_func = backend_api_ds.query
        output = query_func(
            system_message=compile_prompt_to_md(system_message) if system_message else None,
            user_message=compile_prompt_to_md(user_message) if user_message else None,
            func_spec=func_spec,
            **model_kwargs,
            )
    else:
        query_func = backend_api_all.query
        output, req_time, in_tok_count, out_tok_count, info = query_func(
            system_message=compile_prompt_to_md(system_message) if system_message else None,
            user_message=compile_prompt_to_md(user_message) if user_message else None,
            func_spec=func_spec,
            **model_kwargs,
        )

    return output


def batch_query(
    system_messages: list[str] | None,
    user_messages: list[str] | None,
    func_spec: FunctionSpec | None = None,
    **model_kwargs,
):
    """
    Query the OpenAI API, optionally with function calling.
    If the model doesn't support function calling, gracefully degrade to text generation.
    """
    model = model_kwargs.get("model", None)
    if not model:
        raise ValueError("model must be specified in model_kwargs")

    if "deepseek" in model.lower() or "qwen3" in model.lower():
        query_func = backend_api_ds.batch_query
        return query_func(
            system_messages=[compile_prompt_to_md(s) if s else None for s in system_messages] if system_messages else None,
            user_messages=[compile_prompt_to_md(u) if u else None for u in user_messages] if user_messages else None,
            func_spec=func_spec,
            **model_kwargs,
        )
    else:
        query_func = backend_api_all.batch_query
        return query_func(
            system_messages=[compile_prompt_to_md(s) if s else None for s in system_messages] if system_messages else None,
            user_messages=[compile_prompt_to_md(u) if u else None for u in user_messages] if user_messages else None,
            func_spec=func_spec,
            **model_kwargs,
        )
