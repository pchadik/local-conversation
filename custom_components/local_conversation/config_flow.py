"""Config flow for Local LLM Conversation integration."""
from __future__ import annotations

from functools import partial
import logging
import types
from types import MappingProxyType
from typing import Any

#import openai
#from openai import error
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    TemplateSelector,
)

from .const import (
    CONF_CHAT_MODEL,
    CONF_SERVER_IP,
    CONF_SERVER_PORT,
    CONF_MAX_TOKENS,
    CONF_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_TOP_K,
    CONF_NUM_BEAMS,
    CONF_TRUNC_LENGTH,
    DEFAULT_CHAT_MODEL,
    DEFAULT_SERVER_IP,
    DEFAULT_SERVER_PORT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PROMPT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_TOP_K,
    DEFAULT_NUM_BEAMS,
    DEFAULT_TRUNC_LENGTH,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_PROMPT,
            description="Prompt Template",
            default=DEFAULT_PROMPT,
            ): TemplateSelector(),
        vol.Optional(
            CONF_SERVER_IP,
            description="LLM Server IP Address",
            default=DEFAULT_SERVER_IP,
            ): str,
        vol.Optional(
            CONF_SERVER_PORT,
            description="LLM Server Port",
            default=DEFAULT_SERVER_PORT,
            ): int,
        vol.Optional(
            CONF_MAX_TOKENS,
            description="Maximum tokens to return in response",
            default=DEFAULT_MAX_TOKENS,
            ): int,
        vol.Optional(
            CONF_TOP_P,
            description="Top P",
            default=DEFAULT_TOP_P,
            ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
        vol.Optional(
            CONF_TEMPERATURE,
            description="Temperature",
            default=DEFAULT_TEMPERATURE,
            ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
        vol.Optional(
            CONF_TOP_K,
            description="Top K",
            default=DEFAULT_TOP_K,
            ): NumberSelector(NumberSelectorConfig(min=0, max=200, step=1)),
        vol.Optional(
            CONF_NUM_BEAMS,
            description="Number of beams in search",
            default=DEFAULT_NUM_BEAMS,
            ): NumberSelector(NumberSelectorConfig(min=1, max=5, step=1)),
        vol.Optional(
            CONF_TRUNC_LENGTH,
            description="Truncation length (context)",
            default=DEFAULT_TRUNC_LENGTH,
            ): NumberSelector(NumberSelectorConfig(min=512, max=8192, step=32)),
    }
)

DEFAULT_OPTIONS = types.MappingProxyType(
    {
        CONF_PROMPT: DEFAULT_PROMPT,
        CONF_SERVER_IP: DEFAULT_SERVER_IP,
        CONF_SERVER_PORT: DEFAULT_SERVER_PORT,
        CONF_CHAT_MODEL: DEFAULT_CHAT_MODEL,
        CONF_MAX_TOKENS: DEFAULT_MAX_TOKENS,
        CONF_TOP_P: DEFAULT_TOP_P,
        CONF_TEMPERATURE: DEFAULT_TEMPERATURE,
        CONF_TOP_K: DEFAULT_TOP_K,
        CONF_NUM_BEAMS: DEFAULT_NUM_BEAMS,
        CONF_TRUNC_LENGTH: DEFAULT_TRUNC_LENGTH
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
 #   openai.api_key = data[CONF_API_KEY]
 #   await hass.async_add_executor_job(partial(openai.Engine.list, request_timeout=10))


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Local LLM Conversation."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except error.APIConnectionError:
            errors["base"] = "cannot_connect"
        except error.AuthenticationError:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="Local LLM Conversation", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Local conversation config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="Local LLM Conversation", data=user_input)
        schema = llm_config_option_schema(self.config_entry.options)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(schema),
        )


def llm_config_option_schema(options: MappingProxyType[str, Any]) -> dict:
    """Return a schema for Local LLM completion options."""
    if not options:
        options = DEFAULT_OPTIONS
    return {
        vol.Optional(
            CONF_PROMPT,
            description="Prompt Template",
            default=options.get(CONF_PROMPT, DEFAULT_PROMPT),
        ): TemplateSelector(),
        vol.Optional(
            CONF_SERVER_IP,
            description="LLM Server IP Address",
            default=options.get(CONF_SERVER_IP, DEFAULT_SERVER_IP),
            ): str,
        vol.Optional(
            CONF_SERVER_PORT,
            description="LLM Server Port",
            default=options.get(CONF_SERVER_PORT, DEFAULT_SERVER_PORT),
            ): int,
        vol.Optional(
            CONF_MAX_TOKENS,
            description="Maximum tokens to return in response",
            default=options.get(CONF_MAX_TOKENS, DEFAULT_MAX_TOKENS),
        ): int,
        vol.Optional(
            CONF_TOP_P,
            description="Top P",
            default=options.get(CONF_TOP_P, DEFAULT_TOP_P),
        ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
        vol.Optional(
            CONF_TEMPERATURE,
            description="Temperature",
            default=options.get(CONF_TEMPERATURE, DEFAULT_TEMPERATURE),
        ): NumberSelector(NumberSelectorConfig(min=0, max=1, step=0.05)),
        vol.Optional(
            CONF_TOP_K,
            description="Top K",
            default=options.get(CONF_TOP_K, DEFAULT_TOP_K),
        ): NumberSelector(NumberSelectorConfig(min=0, max=200, step=1)),
        vol.Optional(
            CONF_NUM_BEAMS,
            description="Number of beams in search",
            default=options.get(CONF_NUM_BEAMS, DEFAULT_NUM_BEAMS),
        ): NumberSelector(NumberSelectorConfig(min=1, max=5, step=1)),
        vol.Optional(
            CONF_TRUNC_LENGTH,
            description="Truncation length (context)",
            default=DEFAULT_TRUNC_LENGTH,
            ): NumberSelector(NumberSelectorConfig(min=512, max=8192, step=32)),
    }
