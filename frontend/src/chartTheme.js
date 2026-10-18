/**
 * Shared Recharts theme config.
 * Import getChartTheme() in any page to get theme-aware colors.
 *
 * Usage:
 *   const ct = getChartTheme()
 *   <Tooltip contentStyle={ct.tooltip} />
 *   <XAxis tick={{ fill: ct.axisTick, fontSize: 10 }} />
 */

function _getVars() {
  const s = getComputedStyle(document.documentElement)
  return {
    tooltipBg: s.getPropertyValue('--chart-tooltip-bg').trim() || '#141428',
    tooltipBorder: s.getPropertyValue('--chart-tooltip-border').trim() || '#1e1e3a',
    axisTick: s.getPropertyValue('--chart-axis').trim() || '#6a6a8e',
    grid: s.getPropertyValue('--chart-grid').trim() || '#1e1e3a',
    text: s.getPropertyValue('--color-fg').trim() || '#e8e8ff',
  }
}

let _cache = null
let _lastTheme = null

export function getChartTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme')
  if (_cache && _lastTheme === currentTheme) return _cache
  const v = _getVars()
  _cache = {
    tooltip: {
      background: v.tooltipBg,
      border: `1px solid ${v.tooltipBorder}`,
      borderRadius: 8,
      fontSize: 12,
      color: v.text,
    },
    axisTick: { fill: v.axisTick, fontSize: 10 },
    axisTickLg: { fill: v.axisTick, fontSize: 11 },
    grid: { stroke: v.grid, strokeDasharray: '3 3' },
  }
  _lastTheme = currentTheme
  return _cache
}

// Fixed semantic colors (don't change with theme)
export const CHART_COLORS = {
  accent:  '#0a84ff',
  accent2: '#30d158',
  warn:    '#f59e0b',
  danger:  '#ff453a',
  info:    '#5aa9ff',
  purple:  '#bf5af2',
  pink:    '#f472b6',
  gold:    '#FFD700',
  silver:  '#C0C0C0',
  bronze:  '#CD7F32',
}
