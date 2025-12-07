"use client"

import { format } from "date-fns"
import { Card, CardContent } from "@/components/ui/card"
import { Message } from "@/lib/types"

interface RecentLessonsProps {
  lessons?: Message[]
}

export function RecentLessons({ lessons = [] }: RecentLessonsProps) {
  if (!lessons || lessons.length === 0) {
    return (
      <div className="text-center text-muted-foreground py-8">
        No recent lessons. Start practicing now!
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {lessons.map((lesson) => (
        <Card key={lesson.id} className="hover:shadow-md transition-shadow">
          <CardContent className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    lesson.role === "user"
                      ? "bg-blue-100 text-blue-700"
                      : "bg-green-100 text-green-700"
                  }`}>
                    {lesson.role === "user" ? "You" : "Honzík"}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {format(new Date(lesson.created_at), "MMM dd, HH:mm")}
                  </span>
                </div>
                <p className="text-sm line-clamp-2">{lesson.text}</p>
              </div>
              {lesson.role === "user" && lesson.correctness_score !== undefined && (
                <div className="ml-4 flex-shrink-0">
                  <div className={`text-lg font-bold ${
                    lesson.correctness_score >= 80 ? "text-green-600" :
                    lesson.correctness_score >= 60 ? "text-yellow-600" :
                    "text-red-600"
                  }`}>
                    {lesson.correctness_score}%
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
