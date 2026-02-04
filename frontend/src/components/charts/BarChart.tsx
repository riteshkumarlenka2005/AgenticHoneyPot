'use client'

import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface BarChartProps {
  data: Array<{
    [key: string]: string | number
  }>
  xKey: string
  yKeys: Array<{
    key: string
    label: string
    color?: string
  }>
  height?: number
  stacked?: boolean
}

const DEFAULT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function BarChart({ data, xKey, yKeys, height = 300, stacked = false }: BarChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        No data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xKey} />
        <YAxis />
        <Tooltip />
        <Legend />
        {yKeys.map((yKey, index) => (
          <Bar
            key={yKey.key}
            dataKey={yKey.key}
            name={yKey.label}
            fill={yKey.color || DEFAULT_COLORS[index % DEFAULT_COLORS.length]}
            stackId={stacked ? "stack" : undefined}
          />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  )
}
