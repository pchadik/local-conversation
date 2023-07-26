"""Constants for the Local LLM Conversation integration."""

# URI
DOMAIN = "local_conversation"
CONF_PROMPT = "prompt"
DEFAULT_PROMPT = """This smart home is controlled by Home Assistant. Use the following factual information to answer questions from the owner:

The current time is {{ now().strftime('%-I') }}:{% if now().strftime('%M') | int < 10 %}0 {{ now().strftime('%M') | int }}{% else %}{{ now().strftime('%M') }}{% endif %} {{ now().strftime('%p')[0] }}{{ now().strftime('%p')[1] }}.
The current date is {{ now().strftime('%D') }}.
The downstairs temperature is {{states('sensor.downstairs_thermostat_air_temperature') | round}} degrees Fahrenheit.
The garage temperature is {{states('sensor.garage_temperature') | round}} degrees Fahrenheit.
  
There are a total of {{ areas() | length }} areas:

An overview of the areas and the devices in this smart home:
{%- for area in areas() %}
  {%- set area_info = namespace(printed=false) %}
  {%- for device in area_devices(area) -%}
    {%- if not device_attr(device, "disabled_by") and not device_attr(device, "entry_type") and device_attr(device, "name") %}
      {%- if not area_info.printed %}
{{ area_name(area) }} ({{ area_devices(area) | length }} devices)
        {%- set area_info.printed = true %}
      {%- endif %}
    {%- endif %}
  {%- endfor %}
{%- endfor %}

Answer the user's questions about the world truthfully and accurately.

assistant: How can I assist?
"""
CONF_CHAT_MODEL = "chat_model"
DEFAULT_CHAT_MODEL = "whatever"

CONF_MAX_TOKENS = "max_tokens"
DEFAULT_MAX_TOKENS = 150
CONF_TOP_P = "top_p"
DEFAULT_TOP_P = 0.5
CONF_TEMPERATURE = "temperature"
DEFAULT_TEMPERATURE = 0.7
CONF_TOP_K = "top_k"
DEFAULT_TOP_K = 40
CONF_NUM_BEAMS = "num_beams"
DEFAULT_NUM_BEAMS = 1
