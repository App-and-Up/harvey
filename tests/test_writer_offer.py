"""The configured first email approach reaches both writing paths."""

from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from harvey.agents.writer import Writer
from harvey.brain import Brain
from harvey.config import HarveyConfig, OfferConfig
from harvey.models.prospect import Prospect


@pytest.mark.parametrize('mode', ['discovery', 'product_intro'])
@pytest.mark.parametrize('personal', [True, False])
@pytest.mark.asyncio
async def test_first_email_approach_in_rendered_prompt(mode, personal):
    config = HarveyConfig(
        persona=dict(name='Daniele', company='Halvea', role='Fondatore',
                     email='sender@example.com', linkedin='', tone='Italiano'),
        product=dict(name='Halvea', description='App ordini B2B', pricing='150 EUR',
                     key_benefits=['Ordini clienti e agenti'], objection_responses={},
                     offer=dict(first_email_mode=mode, entry='Ordini per i clienti assegnati')),
        icp=dict(industries=['Distribuzione B2B'], company_size='PMI',
                 titles=['Titolare'], geography=['Italia']),
    )
    brain = Brain(state=None, brain_config=config.brain)
    if personal:
        result = {'subject': 'ordini degli agenti', 'body': 'Come raccogliete gli ordini?'}
    else:
        result = [{'step': 1, 'subject': 'ordini degli agenti',
                   'body': 'Come raccogliete gli ordini?', 'delay_days': 0}]
    brain.think_json = AsyncMock(return_value=result)
    writer = Writer(brain, state=None, config=config)
    # Include a conflicting generic framework to check explicit prompt precedence.
    writer.skills = 'Generic framework: Email 1 has no offer.'
    prospect = Prospect(first_name='Test', last_name='Persona', title='Titolare',
                        company='Azienda di esempio')
    if personal:
        assert await writer._write_personal_email(prospect)
    else:
        assert await writer._write_sequence([prospect])
    prompt = brain.think_json.call_args.args[0]
    assert '{{first_email_instructions}}' not in prompt
    assert 'take precedence over generic outreach frameworks' in prompt
    assert 'No links in email 1' in prompt
    assert 'NEVER fabricate details' in prompt
    if mode == 'product_intro':
        assert 'Ordini per i clienti assegnati' in prompt
        assert 'You may name the product' in prompt
        assert 'No pitch, no product name' not in prompt
        assert 'Email 1 does NOT pitch' not in prompt
    else:
        assert 'No pitch, no product name' in prompt
        assert 'You may name the product' not in prompt


def test_first_email_mode_defaults_and_validation():
    assert OfferConfig().first_email_mode == 'discovery'
    with pytest.raises(ValidationError):
        OfferConfig(first_email_mode='unknown')
