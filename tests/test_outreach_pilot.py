"""A pilot bounds new companies across workers, days and contacts."""

import asyncio
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from pydantic import ValidationError

from harvey.config import EmailChannelConfig, OutreachPilotConfig
from harvey.models.company import Company
from harvey.outreach import OutreachPilot
from harvey.state import StateManager
from tests.test_outbox_native import FakeProvider, make_sender, seed_prospect


@pytest_asyncio.fixture
async def state(tmp_path):
    state = StateManager(str(tmp_path / 'pilot.db'))
    await state.init_db()
    return state


def pilot(state, **overrides):
    return OutreachPilot(state, OutreachPilotConfig(enabled=True, min_interval_minutes=0,
                          **overrides), 'Europe/Rome')


def company(i):
    return Company(id=f'c{i}', name=f'Company {i}', domain=f'company{i}.example')


@pytest.mark.asyncio
async def test_twenty_slots_are_atomic_across_workers(state):
    a, b = pilot(state), pilot(state)
    results = await asyncio.gather(*[
        (a if i % 2 else b).reserve(company(i), f'o{i}') for i in range(25)
    ])
    assert results.count('') == 20
    assert results.count('daily_limit') == 5


@pytest.mark.asyncio
async def test_same_company_cannot_be_recontacted_next_day_or_by_another_contact(state):
    p = pilot(state)
    now = datetime(2026, 10, 14, 10, tzinfo=timezone.utc)
    assert await p.reserve(company(1), 'first', now=now) == ''
    await p.finish('first', success=True)
    alias = Company(id='another-id', domain='WWW.Company1.example')
    assert await p.reserve(alias, 'another-contact', now=now + timedelta(days=1)) == 'already_reserved'


@pytest.mark.asyncio
async def test_fourteen_calendar_days_and_no_catchup(state):
    p = pilot(state, daily_new_companies=1)
    now = datetime(2026, 10, 14, 10, tzinfo=timezone.utc)
    assert await p.reserve(company(1), 'first', now=now) == ''
    assert await p.reserve(company(2), 'next', now=now + timedelta(days=12)) == ''
    assert await p.reserve(company(3), 'overdaily', now=now + timedelta(days=12)) == 'daily_limit'
    assert await p.reserve(company(4), 'last', now=now + timedelta(days=13)) == ''
    assert await p.reserve(company(5), 'expired', now=now + timedelta(days=14)) == 'expired'


@pytest.mark.asyncio
async def test_days_use_rome_midnight_not_utc(state):
    p = pilot(state, daily_new_companies=1)
    before = datetime(2026, 10, 14, 21, 59, tzinfo=timezone.utc)
    assert await p.reserve(company(1), 'first', now=before) == ''
    assert await p.reserve(company(2), 'next', now=before + timedelta(minutes=2)) == ''


@pytest.mark.asyncio
async def test_pacing_and_restart_preserve_claim(state):
    config = OutreachPilotConfig(enabled=True, min_interval_minutes=20)
    p = OutreachPilot(state, config, 'Europe/Rome')
    now = datetime(2026, 10, 14, 10, tzinfo=timezone.utc)
    assert await p.reserve(company(1), 'first', now=now) == ''
    restarted = OutreachPilot(StateManager(state.db_path), config, 'Europe/Rome')
    assert await restarted.reserve(company(1), 'retry', now=now) == 'already_reserved'
    assert await restarted.reserve(company(2), 'next', now=now + timedelta(minutes=19)) == 'interval'
    assert await restarted.reserve(company(2), 'next', now=now + timedelta(minutes=20)) == ''


@pytest.mark.asyncio
async def test_missing_company_is_not_counted_as_new_company(state):
    assert await pilot(state).reserve(None, 'unknown') == 'unknown_company'


def test_pilot_rejects_unenforced_provider_and_invalid_limits():
    with pytest.raises(ValidationError):
        EmailChannelConfig(provider='instantly', pilot={'enabled': True})
    with pytest.raises(ValidationError):
        OutreachPilotConfig(duration_days=0)


@pytest.mark.asyncio
async def test_sender_enforces_company_rule_and_suppresses_followup(state):
    sender = make_sender(state, FakeProvider(), require_approval=False)
    sender.pilot = pilot(state)
    c = company(1)
    await state.add_company(c)
    for index in range(2):
        pid = await seed_prospect(state, email=f'p{index}@company1.example')
        async with state._connect() as db:
            await db.execute('UPDATE prospects SET company_id = ? WHERE id = ?', (c.id, pid))
            await db.commit()
        for step in (1, 2):
            await state.add_outbox_item(prospect_id=pid, campaign_id=f'campaign{index}',
                                        step=step, to_email=f'p{index}@company1.example',
                                        subject='ordini dei clienti', body='Come raccogliete gli ordini?',
                                        send_at='2020-01-01', status='approved')
    await sender._drain_due()
    assert len(sender.provider.sent) == 1
    assert len(await state.get_outbox(status='cancelled')) == 3


@pytest.mark.asyncio
async def test_reply_is_allowed_even_when_pilot_expired(state):
    import json
    p = pilot(state)
    sender = make_sender(state, FakeProvider())
    sender.pilot = p
    await state.set_setting(p.key, json.dumps({'started_on': '2000-01-01', 'companies': {}}))
    pid = await seed_prospect(state, status='replied')
    await state.add_outbox_item(prospect_id=pid, campaign_id='reply-campaign', step=0,
                               to_email='jane@acme.com', subject='risposta alla domanda',
                               body='Quale listino usate?', send_at='2020-01-01',
                               kind='reply', status='approved')
    await sender._drain_due()
    assert len(sender.provider.sent) == 1


@pytest.mark.asyncio
async def test_entire_pilot_allows_280_distinct_companies_then_stops(state):
    p = pilot(state)
    start = datetime(2026, 10, 14, 10, tzinfo=timezone.utc)
    for day in range(14):
        for index in range(20):
            i = day * 20 + index
            assert await p.reserve(company(i), f'o{i}', now=start + timedelta(days=day)) == ''
            await p.finish(f'o{i}', success=True)
        assert await p.reserve(company(1000 + day), f'extra{day}',
                               now=start + timedelta(days=day)) == 'daily_limit'
    assert await p.reserve(company(9999), 'after', now=start + timedelta(days=14)) == 'expired'


@pytest.mark.asyncio
async def test_ambiguous_provider_failure_keeps_company_reserved(state):
    sender = make_sender(state, FakeProvider())
    sender.pilot = pilot(state)
    c = company(1)
    await state.add_company(c)
    pid = await seed_prospect(state)
    async with state._connect() as db:
        await db.execute('UPDATE prospects SET company_id = ? WHERE id = ?', (c.id, pid))
        await db.commit()
    await state.add_outbox_item(prospect_id=pid, campaign_id='first', step=1,
                               to_email='jane@acme.com', subject='ordini dei clienti',
                               body='Come raccogliete gli ordini?', send_at='2020-01-01',
                               status='approved')
    sender.provider.fail_next = True
    await sender._drain_due()
    assert not sender.provider.sent
    assert await sender.pilot.reserve(c, 'blind-retry') == 'already_reserved'


@pytest.mark.asyncio
async def test_staging_pilot_suppresses_scheduled_followups(state):
    from tests.test_outbox_native import seed_campaign
    sender = make_sender(state, FakeProvider())
    sender.pilot = pilot(state)
    pid = await seed_prospect(state)
    campaign = await seed_campaign(state, [pid])
    await sender._stage_campaign_native(campaign)
    assert [r['step'] for r in await state.get_outbox(status='pending_review')] == [1]
