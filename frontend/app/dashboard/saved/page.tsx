"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Search, Trash2, Volume2, BookmarkCheck, RotateCcw, Eye, EyeOff, Check, X, Shuffle } from "lucide-react"
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
  const [reviewMode, setReviewMode] = useState(false)
  const [reviewIndex, setReviewIndex] = useState(0)
  const [showTranslation, setShowTranslation] = useState(false)
  const [reviewQueue, setReviewQueue] = useState<SavedWord[]>([])
  const [reviewStats, setReviewStats] = useState({ known: 0, unknown: 0 })

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

  // Start review mode — shuffle words
  const startReview = useCallback(() => {
    if (!savedWords || savedWords.length === 0) return
    const shuffled = [...savedWords].sort(() => Math.random() - 0.5)
    setReviewQueue(shuffled)
    setReviewIndex(0)
    setShowTranslation(false)
    setReviewStats({ known: 0, unknown: 0 })
    setReviewMode(true)
  }, [savedWords])

  // Mark word as known/unknown in review
  const handleReviewAnswer = useCallback((known: boolean) => {
    setReviewStats((prev) => ({
      known: prev.known + (known ? 1 : 0),
      unknown: prev.unknown + (known ? 0 : 1),
    }))
    // If known, mark as reviewed in backend
    if (known && reviewQueue[reviewIndex]) {
      reviewMutation.mutate(reviewQueue[reviewIndex].id)
    }
    // Move to next card
    setShowTranslation(false)
    setReviewIndex((prev) => prev + 1)
  }, [reviewIndex, reviewQueue, reviewMutation])

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
        {/* Review Mode */}
        {reviewMode ? (
          <div className="mb-6">
            {reviewIndex < reviewQueue.length ? (
              <div className="illustrated-card p-6">
                {/* Progress */}
                <div className="flex items-center justify-between mb-4">
                  <span className="text-xs text-muted-foreground">
                    {reviewIndex + 1} / {reviewQueue.length}
                  </span>
                  <button
                    onClick={() => setReviewMode(false)}
                    className="text-xs text-red-500 hover:text-red-600"
                  >
                    Ukončit
                  </button>
                </div>
                <div className="h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full mb-6 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-amber-500 rounded-full transition-all"
                    style={{ width: `${((reviewIndex + 1) / reviewQueue.length) * 100}%` }}
                  />
                </div>

                {/* Flashcard */}
                <div className="text-center py-6">
                  <h2 className="text-3xl font-bold text-foreground mb-2">
                    {reviewQueue[reviewIndex].word_czech}
                  </h2>
                  {reviewQueue[reviewIndex].phonetics && (
                    <p className="text-sm text-muted-foreground mb-2">
                      [{reviewQueue[reviewIndex].phonetics}]
                    </p>
                  )}
                  <button
                    onClick={() => speakWord(reviewQueue[reviewIndex].word_czech)}
                    className="p-2 rounded-full hover:bg-primary/10 transition-colors inline-block mb-4"
                  >
                    <Volume2 className="h-5 w-5 text-primary" />
                  </button>

                  {/* Translation (hidden by default) */}
                  {showTranslation ? (
                    <div className="mt-4 py-3 px-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl">
                      <p className="text-lg font-medium text-foreground">
                        {reviewQueue[reviewIndex].translation}
                      </p>
                      {reviewQueue[reviewIndex].context_sentence && (
                        <p className="text-xs text-muted-foreground mt-1 italic">
                          &ldquo;{reviewQueue[reviewIndex].context_sentence}&rdquo;
                        </p>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowTranslation(true)}
                      className="mt-4 px-6 py-3 rounded-xl bg-gray-100 dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center gap-2 mx-auto"
                    >
                      <Eye className="w-4 h-4" />
                      Zobrazit překlad
                    </button>
                  )}
                </div>

                {/* Know / Don't know buttons */}
                {showTranslation && (
                  <div className="flex gap-3 mt-6">
                    <button
                      onClick={() => handleReviewAnswer(false)}
                      className="flex-1 py-3 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 font-medium text-sm hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors flex items-center justify-center gap-2"
                    >
                      <X className="w-4 h-4" />
                      Nevím
                    </button>
                    <button
                      onClick={() => handleReviewAnswer(true)}
                      className="flex-1 py-3 rounded-xl bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 font-medium text-sm hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors flex items-center justify-center gap-2"
                    >
                      <Check className="w-4 h-4" />
                      Vím
                    </button>
                  </div>
                )}
              </div>
            ) : (
              /* Review Complete */
              <div className="illustrated-card p-6 text-center">
                <div className="text-4xl mb-3">🎉</div>
                <h3 className="text-xl font-bold text-foreground mb-2">Hotovo!</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Prošel jsi {reviewQueue.length} slov
                </p>
                <div className="flex justify-center gap-6 mb-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-500">{reviewStats.known}</p>
                    <p className="text-xs text-muted-foreground">Umím</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-red-500">{reviewStats.unknown}</p>
                    <p className="text-xs text-muted-foreground">K opakování</p>
                  </div>
                </div>
                <div className="flex gap-3 justify-center">
                  <button
                    onClick={() => setReviewMode(false)}
                    className="px-4 py-2 rounded-xl bg-gray-100 dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300"
                  >
                    Zpět na seznam
                  </button>
                  <button
                    onClick={startReview}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-500 to-amber-500 text-white text-sm font-bold flex items-center gap-1"
                  >
                    <RotateCcw className="w-4 h-4" />
                    Znovu
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
        {/* Review Start Button */}
        {savedWords && savedWords.length >= 3 && (
          <button
            onClick={startReview}
            className="w-full mb-4 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-amber-500 text-white text-sm font-bold hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            <Shuffle className="w-4 h-4" />
            Opakovat slova ({savedWords.length})
          </button>
        )}

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
        </>
        )}
      </div>
    </div>
  )
}
