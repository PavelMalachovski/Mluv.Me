"use client"

import { useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { LessonResponse } from "@/lib/types"

interface ConversationMessage {
  role: "user" | "assistant"
  text: string
  response?: LessonResponse
}

export default function PracticePage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const [userText, setUserText] = useState("")
  const [conversation, setConversation] = useState<ConversationMessage[]>([])

  const sendMessage = useMutation({
    mutationFn: (text: string) =>
      apiClient.post<LessonResponse>("/api/v1/web/lessons/text", {
        text,
        user_id: user?.id,
      }),
    onSuccess: (data, text) => {
      // Add user message
      setConversation((prev) => [
        ...prev,
        {
          role: "user",
          text: text,
          response: data,
        },
      ])

      // Add Honzík response
      setConversation((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.honzik_text,
        },
      ])

      setUserText("")
    },
  })

  if (!user) {
    router.push("/login")
    return null
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (userText.trim()) {
      sendMessage.mutate(userText)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto max-w-4xl p-6">
        <div className="mb-6">
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            ← Back to Dashboard
          </Button>
        </div>

        <div className="rounded-lg border bg-white p-6 shadow-sm">
          <h1 className="mb-2 text-3xl font-bold">Practice Czech with Honzík</h1>
          <p className="mb-6 text-muted-foreground">
            Type in Czech and get instant feedback from your AI teacher
          </p>

          {/* Conversation History */}
          <div className="mb-6 space-y-4 max-h-[500px] overflow-y-auto">
            {conversation.length === 0 ? (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-6">
                  <p className="text-center text-blue-900">
                    👋 Nazdar! Jsem Honzík. Let&apos;s start practicing Czech! Write
                    something in Czech and I&apos;ll help you improve.
                  </p>
                </CardContent>
              </Card>
            ) : (
              conversation.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[80%] ${
                      msg.role === "user"
                        ? "rounded-lg bg-blue-500 p-4 text-white"
                        : "rounded-lg bg-gray-100 p-4"
                    }`}
                  >
                    <p className="whitespace-pre-wrap">{msg.text}</p>

                    {msg.role === "user" && msg.response && (
                      <div className="mt-3 space-y-2 border-t border-blue-400 pt-3">
                        <div className="flex items-center gap-2 text-sm">
                          <span>⭐ {msg.response.stars_earned} stars</span>
                          <span>•</span>
                          <span>{msg.response.correctness_score}% correct</span>
                        </div>

                        {msg.response.user_mistakes.length > 0 && (
                          <div className="rounded-md bg-blue-600 p-2 text-xs">
                            <p className="font-semibold mb-1">Corrections:</p>
                            <ul className="list-disc pl-4 space-y-1">
                              {msg.response.user_mistakes.map((mistake, i) => (
                                <li key={i}>{mistake}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}

            {sendMessage.isPending && (
              <div className="flex justify-start">
                <div className="rounded-lg bg-gray-100 p-4">
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-100" />
                    <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400 delay-200" />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <form onSubmit={handleSubmit} className="space-y-3">
            <Textarea
              value={userText}
              onChange={(e) => setUserText(e.target.value)}
              placeholder="Napište svou zprávu v češtině... (Type your message in Czech...)"
              rows={4}
              className="resize-none"
              disabled={sendMessage.isPending}
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                Tip: Don&apos;t worry about mistakes - that&apos;s how you learn! 💪
              </p>
              <Button
                type="submit"
                disabled={!userText.trim() || sendMessage.isPending}
                size="lg"
              >
                {sendMessage.isPending ? "Sending..." : "Send Message"}
              </Button>
            </div>
          </form>
        </div>

        {/* Tips Section */}
        <div className="mt-6 rounded-lg border bg-white p-6 shadow-sm">
          <h3 className="mb-3 font-semibold">Practice Tips:</h3>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>✅ Try to write complete sentences</li>
            <li>✅ Don&apos;t be afraid to make mistakes</li>
            <li>✅ Ask Honzík questions about Czech culture</li>
            <li>✅ Practice regularly to maintain your streak</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
