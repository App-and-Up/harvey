"""Text-only inference on the ChatGPT subscription endpoint used by Codex.

The CLI checks the account and model before this module is called, but never
receives the prompt. Requests contain no tools; responses are data only. The
endpoint is fixed, environment proxies and redirects are disabled, and neither
refresh tokens nor API keys are used. This backend protocol is pinned to the
Codex source verified for this checkout, rather than a public API contract.
"""

import json
import time
from contextlib import aclosing
from dataclasses import dataclass, field

import httpx

from harvey.codex import CodexError, CodexResult, DEVELOPER_INSTRUCTIONS, _remaining

# Same route as codex-rs/model-provider-info/src/lib.rs at rust-v0.159.3.
CHATGPT_RESPONSES_URL = "https://chatgpt.com/backend-api/codex/responses"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_EVENT_BYTES = 1024 * 1024
TEXT_ITEM_TYPES = frozenset({"message", "reasoning", "compaction"})


def _request_error(status: int, error=None) -> CodexError:
    code = error.get("code", "") if isinstance(error, dict) else ""
    if status in (401, 403):
        return CodexError("Codex rejected the ChatGPT login. Run 'codex login'.", kind="auth")
    if status == 429 or code in ("usage_limit_reached", "rate_limit_exceeded", "insufficient_quota"):
        return CodexError("Codex usage limit reached for this ChatGPT plan.", kind="usage_limit")
    if 300 <= status < 400:
        return CodexError("ChatGPT text endpoint redirect refused.", kind="isolation")
    if status >= 500:
        return CodexError("ChatGPT text service is temporarily unavailable.", kind="runtime", retryable=True)
    return CodexError("ChatGPT refused the text request.", kind="request")


def _protocol_error() -> CodexError:
    # Never include response bodies: they can contain prompts or credentials.
    return CodexError("ChatGPT returned an incomplete or invalid text response.", kind="protocol")


def _check_item(item) -> None:
    if not isinstance(item, dict) or item.get("type") not in TEXT_ITEM_TYPES:
        raise CodexError("ChatGPT returned a tool call or a non-text item; nothing was executed.", kind="isolation")
    if item["type"] == "message":
        if item.get("role") != "assistant" or not isinstance(item.get("content"), list):
            raise _protocol_error()
        for part in item["content"]:
            if not isinstance(part, dict) or part.get("type") not in ("output_text", "refusal"):
                raise CodexError("ChatGPT returned non-text message content; nothing was executed.", kind="isolation")
            key = "text" if part["type"] == "output_text" else "refusal"
            if not isinstance(part.get(key), str):
                raise _protocol_error()


@dataclass
class _TextResponse:
    model: str
    items: list[dict] = field(default_factory=list)
    completed: dict | None = None

    def take(self, event: dict) -> None:
        kind = event.get("type", "")
        if not isinstance(kind, str):
            raise _protocol_error()
        if "function_call" in kind or "custom_tool_call" in kind:
            raise CodexError("ChatGPT attempted a tool call; nothing was executed.", kind="isolation")
        if kind in ("response.output_item.added", "response.output_item.done"):
            item = event.get("item")
            _check_item(item)
            if kind.endswith(".done"):
                self.items.append(item)
        elif kind in ("error", "response.failed", "response.incomplete"):
            response = event.get("response") or {}
            error = event.get("error") or response.get("error") or event
            raise _request_error(200, error)
        elif kind == "response.completed":
            response = event.get("response")
            if not isinstance(response, dict) or response.get("status") != "completed":
                raise _protocol_error()
            if response.get("model") != self.model:
                raise CodexError("ChatGPT returned a different model; no substitution is allowed.", kind="isolation")
            output = response.get("output", self.items)
            if not isinstance(output, list):
                raise _protocol_error()
            for item in output:
                _check_item(item)
            self.items = output
            self.completed = response

    def result(self, started: float) -> CodexResult:
        if self.completed is None:
            raise _protocol_error()
        messages = [i for i in self.items if i["type"] == "message"
                    and i.get("phase") in (None, "final_answer")]
        if any(i.get("phase") == "final_answer" for i in messages):
            messages = [i for i in messages if i.get("phase") == "final_answer"]
        text = "\n".join(part.get("text", part.get("refusal", ""))
                         for item in messages for part in item["content"]).strip()
        if not text:
            raise _protocol_error()
        usage = self.completed.get("usage") or {}
        if not isinstance(usage, dict):
            raise _protocol_error()
        details = usage.get("input_tokens_details") or {}
        if not isinstance(details, dict):
            raise _protocol_error()
        def count(value):
            return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0
        cached = count(details.get("cached_tokens"))
        return CodexResult(
            text=text, model=self.model,
            thread_id=str(self.completed.get("id") or ""),
            duration_ms=int((time.monotonic() - started) * 1000),
            usage={"input_tokens": max(count(usage.get("input_tokens")) - cached, 0),
                   "cache_read_tokens": cached,
                   "cache_creation_tokens": count(details.get("cache_write_tokens")),
                   "output_tokens": count(usage.get("output_tokens"))},
        )


async def _events(response):
    """Read bounded SSE frames, including chunk boundaries and CRLF framing."""
    buffer = b""
    total = 0
    async with aclosing(response.aiter_bytes()) as chunks:
        async for chunk in chunks:
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise _protocol_error()
            buffer += chunk
            while b"\n\n" in buffer or b"\r\n\r\n" in buffer:
                markers = [(buffer.find(m), m) for m in (b"\n\n", b"\r\n\r\n") if m in buffer]
                index, marker = min(markers)
                frame, buffer = buffer[:index], buffer[index + len(marker):]
                if len(frame) > MAX_EVENT_BYTES:
                    raise _protocol_error()
                data = b"\n".join(line[5:].lstrip(b" ") for line in frame.splitlines()
                                  if line.startswith(b"data:"))
                if not data or data == b"[DONE]":
                    continue
                try:
                    event = json.loads(data)
                except (ValueError, UnicodeError):
                    raise _protocol_error() from None
                if not isinstance(event, dict):
                    raise _protocol_error()
                yield event
            if len(buffer) > MAX_EVENT_BYTES:
                raise _protocol_error()
    if buffer.strip():
        raise _protocol_error()


async def generate_text(prompt: str, model: str, effort: str, snapshot: dict,
                        deadline: float) -> CodexResult:
    """A single text response, after CodexClient has attested account/catalog."""
    started = time.monotonic()
    tokens = snapshot["tokens"]
    headers = {"Authorization": "Bearer " + tokens["access_token"],
               "Content-Type": "application/json", "Accept": "text/event-stream",
               "User-Agent": "harvey/0.3.0", "originator": "harvey"}
    if tokens.get("account_id"):
        headers["ChatGPT-Account-ID"] = tokens["account_id"]
    payload = {"model": model, "instructions": DEVELOPER_INSTRUCTIONS,
               "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}],
               "tools": [], "tool_choice": "none", "parallel_tool_calls": False,
               "store": False, "stream": True}
    if effort:
        payload["reasoning"] = {"effort": effort}
    turn = _TextResponse(model)
    try:
        async with httpx.AsyncClient(trust_env=False, follow_redirects=False,
                                     timeout=_remaining(deadline)) as client:
            async with client.stream("POST", CHATGPT_RESPONSES_URL,
                                     json=payload, headers=headers) as response:
                if response.status_code != 200:
                    raise _request_error(response.status_code)
                # The subscription backend can omit Content-Type even for a
                # valid SSE stream. Validate the bounded events themselves.
                async with aclosing(_events(response)) as events:
                    async for event in events:
                        turn.take(event)
                        if turn.completed is not None:
                            break
    except httpx.TimeoutException:
        raise CodexError("Codex text call timed out.", kind="timeout", retryable=True) from None
    except httpx.HTTPError:
        raise CodexError("Codex text connection failed.", kind="runtime", retryable=True) from None
    return turn.result(started)
