"""GPT-6 Luna uses a subscription text request, with no executable tools."""
import json

import httpx
import pytest

import harvey.codex as hc
from tests.test_codex import fake, native_home, private_tempdir, _client, PROMPT


def response_stream(*, output=None, model="gpt-6-luna", status="completed"):
    if output is None:
        output = [{"type": "message", "id": "msg-1", "role": "assistant",
                   "content": [{"type": "output_text", "text": "PONG"}]}]
    events = [{"type": "response.output_item.done", "item": item} for item in output]
    events.append({"type": "response.completed", "response": {
        "id": "resp-1", "model": model, "status": status, "output": output,
        "usage": {"input_tokens": 100, "input_tokens_details": {"cached_tokens": 20},
                  "output_tokens": 6}}})
    return "".join("data: " + json.dumps(e) + "\n\n" for e in events).encode()


@pytest.fixture
def subscription_http(monkeypatch):
    calls = []
    options = []
    result = {"status": 200, "body": response_stream()}
    original = httpx.AsyncClient

    async def handle(request):
        calls.append(request)
        return httpx.Response(result["status"], headers=result.get("headers", {"content-type": "text/event-stream"}),
                              content=result["body"])

    def client(**kwargs):
        options.append(kwargs.copy())
        return original(**kwargs, transport=httpx.MockTransport(handle))

    monkeypatch.setattr(httpx, "AsyncClient", client)
    return calls, options, result


@pytest.mark.asyncio
async def test_luna_returns_text_without_sending_prompt_to_cli(fake, native_home, subscription_http):
    calls, options, _ = subscription_http
    before = (native_home / "auth.json").read_bytes()
    client = _client(native_home, model="gpt-6-luna", reasoning_effort="medium")
    await client.preflight(timeout=10)
    assert calls == []  # health checks never infer or spend tokens
    result = await client.run(PROMPT, timeout=10)
    assert result.text == "PONG" and result.model == "gpt-6-luna"
    assert result.usage == {"input_tokens": 80, "cache_read_tokens": 20,
                            "cache_creation_tokens": 0, "output_tokens": 6}
    assert len(calls) == 1
    request = calls[0]
    assert str(request.url) == "https://chatgpt.com/backend-api/codex/responses"
    body = json.loads(request.content)
    assert body["model"] == "gpt-6-luna" and body["tools"] == []
    assert body["tool_choice"] == "none" and body["parallel_tool_calls"] is False
    assert body["store"] is False
    assert body["reasoning"]["effort"] == "medium"
    assert request.headers["ChatGPT-Account-ID"] == "acct-1"
    assert "native-refresh-token-never-leaves" not in request.content.decode()
    assert all(o["trust_env"] is False and o["follow_redirects"] is False for o in options)
    assert "turn/start" not in fake.methods()
    assert not fake.sent_prompt()
    assert (native_home / "auth.json").read_bytes() == before


@pytest.mark.asyncio
@pytest.mark.parametrize('item_type', ['function_call', 'custom_tool_call', 'web_search_call', 'code_interpreter_call'])
async def test_tool_output_is_rejected_without_a_cli_turn(fake, native_home, subscription_http, item_type):
    calls, _, response = subscription_http
    response['body'] = response_stream(output=[{'type': item_type, 'name': 'exec_command',
                                                'arguments': '{"cmd":"rm -rf ~"}'}])
    with pytest.raises(hc.CodexError) as err:
        await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert err.value.kind == 'isolation'
    assert len(calls) == 1 and 'turn/start' not in fake.methods()


@pytest.mark.asyncio
@pytest.mark.parametrize('status,kind', [(302, 'isolation'), (401, 'auth'),
                                        (403, 'auth'), (429, 'usage_limit'), (503, 'runtime')])
async def test_http_errors_are_classified_without_redirects_or_raw_bodies(
        fake, native_home, subscription_http, status, kind):
    calls, _, response = subscription_http
    response.update(status=status, body=b'secret-body-must-not-be-logged')
    with pytest.raises(hc.CodexError) as err:
        await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert err.value.kind == kind
    assert 'secret-body' not in str(err.value)
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize('body', [b'data: {bad json}\n\n', b'data: {}\n\n',
                                  b'data: [DONE]\n\n', b'data: {"type":"response.completed"}'])
async def test_malformed_or_truncated_stream_never_returns_partial_text(fake, native_home, subscription_http, body):
    _, _, response = subscription_http
    response['body'] = body
    with pytest.raises(hc.CodexError) as err:
        await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert err.value.kind == 'protocol'


@pytest.mark.asyncio
async def test_model_substitution_is_rejected(fake, native_home, subscription_http):
    _, _, response = subscription_http
    response['body'] = response_stream(model='gpt-6-sol')
    with pytest.raises(hc.CodexError) as err:
        await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert err.value.kind == 'isolation'


@pytest.mark.asyncio
@pytest.mark.parametrize('scenario', ['chatgpt_endpoint', 'provider_override', 'apikey', 'old_version'])
async def test_metadata_checks_still_block_unsafe_routes_and_accounts(fake, native_home, subscription_http, scenario):
    fake.use(scenario)
    calls, _, _ = subscription_http
    with pytest.raises(hc.CodexError):
        await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert calls == [] and not fake.sent_prompt()


@pytest.mark.asyncio
async def test_luna_must_exist_in_the_attested_catalog(fake, native_home, subscription_http, monkeypatch):
    async def catalog_without_luna(self, deadline):
        return {'gpt-5.5': {'slug': 'gpt-5.5'}}
    monkeypatch.setattr(hc._AppServer, 'read_catalog', catalog_without_luna)
    calls, _, _ = subscription_http
    with pytest.raises(hc.CodexError) as err:
        await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert err.value.kind == 'isolation' and calls == []


@pytest.mark.asyncio
async def test_subscription_stream_can_omit_content_type(fake, native_home, subscription_http):
    _, _, response = subscription_http
    response['headers'] = {}
    result = await _client(native_home, model='gpt-6-luna').run(PROMPT, timeout=10)
    assert result.text == 'PONG'
