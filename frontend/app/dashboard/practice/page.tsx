"use client"

import { useState, useCallback, useEffect } from "react"
import dynamic from "next/dynamic"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { useTextMutation, useVoiceMutation, useTranslateWordMutation, useSaveWordMutation } from "@/lib/hooks"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { ClickableText } from "@/components/ui/ClickableText"
import { TranslationPopup } from "@/components/ui/TranslationPopup"
import { CzechTextInput } from "@/components/ui/CzechTextInput"
import { TopicSelector, TOPICS } from "@/components/features/TopicSelector"
import { LessonResponse, WordTranslation } from "@/lib/types"
import { FileText, Languages, X, Loader2 } from "lucide-react"
import { VoiceRecorderSkeleton } from "@/components/ui/skeletons"
import { CorrectionList, SuggestionBox } from "@/components/ui/CorrectionExplanation"
import { QuotaBanner, QuotaIndicator } from "@/components/features/QuotaBanner"

// Dynamic import VoiceRecorder - heavy component with Web Workers
const VoiceRecorder = dynamic(
  () => import("@/components/ui/VoiceRecorder").then((mod) => mod.VoiceRecorder),
  {
    ssr: false,
    loading: () => <VoiceRecorderSkeleton />,
  }
)

interface ConversationMessage {
  id: string
  role: "user" | "assistant"
  text: string
  response?: LessonResponse
  status: "sending" | "sent" | "error"
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

  // Restore conversation from sessionStorage on mount
  const [conversation, setConversation] = useState<ConversationMessage[]>(() => {
    if (typeof window === "undefined") return []
    try {
      const saved = sessionStorage.getItem("practice_conversation")
      return saved ? JSON.parse(saved) : []
    } catch { return [] }
  })
  const [translationState, setTranslationState] = useState<TranslationState | null>(null)
  const [inputMode, setInputMode] = useState<"text" | "voice">("text")
  const [selectedTopic, setSelectedTopic] = useState<string | null>(() => {
    if (typeof window === "undefined") return null
    return sessionStorage.getItem("practice_topic") || null
  })
  const [showTopicSelector, setShowTopicSelector] = useState(() => {
    if (typeof window === "undefined") return true
    return !sessionStorage.getItem("practice_topic")
  })
  const [quotaExceeded, setQuotaExceeded] = useState(false)

  // Persist conversation to sessionStorage on change
  useEffect(() => {
    if (conversation.length > 0) {
      // Only persist sent messages (skip "sending" status)
      const persistable = conversation.filter(m => m.status === "sent")
      sessionStorage.setItem("practice_conversation", JSON.stringify(persistable))
    }
  }, [conversation])

  // Persist selected topic
  useEffect(() => {
    if (selectedTopic) {
      sessionStorage.setItem("practice_topic", selectedTopic)
    }
  }, [selectedTopic])

  // Text message mutation with optimistic updates
  // Note: All hooks must be called before any early returns
  const sendMessage = useTextMutation({
    telegramId: user?.telegram_id ?? 0,
    includeAudio: false, // No audio for web - faster
    onSuccess: (data) => {
      console.log("Response from backend:", data)

      const lessonResponse: LessonResponse = {
        honzik_text: data.honzik_response_text || "",
        honzik_transcript: data.honzik_response_transcript || data.honzik_response_text || "",
        user_mistakes: data.corrections?.mistakes || [],
        suggestions: data.corrections?.suggestion ? [data.corrections.suggestion] : [],
        stars_earned: data.stars_earned || 0,
        correctness_score: data.corrections?.correctness_score || 0,
      }

      // Add to local conversation state
      setConversation((prev) => [
        ...prev.filter(m => m.status !== "sending"),
        {
          id: `user-${Date.now()}`,
          role: "user",
          text: data.transcript || "",
          response: lessonResponse,
          status: "sent",
        },
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: lessonResponse.honzik_text,
          response: lessonResponse,
          status: "sent",
          showTranscript: false,
          translateMode: false,
        },
      ])
    },
    onError: (err: any) => {
      // Check for quota exceeded (429)
      if (err?.response?.status === 429) {
        setQuotaExceeded(true)
      }
      // Remove the "sending" message on error
      setConversation((prev) => prev.filter(m => m.status !== "sending"))
    },
  })

  // Voice message mutation with optimistic updates
  const processVoice = useVoiceMutation({
    telegramId: user?.telegram_id ?? 0,
    onSuccess: (data) => {
      console.log("Voice response from backend:", data)

      const userTranscript = data.user_transcript || data.transcript || "🎤 Voice message"
      const lessonResponse: LessonResponse = {
        honzik_text: data.honzik_response_text || data.honzik_response_transcript || "",
        honzik_transcript: data.honzik_response_transcript || data.honzik_response_text || "",
        user_mistakes: data.corrections?.mistakes || [],
        suggestions: data.corrections?.suggestion ? [data.corrections.suggestion] : [],
        stars_earned: data.stars_earned || 0,
        correctness_score: data.corrections?.correctness_score || 0,
      }

      setConversation((prev) => [
        ...prev.filter(m => m.status !== "sending"),
        {
          id: `user-${Date.now()}`,
          role: "user",
          text: userTranscript,
          response: lessonResponse,
          status: "sent",
        },
        {
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: lessonResponse.honzik_text,
          response: lessonResponse,
          status: "sent",
          showTranscript: false,
          translateMode: false,
        },
      ])
    },
    onError: (err: any) => {
      if (err?.response?.status === 429) {
        setQuotaExceeded(true)
      }
      setConversation((prev) => prev.filter(m => m.status !== "sending"))
    },
  })

  // Translate word mutation
  const translateWord = useTranslateWordMutation({
    targetLanguage: user?.native_language || "ru",
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

  // Save word mutation with optimistic update
  const saveWord = useSaveWordMutation({
    userId: user?.id ?? 0,
    telegramId: user?.telegram_id ?? 0,
    onSuccess: () => {
      setTranslationState(null)
    },
  })

  // Handlers - useCallback must be called before early returns
  const handleTextSubmit = useCallback((text: string) => {
    if (!user?.telegram_id) return
    // Add optimistic message immediately
    setConversation((prev) => [
      ...prev,
      {
        id: `temp-${Date.now()}`,
        role: "user",
        text: text,
        status: "sending",
      },
    ])
    sendMessage.mutate(text)
  }, [sendMessage, user])

  const handleVoiceSubmit = useCallback((blob: Blob) => {
    if (!user?.telegram_id) return
    // Add optimistic message
    setConversation((prev) => [
      ...prev,
      {
        id: `temp-${Date.now()}`,
        role: "user",
        text: "🎤 Processing voice message...",
        status: "sending",
      },
    ])
    processVoice.mutate(blob)
  }, [processVoice, user])

  const toggleTranscript = useCallback((index: number) => {
    setConversation((prev) =>
      prev.map((msg, i) =>
        i === index ? { ...msg, showTranscript: !msg.showTranscript } : msg
      )
    )
  }, [])

  const toggleTranslateMode = useCallback((index: number) => {
    setConversation((prev) =>
      prev.map((msg, i) =>
        i === index ? { ...msg, translateMode: !msg.translateMode } : msg
      )
    )
    setTranslationState(null)
  }, [])

  const handleWordClick = useCallback((word: string, rect: DOMRect, messageIndex: number) => {
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
  }, [translateWord])

  const handleSaveWord = useCallback(() => {
    if (translationState?.translation) {
      saveWord.mutate({
        word_czech: translationState.word,
        translation: translationState.translation,
      })
    }
  }, [translationState, saveWord])

  const isLoading = sendMessage.isPending || processVoice.isPending

  // Auth check - use useEffect to avoid SSR issues
  useEffect(() => {
    if (!user) {
      router.push("/login")
    }
  }, [user, router])

  // Don't render if not authenticated
  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen cream-bg pb-24">
      {/* Purple Header */}
      <div className="illustrated-header relative pb-6">
        <div className="flex items-center justify-between">
          <button
            onClick={() => router.push("/dashboard")}
            className="rounded-lg p-2 text-white/80 hover:text-white hover:bg-white/10 transition-colors"
          >
            ← Back
          </button>
          <QuotaIndicator />
        </div>
        <h1 className="illustrated-header-title mt-2">Practice Czech</h1>
        <p className="text-center text-sm text-white/80 mt-1">Chat with Honzík, your AI teacher</p>
      </div>

      <div className="container mx-auto max-w-4xl px-4 pt-4">
        {/* Quota / subscription banner */}
        <QuotaBanner />

        <div className="rounded-2xl bg-white dark:bg-gray-900 p-6 shadow-sm mt-4">

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
                  sessionStorage.removeItem("practice_conversation")
                  sessionStorage.removeItem("practice_topic")
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
                <Card className="bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
                  <CardContent className="p-6">
                    <p className="text-center text-purple-900 dark:text-purple-200">
                      👋 Nazdar! Jsem Honzík. Let&apos;s start practicing Czech! Write
                      something in Czech and I&apos;ll help you improve.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                conversation.map((msg, index) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[80%] ${msg.role === "user"
                        ? `rounded-2xl rounded-br-sm bg-[#7d3bed] p-4 text-white ${msg.status === "sending" ? "opacity-70" : ""}`
                        : "rounded-2xl rounded-bl-sm bg-white dark:bg-gray-800 p-4 shadow-sm"
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

                      {/* Sending indicator */}
                      {msg.status === "sending" && (
                        <div className="flex items-center gap-2 mt-2 text-xs opacity-70">
                          <Loader2 className="h-3 w-3 animate-spin" />
                          Processing...
                        </div>
                      )}

                      {msg.role === "user" && msg.response && msg.status === "sent" && (
                        <div className="mt-3 space-y-2 border-t border-white/30 pt-3">
                          <div className="flex items-center gap-2 text-sm">
                            <span>⭐ {msg.response.stars_earned} stars</span>
                            <span>•</span>
                            <span>{msg.response.correctness_score}% correct</span>
                          </div>

                          {msg.response.user_mistakes.length > 0 && (
                            <CorrectionList
                              mistakes={msg.response.user_mistakes}
                              className="mt-2"
                            />
                          )}
                          {msg.response.suggestions.length > 0 && (
                            <SuggestionBox
                              suggestion={msg.response.suggestions[0]}
                              className="mt-2"
                            />
                          )}
                        </div>
                      )}

                      {msg.role === "assistant" && msg.response && msg.status === "sent" && (
                        <div className="mt-3 space-y-2 border-t border-gray-300 dark:border-gray-600 pt-3">
                          <div className="flex flex-wrap gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => toggleTranscript(index)}
                              className="flex items-center gap-2 text-xs bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200"
                            >
                              <FileText className="h-4 w-4" />
                              {msg.showTranscript ? "Skrýt text" : "Zobrazit text"}
                            </Button>

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
                              {msg.translateMode ? "Vypnout překlad" : "Překlad po slovech"}
                            </Button>
                          </div>

                          {msg.showTranscript && msg.response.honzik_transcript && (
                            <div className="rounded-md bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 p-3 text-sm text-gray-800 dark:text-gray-200">
                              <p className="font-semibold mb-2 text-xs text-gray-600 dark:text-gray-400">📝 Text odpovědi:</p>
                              <p className="whitespace-pre-wrap leading-relaxed">{msg.response.honzik_transcript}</p>
                            </div>
                          )}

                          {msg.translateMode && (
                            <div className="rounded-md bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-2 text-xs text-yellow-800 dark:text-yellow-200">
                              💡 Klikněte na libovolné slovo pro zobrazení překladu
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}

              {/* Loading indicator for background processing */}
              {isLoading && conversation.every(m => m.status !== "sending") && (
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

          {/* Input Area */}
          {!showTopicSelector && (
            <>
              {inputMode === "text" ? (
                <CzechTextInput
                  onSubmit={handleTextSubmit}
                  isLoading={isLoading}
                  mode={inputMode}
                  onModeChange={setInputMode}
                  placeholder="Napiš zprávu v češtině..."
                  maxLength={2000}
                />
              ) : (
                <div className="space-y-3">
                  <CzechTextInput
                    onSubmit={handleTextSubmit}
                    onVoiceStart={() => {/* VoiceRecorder handles this */ }}
                    isLoading={isLoading}
                    mode={inputMode}
                    onModeChange={setInputMode}
                  />

                  <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 p-4">
                    <VoiceRecorder
                      onRecordComplete={handleVoiceSubmit}
                      isProcessing={processVoice.isPending}
                      maxDurationSeconds={60}
                    />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Tips Section */}
        <div className="mt-6 rounded-2xl bg-white dark:bg-gray-900 p-6 shadow-sm">
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
