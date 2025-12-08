"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { BookmarkCheck, Search, Trash2, Volume2 } from "lucide-react"
import { useState } from "react"

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

  const { data: savedWords, isLoading } = useQuery<SavedWord[]>({
    queryKey: ["saved-words"],
    queryFn: () => apiClient.get("/api/v1/words"),
    enabled: !!user,
  })

  const deleteMutation = useMutation({
    mutationFn: (wordId: number) => apiClient.delete(`/api/v1/words/${wordId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-words"] })
    },
  })

  const reviewMutation = useMutation({
    mutationFn: (wordId: number) => apiClient.patch(`/api/v1/words/${wordId}/review`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["saved-words"] })
    },
  })

  if (!user) {
    router.push("/login")
    return null
  }

  const filteredWords = savedWords?.filter(
    (word) =>
      word.word_czech.toLowerCase().includes(searchQuery.toLowerCase()) ||
      word.translation.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="mx-auto max-w-2xl p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Saved Words</h1>
        <p className="text-sm text-gray-500">Your personal Czech vocabulary</p>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search saved words..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-lg border border-gray-300 py-3 pl-10 pr-4 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
      </div>

      {/* Stats Card */}
      <Card className="mb-6 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
              <BookmarkCheck className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {savedWords?.length || 0}
              </div>
              <div className="text-sm text-gray-500">Words Saved</div>
            </div>
          </div>
          <Button variant="outline" size="sm">
            Export to Anki
          </Button>
        </div>
      </Card>

      {/* Words List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
        </div>
      ) : filteredWords && filteredWords.length > 0 ? (
        <div className="space-y-3">
          {filteredWords.map((word) => (
            <Card key={word.id} className="p-4 transition-shadow hover:shadow-md">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="mb-2 flex items-center gap-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {word.word_czech}
                    </h3>
                    {word.phonetics && (
                      <span className="text-sm text-gray-500">[{word.phonetics}]</span>
                    )}
                  </div>

                  <p className="mb-2 text-sm text-gray-700">{word.translation}</p>

                  {word.context_sentence && (
                  <div className="rounded-lg bg-blue-50 p-3">
                      <p className="text-sm italic text-blue-900">
                        &ldquo;{word.context_sentence}&rdquo;
                      </p>
                  </div>
                  )}

                  <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
                    <span>
                      Reviewed {word.times_reviewed} time
                      {word.times_reviewed !== 1 ? "s" : ""}
                    </span>
                    <span>•</span>
                    <span>
                      Added {new Date(word.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => {
                      const utterance = new SpeechSynthesisUtterance(word.word_czech)
                      utterance.lang = "cs-CZ"
                      window.speechSynthesis.speak(utterance)
                    }}
                  >
                    <Volume2 className="h-5 w-5 text-blue-600" />
                  </Button>

                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => reviewMutation.mutate(word.id)}
                  >
                    <BookmarkCheck className="h-5 w-5 text-green-600" />
                  </Button>

                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => deleteMutation.mutate(word.id)}
                  >
                    <Trash2 className="h-5 w-5 text-red-600" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <div className="mb-4 text-6xl">📚</div>
          <h3 className="mb-2 text-lg font-semibold text-gray-900">
            No saved words yet
          </h3>
          <p className="mb-6 text-sm text-gray-500">
            Start learning and save new Czech words during your conversations with Honzík
          </p>
          <Button onClick={() => router.push("/dashboard")}>
            Start Practicing
          </Button>
        </Card>
      )}
    </div>
  )
}
