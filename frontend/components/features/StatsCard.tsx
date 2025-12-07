"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LucideIcon, Flame, Star, Award, MessageCircle } from "lucide-react"

interface StatsCardProps {
  title: string
  value: string | number
  icon: "flame" | "star" | "award" | "message-circle"
  trend?: string
}

const iconMap: Record<string, LucideIcon> = {
  flame: Flame,
  star: Star,
  award: Award,
  "message-circle": MessageCircle,
}

export function StatsCard({ title, value, icon, trend }: StatsCardProps) {
  const Icon = iconMap[icon]

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {trend && (
          <p className="text-xs text-muted-foreground">{trend}</p>
        )}
      </CardContent>
    </Card>
  )
}
