"use client"

import { useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { UserStats, Message } from "@/lib/types"
import { Mic, Send, Play, Pause } from "lucide-react"
import { useState, useRef } from "react"

export default function DashboardPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [isPlaying, setIsPlaying] = useState<number | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)

  const { data: stats } = useQuery<UserStats>({
    queryKey: ["user-stats"],
    queryFn: () => apiClient.get("/api/v1/stats/me"),
    enabled: !!user,
  })

  const { data: lessonsData } = useQuery<{ messages: Message[] }>({
    queryKey: ["recent-lessons"],
    queryFn: () =>
      apiClient.get("/api/v1/web/lessons/history", {
        params: { user_id: user?.id, limit: 10 },
      }),
    enabled: !!user,
  })

  if (!user) {
    router.push("/login")
    return null
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder

      const chunks: Blob[] = []
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data)
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/ogg" })
        setAudioBlob(blob)
      }

      mediaRecorder.start()
      setIsRecording(true)
    } catch (err) {
      console.error("Error accessing microphone:", err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach((track) => track.stop())
      setIsRecording(false)
    }
  }

  return (
    <div className="mx-auto h-screen max-w-3xl">
      {/* Header */}
      <div className="border-b bg-white px-4 py-3 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-600 text-white font-bold text-lg">
              🇨🇿
            </div>
            <div>
              <h1 className="text-lg font-semibold">Honzík - Czech Tutor</h1>
              <p className="text-xs text-gray-500">53,405 monthly users</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">🔥 {stats?.streak || 0}</span>
            <span className="text-sm text-gray-600">⭐ {stats?.total_stars || 0}</span>
          </div>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex h-[calc(100vh-160px)] flex-col gap-4 overflow-y-auto bg-gray-50 p-4">
        {/* Bot Info Card */}
        <div className="rounded-lg bg-blue-50 p-4 text-center">
          <div className="mb-2 text-2xl">👋</div>
          <p className="text-sm font-medium text-blue-900">
            Nazdar, {user.first_name}! I'm Honzík, your personal Czech tutor.
          </p>
          <p className="mt-2 text-xs text-blue-700">
            🗣️ Send me voice messages to practice your spoken Czech
          </p>
          <p className="text-xs text-blue-700">
            🎙️ I will check your grammar and pronunciation mistakes
          </p>
          <p className="text-xs text-blue-700">
            😊 We can chat about beer, knedlíky, hockey, or anything you want!
          </p>
        </div>

        {/* Messages */}
        {lessonsData?.messages?.map((message, idx) => (
          <div
            key={idx}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-white text-gray-900 shadow-sm"
              }`}
            >
              {message.audio_file_path && (
                <div className="mb-2 flex items-center gap-2">
                  <button
                    onClick={() =>
                      setIsPlaying(isPlaying === idx ? null : idx)
                    }
                    className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white hover:bg-blue-700"
                  >
                    {isPlaying === idx ? (
                      <Pause className="h-4 w-4" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </button>
                  <div className="h-1 flex-1 rounded-full bg-gray-300">
                    <div className="h-1 w-1/3 rounded-full bg-blue-600"></div>
                  </div>
                  <span className="text-xs">0:13</span>
                </div>
              )}
              <p className="text-sm">{message.text || message.transcript_raw}</p>
              {message.correctness_score !== undefined && (
                <div className="mt-2 flex items-center gap-2 text-xs">
                  <span className="rounded-full bg-green-100 px-2 py-0.5 font-medium text-green-700">
                    ✅ {message.correctness_score}%
                  </span>
                  <span className="text-gray-500">
                    {new Date(message.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {lessonsData?.messages?.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="mb-4 text-6xl">🎤</div>
            <h3 className="mb-2 text-lg font-semibold text-gray-900">
              Start Your First Conversation
            </h3>
            <p className="text-sm text-gray-500">
              Press and hold the microphone button to record your message
            </p>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t bg-white p-4">
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            size="icon"
            className="h-10 w-10 rounded-full"
          >
            <Send className="h-5 w-5 text-gray-600" />
          </Button>

          <div className="flex-1 rounded-full bg-gray-100 px-4 py-2">
            <input
              type="text"
              placeholder="Type a message or use voice..."
              className="w-full bg-transparent text-sm outline-none"
            />
          </div>

          <Button
            size="icon"
            className={`h-12 w-12 rounded-full ${
              isRecording
                ? "bg-red-500 hover:bg-red-600"
                : "bg-blue-500 hover:bg-blue-600"
            }`}
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
          >
            <Mic className={`h-6 w-6 ${isRecording ? "animate-pulse" : ""}`} />
          </Button>
        </div>

        <div className="mt-2 flex justify-center gap-4 text-xs text-gray-500">
          <button className="hover:text-blue-600">Menu</button>
          <button className="hover:text-blue-600">Help</button>
          <button className="hover:text-blue-600">Commands</button>
        </div>
      </div>
    </div>
  )
}
