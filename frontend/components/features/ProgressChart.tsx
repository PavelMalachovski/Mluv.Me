"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  TooltipProps,
} from "recharts"
import { format } from "date-fns"

interface ProgressChartProps {
  data?: Array<{
    date: string
    correctness_score: number
    messages_count: number
  }>
}

const CustomTooltip = ({
  active,
  payload,
  label,
}: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-background p-3 shadow-md">
        <p className="font-semibold">
          {format(new Date(label), "MMM dd, yyyy")}
        </p>
        <p className="text-sm text-blue-600">
          Score: {payload[0].value}%
        </p>
      </div>
    )
  }
  return null
}

export function ProgressChart({ data = [] }: ProgressChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        No data available yet. Start practicing to see your progress!
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="date"
          tickFormatter={(date) => format(new Date(date), "MMM dd")}
          className="text-xs"
        />
        <YAxis className="text-xs" domain={[0, 100]} />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey="correctness_score"
          stroke="#3b82f6"
          strokeWidth={2}
          name="Correctness Score"
          dot={{ fill: "#3b82f6", r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
