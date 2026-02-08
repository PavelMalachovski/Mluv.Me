"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Search, Trash2, Volume2, BookmarkCheck } from "lucide-react"
import { useState, useEffect, useCallback } from "react"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import { IllustratedEmptyState } from "@/components/ui/IllustratedEmptyState"

interface SavedWord {
  id: number
  word_czech: string
  translation: string
  context_sentence: string
  phonetics?: string
  times_reviewed: number
  created_at: string
}

export default function SavedPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState("")
  const [voicesLoaded, setVoicesLoaded] = useState(false)

  // Load voices on mount (required for mobile browsers)
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      const loadVoices = () => {
        window.speechSynthesis.getVoices()
        setVoicesLoaded(true)
      }

      // Load immediately
      loadVoices()

      // Also listen for voices changed event (some browsers load async)
      window.speechSynthesis.onvoiceschanged = loadVoices

      return () => {
        window.speechSynthesis.onvoiceschanged = null
      }
    }
  }, [])

  // Mobile-compatible speech synthesis
  const speakWord = useCallback((word: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      console.warn('Speech synthesis not available')
      return
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(word)

    // Try to find Czech voice, fallback to default
    const voices = window.speechSynthesis.getVoices()
    const czechVoice = voices.find(v => v.lang.startsWith('cs'))

    if (czechVoice) {
      utterance.voice = czechVoice
      utterance.lang = 'cs-CZ'
    } else {
      // Fallback: use slower rate for clarity
      utterance.lang = 'cs-CZ'
      utterance.rate = 0.8
    }

    // Handle errors silently
    utterance.onerror = (e) => {
      console.error('Speech error:', e)
    }

    window.speechSynthesis.speak(utterance)
  }, [])

  const { data: savedWords, isLoading } = useQuery<SavedWord[]>({
    queryKey: ["saved-words", user?.telegram_id],
    queryFn: () => apiClient.getSavedWords(user!.telegram_id),
    enabled: !!user?.telegram_id,
  })

  const deleteMutation = useMutation({
    mutationFn: (wordId: number) => apiClient.deleteWord(wordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-words", user?.telegram_id] })
    },
  })

  const reviewMutation = useMutation({
    mutationFn: (wordId: number) => apiClient.patch(`/api/v1/words/${wordId}/review`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-words", user?.telegram_id] })
    },
  })

  // Auth check - use useEffect to avoid SSR issues
  useEffect(() => {
    if (!user) {
      router.push("/login")
    }
  }, [user, router])

  if (!user) {
    return null
  }

  const filteredWords = savedWords?.filter(
    (word) =>
      word.word_czech.toLowerCase().includes(searchQuery.toLowerCase()) ||
      word.translation.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="min-h-screen cream-bg landscape-bg pb-20">
      {/* Purple Header */}
      <IllustratedHeader title="Uložená slova" />

      <div className="mx-auto max-w-2xl px-4 pt-6">
        {/* Search Bar */}
        <div className="mb-6 relative">
          <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Hledat uložená slova..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="illustrated-search"
          />
        </div>

        {/* Words List or Empty State */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          </div>
        ) : filteredWords && filteredWords.length > 0 ? (
          <div className="space-y-3">
            {filteredWords.map((word) => (
              <div key={word.id} className="illustrated-card p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="mb-2 flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-foreground">
                        {word.word_czech}
                      </h3>
                      {word.phonetics && (
                        <span className="text-sm text-muted-foreground">[{word.phonetics}]</span>
                      )}
                    </div>

                    <p className="mb-2 text-sm text-foreground/80">{word.translation}</p>

                    {word.context_sentence && (
                      <div className="rounded-lg bg-primary/10 p-3">
                        <p className="text-sm italic text-primary dark:text-primary">
                          &ldquo;{word.context_sentence}&rdquo;
                        </p>
                      </div>
                    )}

                    <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                      <span>
                        Opakováno {word.times_reviewed}×
                      </span>
                      <span>•</span>
                      <span>
                        Přidáno {new Date(word.created_at).toLocaleDateString('cs-CZ')}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => speakWord(word.word_czech)}
                      className="p-2 rounded-full hover:bg-primary/10 transition-colors"
                    >
                      <Volume2 className="h-5 w-5 text-primary" />
                    </button>

                    <button
                      onClick={() => reviewMutation.mutate(word.id)}
                      className="p-2 rounded-full hover:bg-green-500/10 transition-colors"
                    >
                      <BookmarkCheck className="h-5 w-5 text-green-600" />
                    </button>

                    <button
                      onClick={() => deleteMutation.mutate(word.id)}
                      className="p-2 rounded-full hover:bg-red-500/10 transition-colors"
                    >
                      <Trash2 className="h-5 w-5 text-red-500" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <IllustratedEmptyState
            title="Zatím žádná uložená slova"
            description="Začni se učit a ukládej nová česká slova během konverzací s Honzíkem"
            buttonText="Začít procvičovat"
            buttonHref="/dashboard/practice"
          />
        )}
      </div>
    </div>
  )
}
