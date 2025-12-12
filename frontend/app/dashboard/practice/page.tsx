"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { useMutation } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { ClickableText } from "@/components/ui/ClickableText"
import { TranslationPopup } from "@/components/ui/TranslationPopup"
import { TopicSelector, TOPICS } from "@/components/features/TopicSelector"
import { LessonResponse, WordTranslation } from "@/lib/types"
import { FileText, Languages, Mic, Keyboard, X, Loader2 } from "lucide-react"

// Dynamic import to avoid SSR issues with react-media-recorder (uses Web Workers)
const VoiceRecorder = dynamic(
  () => import("@/components/ui/VoiceRecorder").then((mod) => mod.VoiceRecorder),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
      </div>
    ),
  }
)

interface ConversationMessage {
  role: "user" | "assistant"
  text: string
  response?: LessonResponse
  showTranscript?: boolean
  translateMode?: boolean
}

interface TranslationState {
  word: string
  translation: string | null
  phonetics: string | null
  isLoading: boolean
  position: { top: number; left: number }
  messageIndex: number
}

export default function PracticePage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const [userText, setUserText] = useState("")
  const [conversation, setConversation] = useState<ConversationMessage[]>([])
  const [translationState, setTranslationState] = useState<TranslationState | null>(null)
  const [inputMode, setInputMode] = useState<"text" | "voice">("text")
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null)
  const [showTopicSelector, setShowTopicSelector] = useState(true)

  const sendMessage = useMutation({
    mutationFn: (text: string) =>
      apiClient.post<LessonResponse>("/api/v1/web/lessons/text", {
        text,
        user_id: user?.id,
      }),
    onSuccess: (data, text) => {
      console.log("Response from backend:", data)

      // Add user message
      setConversation((prev) => [
        ...prev,
        {
          role: "user",
          text: text,
          response: data,
        },
      ])

      // Add Honzík response with transcript
      setConversation((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.honzik_text,
          response: data,
          showTranscript: false,
          translateMode: false,
        },
      ])

      setUserText("")
    },
  })

  const translateWord = useMutation({
    mutationFn: (word: string) =>
      apiClient.translateWord(word, user?.ui_language || "ru"),
    onSuccess: (data: WordTranslation) => {
      setTranslationState((prev) =>
        prev ? {
          ...prev,
          translation: data.translation,
          phonetics: data.phonetics || null,
          isLoading: false
        } : null
      )
    },
    onError: () => {
      setTranslationState((prev) =>
        prev ? { ...prev, translation: null, isLoading: false } : null
      )
    },
  })

  const saveWord = useMutation({
    mutationFn: (wordData: { word_czech: string; translation: string }) =>
      apiClient.saveWord(user!.id, wordData),
    onSuccess: () => {
      // Close popup after saving
      setTranslationState(null)
    },
  })

  // Voice processing mutation
  const processVoice = useMutation({
    mutationFn: (audioBlob: Blob) => apiClient.processVoice(user!.telegram_id, audioBlob),
    onSuccess: (data) => {
      console.log("Voice response from backend:", data)

      // Get user transcript if available
      const userTranscript = data.user_transcript || data.transcript || "🎤 Voice message"

      // Create lesson response from voice response
      const lessonResponse: LessonResponse = {
        honzik_text: data.honzik_response_text || data.honzik_response_transcript || "",
        honzik_transcript: data.honzik_response_transcript || data.honzik_response_text || "",
        user_mistakes: data.corrections?.mistakes?.map((m: { original: string }) => m.original) || [],
        suggestions: data.corrections?.suggestion ? [data.corrections.suggestion] : [],
        stars_earned: data.stars_earned || 0,
        correctness_score: data.corrections?.correctness_score || 0,
      }

      // Add user message
      setConversation((prev) => [
        ...prev,
        {
          role: "user",
          text: userTranscript,
          response: lessonResponse,
        },
      ])

      // Add Honzík response
      setConversation((prev) => [
        ...prev,
        {
          role: "assistant",
          text: lessonResponse.honzik_text,
          response: lessonResponse,
          showTranscript: false,
          translateMode: false,
        },
      ])
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

  const toggleTranscript = (index: number) => {
    setConversation((prev) =>
      prev.map((msg, i) =>
        i === index ? { ...msg, showTranscript: !msg.showTranscript } : msg
      )
    )
  }

  const toggleTranslateMode = (index: number) => {
    setConversation((prev) =>
      prev.map((msg, i) =>
        i === index ? { ...msg, translateMode: !msg.translateMode } : msg
      )
    )
    // Close any open translation popup
    setTranslationState(null)
  }

  const handleWordClick = (word: string, rect: DOMRect, messageIndex: number) => {
    const scrollY = typeof window !== 'undefined' ? window.scrollY : 0
    setTranslationState({
      word,
      translation: null,
      phonetics: null,
      isLoading: true,
      position: { top: rect.bottom + scrollY, left: rect.left + rect.width / 2 },
      messageIndex,
    })
    translateWord.mutate(word)
  }

  const handleSaveWord = () => {
    if (translationState?.translation) {
      saveWord.mutate({
        word_czech: translationState.word,
        translation: translationState.translation,
      })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="container mx-auto max-w-4xl p-6">
        <div className="mb-6">
          <Button variant="outline" onClick={() => router.push("/dashboard")}>
            ← Back to Dashboard
          </Button>
        </div>

        <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-sm">
          <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-gray-100">Practice Czech with Honzík</h1>
          <p className="mb-6 text-gray-600 dark:text-gray-400">
            Type in Czech and get instant feedback from your AI teacher
          </p>

          {/* Topic Selector */}
          {showTopicSelector && conversation.length === 0 && (
            <div className="mb-6">
              <TopicSelector
                selectedTopic={selectedTopic}
                onSelectTopic={setSelectedTopic}
              />
              <div className="mt-4 text-center">
                <Button
                  onClick={() => setShowTopicSelector(false)}
                  className="px-8"
                >
                  Start Practice
                </Button>
              </div>
            </div>
          )}

          {/* Topic Banner */}
          {selectedTopic && !showTopicSelector && (
            <div className="mb-4 flex items-center justify-between p-3 rounded-lg bg-primary/10 border border-primary/20">
              <div className="flex items-center gap-2">
                <span className="text-sm">
                  <span className="font-medium">Topic:</span>{" "}
                  {TOPICS.find(t => t.id === selectedTopic)?.nameCzech}
                </span>
              </div>
              <button
                onClick={() => {
                  setSelectedTopic(null)
                  setShowTopicSelector(true)
                  setConversation([])
                }}
                className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Conversation History */}
          {!showTopicSelector && (
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
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"
                      }`}
                  >
                    <div
                      className={`max-w-[80%] ${msg.role === "user"
                        ? "rounded-lg bg-blue-500 p-4 text-white"
                        : "rounded-lg bg-gray-100 dark:bg-gray-800 p-4"
                        }`}
                    >
                      {/* Message text - use ClickableText in translate mode */}
                      {msg.role === "assistant" && msg.translateMode ? (
                        <ClickableText
                          text={msg.text}
                          onWordClick={(word, rect) => handleWordClick(word, rect, index)}
                          className="text-gray-800 dark:text-gray-200"
                        />
                      ) : (
                        <p className="whitespace-pre-wrap">{msg.text}</p>
                      )}

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

                      {msg.role === "assistant" && msg.response && (
                        <div className="mt-3 space-y-2 border-t border-gray-300 dark:border-gray-600 pt-3">
                          <div className="flex flex-wrap gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => toggleTranscript(index)}
                              className="flex items-center gap-2 text-xs bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200"
                            >
                              <FileText className="h-4 w-4" />
                              {msg.showTranscript ? "Скрыть текст" : "Показать текст"}
                            </Button>

                            {/* Translate by word button */}
                            <Button
                              variant={msg.translateMode ? "default" : "outline"}
                              size="sm"
                              onClick={() => toggleTranslateMode(index)}
                              className={`flex items-center gap-2 text-xs ${msg.translateMode
                                ? "bg-yellow-500 hover:bg-yellow-600 text-black border-yellow-500"
                                : "bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200"
                                }`}
                            >
                              <Languages className="h-4 w-4" />
                              {msg.translateMode ? "Выключить перевод" : "Translate by word"}
                            </Button>
                          </div>

                          {msg.showTranscript && msg.response.honzik_transcript && (
                            <div className="rounded-md bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 p-3 text-sm text-gray-800 dark:text-gray-200">
                              <p className="font-semibold mb-2 text-xs text-gray-600 dark:text-gray-400">📝 Текст ответа:</p>
                              <p className="whitespace-pre-wrap leading-relaxed">{msg.response.honzik_transcript}</p>
                            </div>
                          )}

                          {msg.translateMode && (
                            <div className="rounded-md bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-2 text-xs text-yellow-800 dark:text-yellow-200">
                              💡 Нажмите на любое слово, чтобы увидеть перевод
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
          )}

          {/* Input Mode Toggle - only show when not selecting topic */}
          {!showTopicSelector && (
            <>
              <div className="flex items-center justify-center gap-2 mb-4">
                <Button
                  type="button"
                  variant={inputMode === "text" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setInputMode("text")}
                  className="flex items-center gap-2"
                >
                  <Keyboard className="h-4 w-4" />
                  Text
                </Button>
                <Button
                  type="button"
                  variant={inputMode === "voice" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setInputMode("voice")}
                  className="flex items-center gap-2"
                >
                  <Mic className="h-4 w-4" />
                  Voice
                </Button>
              </div>

              {/* Input Area */}
              {inputMode === "text" ? (
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
              ) : (
                <div className="space-y-3">
                  <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-4">
                    <VoiceRecorder
                      onRecordComplete={(blob) => processVoice.mutate(blob)}
                      isProcessing={processVoice.isPending}
                      maxDurationSeconds={60}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground text-center">
                    🎤 Tap to record your Czech message (max 60 seconds)
                  </p>
                </div>
              )}
            </>
          )}
        </div>

        {/* Tips Section */}
        <div className="mt-6 rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-sm">
          <h3 className="mb-3 font-semibold text-gray-900 dark:text-gray-100">Practice Tips:</h3>
          <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <li>✅ Try to write complete sentences</li>
            <li>✅ Don&apos;t be afraid to make mistakes</li>
            <li>✅ Ask Honzík questions about Czech culture</li>
            <li>✅ Practice regularly to maintain your streak</li>
            <li>✅ Use &quot;Translate by word&quot; to learn new vocabulary</li>
          </ul>
        </div>
      </div>

      {/* Translation Popup */}
      {translationState && (
        <TranslationPopup
          word={translationState.word}
          translation={translationState.translation}
          isLoading={translationState.isLoading}
          position={translationState.position}
          onClose={() => setTranslationState(null)}
          onSave={handleSaveWord}
          phonetics={translationState.phonetics}
        />
      )}
    </div>
  )
}
