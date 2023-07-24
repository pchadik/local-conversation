from __future__ import annotations

from functools import partial
import logging
from typing import Literal

import requests
import asyncio
import json
import sys

import aiohttp

try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.")
    
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.components import conversation
from homeassistant.components.conversation import agent
from homeassistant.exceptions import ConfigEntryNotReady, TemplateError
from homeassistant.helpers import intent, template
from homeassistant.util import ulid

from .const import (
    CONF_CHAT_MODEL,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_CHAT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
)

DOMAIN = "local_conversation"
HOST = '192.168.86.79:5000'
URI = f'http://{HOST}/api/v1/generate'

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:

    conversation.async_set_agent(hass, entry, MyConversationAgent(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload."""
    conversation.async_unset_agent(hass, entry)
    return True


class MyConversationAgent(agent.AbstractConversationAgent):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the agent."""
        self.hass = hass
        self.entry = entry
        self.history: dict[str, list[dict]] = {}

    @property
    def attribution(self) -> agent.Attribution:
        """Return the attribution."""
        return {
            "name": "My Conversation Agent",
            "url": "https://example.com",
        }

    #@abstractmethod
    async def async_process(self, user_input: agent.ConversationInput) -> agent.ConversationResult:
        """Process a sentence."""
        raw_prompt = self.entry.options.get(CONF_PROMPT, DEFAULT_PROMPT)
        model = self.entry.options.get(CONF_CHAT_MODEL, DEFAULT_CHAT_MODEL)
        max_tokens = self.entry.options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS)
        top_p = self.entry.options.get(CONF_TOP_P, DEFAULT_TOP_P)
        temperature = self.entry.options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE)
        #response = intent.IntentResponse(language=user_input.language)
        #response.async_set_speech("Test response")
        if user_input.conversation_id in self.history:
            conversation_id = user_input.conversation_id
            messages = self.history[conversation_id]
        else:
            conversation_id = ulid.ulid()
            try:
                prompt = self._async_generate_prompt(raw_prompt)
            except TemplateError as err:
                _LOGGER.error("Error rendering prompt: %s", err)
                intent_response = intent.IntentResponse(language=user_input.language)
                intent_response.async_set_error(
                    intent.IntentResponseErrorCode.UNKNOWN,
                    f"Sorry, I had a problem with my template: {err}",
                )
                return conversation.ConversationResult(
                    response=intent_response, conversation_id=conversation_id
                )
            messages = [{"role": "system", "content": prompt}]

        messages.append({"role": "user", "content": user_input.text})

        _LOGGER.debug("Prompt for %s: %s", model, messages)

        
#@dataclass(slots=True)
#class ConversationInput:
#    """User input to be processed."""
#    text: str
#    context: Context
#    conversation_id: str | None
#    device_id: str | None
#    language: str

        request = {
            'prompt': user_input.text,
            'max_new_tokens': 250,
    
            # Generation params. If 'preset' is set to different than 'None', the values
            # in presets/preset-name.yaml are used instead of the individual numbers.
            'preset': 'None',
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.1,
            'typical_p': 1,
            'epsilon_cutoff': 0,  # In units of 1e-4
            'eta_cutoff': 0,  # In units of 1e-4
            'tfs': 1,
            'top_a': 0,
            'repetition_penalty': 1.18,
            'repetition_penalty_range': 0,
            'top_k': 40,
            'min_length': 0,
            'no_repeat_ngram_size': 0,
            'num_beams': 1,
            'penalty_alpha': 0,
            'length_penalty': 1,
            'early_stopping': False,
            'mirostat_mode': 0,
            'mirostat_tau': 5,
            'mirostat_eta': 0.1,
    
            'seed': -1,
            'add_bos_token': True,
            'truncation_length': 2048,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stopping_strings': []
        }

        #response = requests.post(URI, json=request)
        #response = await aiohttp.ClientSession().post(URI, json=request)
        async with aiohttp.ClientSession() as session:
            response = await session.post(URI, data=json.dumps(request))
            if response.status == 200:
                result = response.json()['results'][0]['text']
    
        intent_response = intent.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(result)
        return conversation.ConversationResult(
            response=intent_response, conversation_id=conversation_id
        )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        """Return a list of supported languages."""
        return MATCH_ALL

    def _async_generate_prompt(self, raw_prompt: str) -> str:
        """Generate a prompt for the user."""
        return template.Template(raw_prompt, self.hass).async_render(
            {
                "ha_name": self.hass.config.location_name,
            },
            parse_result=False,
        )