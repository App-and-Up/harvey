"""Persistent company reservations for a bounded native outreach pilot.

A reservation survives a crash so an ambiguous send is never retried blindly.
Only a definitive provider rejection releases it. Settings updates use SQLite's
writer lock, so concurrent workers share the same company and daily limits.
"""

import json
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


class OutreachPilot:
    def __init__(self, state, config, timezone_name):
        self.state = state
        self.config = config
        self.timezone = ZoneInfo(timezone_name)
        self.key = 'outreach_pilot:' + config.campaign_id

    @staticmethod
    def _decode(raw):
        data = json.loads(raw) if raw else {'started_on': None, 'companies': {}}
        if not isinstance(data, dict) or not isinstance(data.get('companies'), dict):
            raise ValueError('Invalid outreach pilot state; sending held')
        return data

    async def reserve(self, company, outbox_id, now=None):
        """Return an empty reason if reserved, otherwise a reason to hold."""
        if company is None or not company.id:
            return 'unknown_company'
        identity = (company.domain or '').lower().strip().removeprefix('www.')
        identity = 'domain:' + identity if identity else 'company:' + company.id
        requested_now = now
        async with self.state._connect() as db:
            await db.execute('BEGIN IMMEDIATE')
            now = requested_now or datetime.now(timezone.utc)
            today = now.astimezone(self.timezone).date()
            async with db.execute('SELECT value FROM settings WHERE key = ?', (self.key,)) as cur:
                row = await cur.fetchone()
            data = self._decode(row[0] if row else '')
            claims = data['companies']
            if identity in claims:
                return 'already_reserved'
            async with db.execute(
                "SELECT 1 FROM outbox o JOIN prospects p ON p.id = o.prospect_id "
                "WHERE p.company_id = ? AND o.status = 'sent' AND o.kind = 'sequence' LIMIT 1",
                (company.id,),
            ) as cur:
                if await cur.fetchone():
                    return 'already_contacted'
            start = date.fromisoformat(data['started_on']) if data['started_on'] else today
            day = (today - start).days
            if day < 0 or day >= self.config.duration_days:
                return 'expired'
            if sum(c['day'] == today.isoformat() for c in claims.values()) >= self.config.daily_new_companies:
                return 'daily_limit'
            if claims and self.config.min_interval_minutes:
                latest = max(datetime.fromisoformat(c['reserved_at']) for c in claims.values())
                if (now - latest).total_seconds() < self.config.min_interval_minutes * 60:
                    return 'interval'
            data['started_on'] = start.isoformat()
            claims[identity] = {'outbox_id': outbox_id, 'day': today.isoformat(),
                                'reserved_at': now.isoformat(), 'status': 'reserved'}
            await db.execute('INSERT INTO settings (key,value) VALUES (?,?) '
                             'ON CONFLICT(key) DO UPDATE SET value=excluded.value',
                             (self.key, json.dumps(data)))
            await db.commit()
        return ''

    async def finish(self, outbox_id, success):
        async with self.state._connect() as db:
            await db.execute('BEGIN IMMEDIATE')
            async with db.execute('SELECT value FROM settings WHERE key = ?', (self.key,)) as cur:
                row = await cur.fetchone()
            if not row:
                return
            data = self._decode(row[0])
            for identity, claim in list(data['companies'].items()):
                if claim['outbox_id'] == outbox_id:
                    if success:
                        claim['status'] = 'sent'
                    elif claim['status'] == 'reserved':
                        del data['companies'][identity]
                    break
            if not data['companies']:
                data['started_on'] = None
            await db.execute('UPDATE settings SET value = ? WHERE key = ?',
                             (json.dumps(data), self.key))
            await db.commit()
