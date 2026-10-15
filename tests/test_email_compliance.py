"""Mail footer delivery and reply interpretation at the native mail boundary."""
from types import SimpleNamespace

import pytest

from harvey.integrations.mail_provider import InboundMessage
from tests.test_outbox_native import (
    state, FakeProvider, make_handler, make_sender, seed_prospect, _now_iso,
)


async def queue(state, pid, *, kind="sequence", step=1, body="Una domanda sul vostro sito."):
    return await state.add_outbox_item(
        prospect_id=pid, to_email="jane@acme.com", subject="Una domanda",
        body=body, send_at=_now_iso(), status="approved", campaign_id="c1",
        step=step, kind=kind,
    )


@pytest.mark.asyncio
async def test_footer_is_sent_once_and_stored_with_actual_body(state):
    pid = await seed_prospect(state)
    provider = FakeProvider()
    sender = make_sender(state, provider)
    sender.config.compliance = SimpleNamespace(
        postal_address="Via Roma 1, Milano", opt_out_line='Rispondi "no grazie" per non ricevere altre email.',
    )
    body = "Una domanda sul sito.\n\nVia Roma 1, Milano"
    oid = await queue(state, pid, body=body)
    await sender._drain_due()
    sent = await state.get_outbox_item(oid)
    assert sent["status"] == "sent"
    assert sent["body"] == provider.sent[0]["body"]
    assert sent["body"].count("Via Roma 1, Milano") == 1
    assert sent["body"].count(sender.config.compliance.opt_out_line) == 1


@pytest.mark.asyncio
async def test_missing_address_holds_sequences_but_not_replies_behind_backlog(state):
    pid = await seed_prospect(state)
    provider = FakeProvider()
    sender = make_sender(state, provider)
    sender.config.compliance = SimpleNamespace(postal_address="", opt_out_line="No grazie")
    for step in range(1, 26):
        await queue(state, pid, step=step)
    reply = await queue(state, pid, kind="reply", body="Ecco la risposta.")
    await sender._drain_due()
    assert len(provider.sent) == 1
    assert provider.sent[0]["body"] == "Ecco la risposta."
    assert (await state.get_outbox_item(reply))["status"] == "sent"
    assert len(await state.get_outbox(status="approved")) == 25
    sender.config.compliance.postal_address = "Via Roma 1, Milano"
    await sender._drain_due()
    assert len(provider.sent) > 1


@pytest.mark.asyncio
@pytest.mark.parametrize("quote", [
    'On Wed, Oct 14, 2026 at 10:00 Harvey wrote:\nNo thanks',
    'Il giorno 14 ott 2026,\nHarvey ha scritto:\nNo grazie',
    'Da: Harvey\nInviato: mercoledì 14 ottobre 2026\nNo grazie',
    '-----Messaggio originale-----\nNo grazie',
    '> No grazie',
])
async def test_quoted_opt_out_does_not_override_prospects_question(state, quote):
    pid = await seed_prospect(state, status="contacted")
    provider = FakeProvider()
    provider.inbound = [InboundMessage(
        provider_id="reply-1", from_email="jane@acme.com",
        subject="Re: Una domanda", body="Quanto costa?\n\n" + quote,
    )]
    await make_handler(state, provider, intent="question")._run_native()
    assert (await state.get_prospect(pid)).status != "opted_out"
    conversations = await state.get_conversations_by_status("open")
    assert len(conversations) == 1
    assert conversations[0].thread[0].content == "Quanto costa?"
    assert len(await state.get_outbox(status="pending_review")) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("body", ["No grazie", "Non contattatemi", "no thanks"])
async def test_direct_opt_out_is_honored_without_trusting_classifier(state, body):
    pid = await seed_prospect(state, status="contacted")
    provider = FakeProvider()
    provider.inbound = [InboundMessage(
        provider_id="opt-out-1", from_email="jane@acme.com", body=body,
    )]
    await make_handler(state, provider, intent="question")._run_native()
    assert (await state.get_prospect(pid)).status == "opted_out"
    assert not await state.get_outbox()
