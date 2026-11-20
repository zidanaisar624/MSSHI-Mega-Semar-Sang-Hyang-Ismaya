/**
 * MSSHITrim — Desktop Settings & Multi-Bot Control Surface for Hermes Desktop.
 *
 * Registers the "MSSHITrim" entry in Settings ▸ Plugins (and pairs with the
 * backend `msshi-auto-trim` agent plugin across all bot profiles: Hermes,
 * Yukino Yukinoshita, Sensei Shizuka Hiratsuka, Val, Kiki-Chii, and Sir. Robot).
 *
 * Pure ESM using only @hermes/plugin-sdk, react, and react/jsx-runtime.
 * No external network calls, no LLM/MCP calls, no raw DOM/bridge access.
 */

import {
  Badge,
  Button,
  Codicon,
  host,
  Input,
  ListRow,
  ToggleRow,
  useValue
} from '@hermes/plugin-sdk'
import { useCallback, useEffect, useState } from 'react'
import { jsx, jsxs } from 'react/jsx-runtime'

const PLUGIN_KEY = 'msshi-auto-trim'
const DISPLAY_NAME = 'MSSHITrim'

const BOT_PROFILES = [
  { id: 'default', label: 'Hermes' },
  { id: 'kiki-chii', label: 'Kiki-Chii' },
  { id: 'shikaku', label: 'Sir. Robot' },
  { id: 'shizuka', label: 'Sensei Shizuka Hiratsuka' },
  { id: 'val', label: 'Val' },
  { id: 'yukino', label: 'Yukino Yukinoshita' }
]

const DEFAULT_VALUES = {
  enabled: true,
  binary: '',
  min_chars: 2048,
  max_chars: 262144,
  timeout_seconds: 3.0
}

function extractValuesFromRow(row) {
  if (!row || !Array.isArray(row.settings_schema)) {
    return null
  }
  const out = { ...DEFAULT_VALUES }
  for (const field of row.settings_schema) {
    if (field && typeof field.key === 'string' && field.value !== undefined) {
      out[field.key] = field.value
    }
  }
  if (row.status === 'disabled' || row.status === 'not enabled') {
    out.enabled = false
  }
  return out
}

function MsshiTrimSettingsPage() {
  const activeProfile = useValue(host.state.profile) || 'default'
  const gatewayState = useValue(host.state.gateway) || 'idle'

  const [selectedProfile, setSelectedProfile] = useState(activeProfile)
  const [values, setValues] = useState(DEFAULT_VALUES)
  const [fleetStatus, setFleetStatus] = useState(() =>
    Object.fromEntries(BOT_PROFILES.map(bot => [bot.id, 'enabled']))
  )
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const loadProfileSettings = useCallback(async (profileId) => {
    if (gatewayState !== 'open') {
      return
    }
    setLoading(true)
    try {
      const scopeParam = profileId && profileId !== 'default' ? { profile: profileId } : {}
      const res = await host.request('plugins.manage', {
        action: 'list',
        ...scopeParam
      })
      const rows = Array.isArray(res?.plugins) ? res.plugins : []
      const match = rows.find(
        r => r && (r.key === PLUGIN_KEY || r.name === PLUGIN_KEY || r.name === DISPLAY_NAME)
      )
      const parsed = extractValuesFromRow(match)
      if (parsed) {
        setValues(parsed)
        setFleetStatus(prev => ({
          ...prev,
          [profileId || 'default']: match.status === 'enabled' && parsed.enabled !== false ? 'enabled' : 'disabled'
        }))
      }
    } catch {
      // Keep local defaults visible when gateway is busy or reconnecting.
    } finally {
      setLoading(false)
    }
  }, [gatewayState])

  useEffect(() => {
    void loadProfileSettings(selectedProfile)
  }, [selectedProfile, loadProfileSettings])

  const saveToProfiles = async (targetProfiles) => {
    if (gatewayState !== 'open') {
      host.notifyError('Hermes gateway is still connecting. Please try again in a moment.', DISPLAY_NAME)
      return
    }
    setSaving(true)
    const cleanPayload = {
      enabled: Boolean(values.enabled),
      binary: String(values.binary ?? '').trim(),
      min_chars: Math.max(256, Number(values.min_chars) || 2048),
      max_chars: Math.min(1048576, Math.max(2048, Number(values.max_chars) || 262144)),
      timeout_seconds: Math.min(10.0, Math.max(0.2, Number(values.timeout_seconds) || 3.0))
    }
    try {
      for (const prof of targetProfiles) {
        const scopeParam = prof && prof !== 'default' ? { profile: prof } : {}
        await host.request('plugins.manage', {
          action: 'toggle',
          key: PLUGIN_KEY,
          enable: cleanPayload.enabled,
          ...scopeParam
        })
        await host.request('plugins.manage', {
          action: 'settings',
          key: PLUGIN_KEY,
          values: cleanPayload,
          ...scopeParam
        })
      }
      setValues(cleanPayload)
      setFleetStatus(prev => {
        const next = { ...prev }
        for (const prof of targetProfiles) {
          next[prof] = cleanPayload.enabled ? 'enabled' : 'disabled'
        }
        return next
      })
      const targetLabel =
        targetProfiles.length > 1
          ? `all ${targetProfiles.length} bot profiles`
          : (BOT_PROFILES.find(b => b.id === targetProfiles[0])?.label || targetProfiles[0])
      host.notify({
        kind: 'success',
        message: `${DISPLAY_NAME} settings saved for ${targetLabel}.`
      })
    } catch (err) {
      host.notifyError(err, `Could not save ${DISPLAY_NAME} settings`)
    } finally {
      setSaving(false)
    }
  }

  const currentBotLabel =
    BOT_PROFILES.find(b => b.id === selectedProfile)?.label || selectedProfile

  return jsxs('div', {
    className: 'flex flex-col gap-5',
    children: [
      jsxs('div', {
        className: 'flex flex-col gap-2',
        children: [
          jsx('span', {
            className: 'text-xs font-medium text-(--ui-text-secondary)',
            children: 'Applies to'
          }),
          jsx('div', {
            className: 'flex flex-wrap items-center gap-1.5',
            children: BOT_PROFILES.map(bot => {
              const active = selectedProfile === bot.id
              const isEnabled = fleetStatus[bot.id] !== 'disabled'
              return jsxs(
                'button',
                {
                  type: 'button',
                  onClick: () => setSelectedProfile(bot.id),
                  className: active
                    ? 'inline-flex items-center gap-1.5 rounded-full border border-(--ui-accent) bg-(--ui-bg-tertiary) px-3 py-1 text-xs font-medium text-foreground'
                    : 'inline-flex items-center gap-1.5 rounded-full border border-(--ui-stroke-tertiary) px-3 py-1 text-xs text-(--ui-text-secondary) hover:bg-(--chrome-action-hover)',
                  children: [
                    jsx('span', {
                      className: isEnabled
                        ? 'size-1.5 rounded-full bg-emerald-400'
                        : 'size-1.5 rounded-full bg-zinc-500'
                    }),
                    jsx('span', { children: bot.label })
                  ]
                },
                bot.id
              )
            })
          }),
          jsx('p', {
            className: 'text-xs text-(--ui-accent)',
            children: `Changes on this page apply to the "${currentBotLabel}" profile (or click "Apply to All Bots" to sync all 6 bots).`
          })
        ]
      }),

      jsxs('div', {
        className: 'flex flex-wrap items-center justify-between gap-3 rounded-lg border border-(--ui-stroke-tertiary) bg-(--ui-bg-secondary) p-3.5',
        children: [
          jsxs('div', {
            className: 'flex flex-col gap-1',
            children: [
              jsxs('div', {
                className: 'flex flex-wrap items-center gap-2',
                children: [
                  jsx(Codicon, { name: 'flame', size: '0.95rem' }),
                  jsx('span', {
                    className: 'text-sm font-semibold text-foreground',
                    children: 'MSSHITrim (Local JSON Auto-Trim v0.2.0)'
                  }),
                  jsx(Badge, {
                    children: values.enabled ? 'Active · All 6 Bots' : 'Paused'
                  })
                ]
              }),
              jsx('p', {
                className: 'text-xs text-(--ui-text-tertiary)',
                children:
                  'Automatically compacts eligible large JSON tool results via local llmtrim (v0.13.8) with exact canonical JSON equality. Zero LLM calls, zero MCP overhead, and 100% model-agnostic.'
              })
            ]
          }),
          jsxs('div', {
            className: 'flex items-center gap-2',
            children: [
              jsx(Button, {
                size: 'sm',
                variant: 'outline',
                disabled: saving || loading,
                onClick: () => void saveToProfiles([selectedProfile]),
                children: saving ? 'Saving…' : `Save (${currentBotLabel})`
              }),
              jsx(Button, {
                size: 'sm',
                disabled: saving || loading,
                onClick: () => void saveToProfiles(BOT_PROFILES.map(b => b.id)),
                children: saving ? 'Applying…' : 'Apply to All Bots'
              })
            ]
          })
        ]
      }),

      jsxs('div', {
        className: 'flex flex-col divide-y divide-(--ui-stroke-tertiary) rounded-lg border border-(--ui-stroke-tertiary)',
        children: [
          jsx(ToggleRow, {
            title: 'Enable MSSHITrim',
            description: 'Automatically process eligible large JSON tool results through the transform_tool_result hook.',
            checked: Boolean(values.enabled),
            disabled: saving,
            onCheckedChange: checked => setValues(prev => ({ ...prev, enabled: Boolean(checked) }))
          }),
          jsx(ListRow, {
            title: 'Local llmtrim Binary',
            description: 'Absolute path to local llmtrim executable (leave blank or default to use the verified local binary).',
            action: jsx(Input, {
              className: 'w-72 font-mono text-xs',
              placeholder: 'Auto-detected (tools/llmtrim/llmtrim.exe)',
              value: String(values.binary ?? ''),
              disabled: saving,
              onChange: e => setValues(prev => ({ ...prev, binary: e.target.value }))
            })
          }),
          jsx(ListRow, {
            title: 'Minimum Characters (min_chars)',
            description: 'Skip short tool results below this character count to avoid subprocess overhead (default: 2048).',
            action: jsx(Input, {
              className: 'w-32 font-mono text-xs',
              type: 'number',
              min: 256,
              max: 1048576,
              value: String(values.min_chars ?? 2048),
              disabled: saving,
              onChange: e => setValues(prev => ({ ...prev, min_chars: Number(e.target.value) || 2048 }))
            })
          }),
          jsx(ListRow, {
            title: 'Maximum Characters (max_chars)',
            description: 'Upper bound on the size processed by each local compressor call (default: 262144).',
            action: jsx(Input, {
              className: 'w-32 font-mono text-xs',
              type: 'number',
              min: 2048,
              max: 1048576,
              value: String(values.max_chars ?? 262144),
              disabled: saving,
              onChange: e => setValues(prev => ({ ...prev, max_chars: Number(e.target.value) || 262144 }))
            })
          }),
          jsx(ListRow, {
            title: 'Timeout Seconds (timeout_seconds)',
            description: 'Fail open to the original uncompressed result if local compression exceeds this time (default: 3.0s).',
            action: jsx(Input, {
              className: 'w-32 font-mono text-xs',
              type: 'number',
              step: '0.5',
              min: 0.2,
              max: 10.0,
              value: String(values.timeout_seconds ?? 3.0),
              disabled: saving,
              onChange: e => setValues(prev => ({ ...prev, timeout_seconds: Number(e.target.value) || 3.0 }))
            })
          })
        ]
      })
    ]
  })
}

export default {
  id: PLUGIN_KEY,
  name: DISPLAY_NAME,
  description:
    'MSSHITrim — Automatically compact eligible large JSON tool results through local Llmtrim with exact canonical JSON equality. No MCP or LLM calls.',
  defaultEnabled: true,
  register(ctx) {
    ctx.registerSettingsPage?.({
      id: 'overview',
      title: DISPLAY_NAME,
      icon: 'flame',
      order: 10,
      render: MsshiTrimSettingsPage
    })
  }
}
