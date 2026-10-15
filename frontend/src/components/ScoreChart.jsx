import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { getChartTheme } from '../chartTheme'

export default function ScoreChart({ data }) {
  const ct = getChartTheme()
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <XAxis dataKey="name" stroke={ct.axis} tick={{ fill: ct.text, fontSize: 12 }} />
        <YAxis domain={[0, 100]} stroke={ct.axis} tick={{ fill: ct.text, fontSize: 12 }} />
        <Tooltip
          contentStyle={{ background: ct.tooltipBg, border: `1px solid ${ct.tooltipBorder}`, borderRadius: 8 }}
          formatter={(val) => [`${Number(val).toFixed(1)}%`, 'Score']}
        />
        <Bar dataKey="score" radius={[6, 6, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={index === 0 ? 'var(--color-primary)' : index === 1 ? 'var(--color-info)' : 'var(--color-purple)'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
