"""Retired compatibility stub: no Steel provider, hooks, tools or prompt routing.

An older configuration may still list this plugin. Loading this stub is inert;
it never opens a browser or account and does not intercept the user's browser.
"""
import json


def register(ctx):
    return None


def result(**value):
    return json.dumps(value, ensure_ascii=False)


def steel_exec(args=None, **kwargs):
    return result(status='legacy_steel_retired', changed=False, connected=False,
                  network_requests=0, message='Choose and connect a browser manually in Hermes.')


def personal_exec(args=None, **kwargs):
    return steel_exec(args, **kwargs)


def pre_tool_call(tool_name, args=None, **kwargs):
    return None
