/**
 * Optimistic Update Hooks for better UX
 *
 * These hooks provide instant UI feedback while waiting for server responses.
 * If the server request fails, we rollback to the previous state.
 */

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { LessonResponse, ReviewWord, ReviewAnswerResponse, SavedWord, WordTranslation } from "@/lib/types"

// ============================================================================
// Voice/Text Message Mutation with Optimistic Updates
// ============================================================================

interface ConversationMessage {
  id: string
  role: "user" | "assistant"
  text: string
  response?: LessonResponse
  status: "sending" | "sent" | "error"
  showTranscript?: boolean
  translateMode?: boolean
}

interface UseVoiceMutationOptions {
  telegramId: number
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

export function useVoiceMutation({ telegramId, onSuccess, onError }: UseVoiceMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (audioBlob: Blob) => apiClient.processVoice(telegramId, audioBlob),

    // Optimistic update - show "processing" message immediately
    onMutate: async () => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ["conversation", telegramId] })

      // Snapshot current state for rollback
      const previousConversation = queryClient.getQueryData<ConversationMessage[]>(
        ["conversation", telegramId]
      )

      // Optimistically add a "processing" message
      const tempId = `temp-${Date.now()}`
      const optimisticMessage: ConversationMessage = {
        id: tempId,
        role: "user",
        status: "sending",
        text: "🎤 Processing voice message...",
      }

      queryClient.setQueryData<ConversationMessage[]>(
        ["conversation", telegramId],
        (old = []) => [...old, optimisticMessage]
      )

      return { previousConversation, tempId }
    },

    onSuccess: (data, _variables, context) => {
      // Replace temp message with real data
      queryClient.setQueryData<ConversationMessage[]>(
        ["conversation", telegramId],
        (old = []) => {
          // Remove temp message
          const filtered = old.filter(m => m.id !== context?.tempId)

          // Get user transcript
          const userTranscript = data.user_transcript || data.transcript || "🎤 Voice message"

          // Create lesson response
          const lessonResponse: LessonResponse = {
            honzik_text: data.honzik_response_text || "",
            honzik_transcript: data.honzik_response_transcript || data.honzik_response_text || "",
            user_mistakes: data.corrections?.mistakes?.map((m: { original: string }) => m.original) || [],
            suggestions: data.corrections?.suggestion ? [data.corrections.suggestion] : [],
            stars_earned: data.stars_earned || 0,
            correctness_score: data.corrections?.correctness_score || 0,
          }

          return [
            ...filtered,
            {
              id: `user-${Date.now()}`,
              role: "user" as const,
              text: userTranscript,
              response: lessonResponse,
              status: "sent" as const,
            },
            {
              id: `assistant-${Date.now()}`,
              role: "assistant" as const,
              text: lessonResponse.honzik_text,
              response: lessonResponse,
              status: "sent" as const,
              showTranscript: false,
              translateMode: false,
            },
          ]
        }
      )

      // Invalidate stats - they will refresh
      queryClient.invalidateQueries({ queryKey: ["user-stats", telegramId] })
      queryClient.invalidateQueries({ queryKey: ["review-stats", telegramId] })

      onSuccess?.(data)
    },

    onError: (error, _variables, context) => {
      // Rollback on error
      if (context?.previousConversation) {
        queryClient.setQueryData(
          ["conversation", telegramId],
          context.previousConversation
        )
      }
      onError?.(error as Error)
    },
  })
}

// ============================================================================
// Text Message Mutation with Optimistic Updates
// ============================================================================

interface UseTextMutationOptions {
  telegramId: number
  includeAudio?: boolean
  onSuccess?: (data: any) => void
  onError?: (error: Error) => void
}

export function useTextMutation({
  telegramId,
  includeAudio = false,
  onSuccess,
  onError
}: UseTextMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (text: string) => apiClient.processText(telegramId, text, includeAudio),

    // Optimistic update - show user message immediately
    onMutate: async (text) => {
      await queryClient.cancelQueries({ queryKey: ["conversation", telegramId] })

      const previousConversation = queryClient.getQueryData<ConversationMessage[]>(
        ["conversation", telegramId]
      )

      const tempId = `temp-${Date.now()}`
      const optimisticMessage: ConversationMessage = {
        id: tempId,
        role: "user",
        status: "sending",
        text: text,
      }

      queryClient.setQueryData<ConversationMessage[]>(
        ["conversation", telegramId],
        (old = []) => [...old, optimisticMessage]
      )

      return { previousConversation, tempId, text }
    },

    onSuccess: (data, _variables, context) => {
      queryClient.setQueryData<ConversationMessage[]>(
        ["conversation", telegramId],
        (old = []) => {
          const filtered = old.filter(m => m.id !== context?.tempId)

          const lessonResponse: LessonResponse = {
            honzik_text: data.honzik_response_text || "",
            honzik_transcript: data.honzik_response_transcript || data.honzik_response_text || "",
            user_mistakes: data.corrections?.mistakes?.map((m: { original: string }) => m.original) || [],
            suggestions: data.corrections?.suggestion ? [data.corrections.suggestion] : [],
            stars_earned: data.stars_earned || 0,
            correctness_score: data.corrections?.correctness_score || 0,
          }

          return [
            ...filtered,
            {
              id: `user-${Date.now()}`,
              role: "user" as const,
              text: context?.text || "",
              response: lessonResponse,
              status: "sent" as const,
            },
            {
              id: `assistant-${Date.now()}`,
              role: "assistant" as const,
              text: lessonResponse.honzik_text,
              response: lessonResponse,
              status: "sent" as const,
              showTranscript: false,
              translateMode: false,
            },
          ]
        }
      )

      queryClient.invalidateQueries({ queryKey: ["user-stats", telegramId] })
      queryClient.invalidateQueries({ queryKey: ["review-stats", telegramId] })

      onSuccess?.(data)
    },

    onError: (error, _variables, context) => {
      if (context?.previousConversation) {
        queryClient.setQueryData(
          ["conversation", telegramId],
          context.previousConversation
        )
      }
      onError?.(error as Error)
    },
  })
}

// ============================================================================
// Save Word Mutation with Optimistic Updates
// ============================================================================

interface SaveWordInput {
  word_czech: string
  translation: string
  context_sentence?: string
  phonetics?: string
}

interface UseSaveWordMutationOptions {
  userId: number
  telegramId: number
  onSuccess?: (data: SavedWord) => void
  onError?: (error: Error) => void
}

export function useSaveWordMutation({
  userId,
  telegramId,
  onSuccess,
  onError
}: UseSaveWordMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (wordData: SaveWordInput) => apiClient.saveWord(userId, wordData),

    // Optimistic update - add word to list immediately
    onMutate: async (newWord) => {
      await queryClient.cancelQueries({ queryKey: ["saved-words", telegramId] })

      const previousWords = queryClient.getQueryData<SavedWord[]>(
        ["saved-words", telegramId]
      )

      // Create optimistic word entry
      const optimisticWord: SavedWord = {
        id: -Date.now(), // Temporary negative ID
        word_czech: newWord.word_czech,
        translation: newWord.translation,
        context_sentence: newWord.context_sentence || "",
        phonetics: newWord.phonetics,
        times_reviewed: 0,
        created_at: new Date().toISOString(),
      }

      queryClient.setQueryData<SavedWord[]>(
        ["saved-words", telegramId],
        (old = []) => [optimisticWord, ...old]
      )

      return { previousWords, optimisticWord }
    },

    onSuccess: (savedWord, _variables, context) => {
      // Replace optimistic word with real one from server
      queryClient.setQueryData<SavedWord[]>(
        ["saved-words", telegramId],
        (old = []) => old.map(w =>
          w.id === context?.optimisticWord.id ? savedWord : w
        )
      )

      // Update review stats
      queryClient.invalidateQueries({ queryKey: ["review-stats", telegramId] })

      onSuccess?.(savedWord)
    },

    onError: (error, _variables, context) => {
      if (context?.previousWords) {
        queryClient.setQueryData(
          ["saved-words", telegramId],
          context.previousWords
        )
      }
      onError?.(error as Error)
    },
  })
}

// ============================================================================
// Delete Word Mutation with Optimistic Updates
// ============================================================================

interface UseDeleteWordMutationOptions {
  telegramId: number
  onSuccess?: () => void
  onError?: (error: Error) => void
}

export function useDeleteWordMutation({
  telegramId,
  onSuccess,
  onError
}: UseDeleteWordMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (wordId: number) => apiClient.deleteWord(wordId),

    // Optimistic update - remove word immediately
    onMutate: async (wordId) => {
      await queryClient.cancelQueries({ queryKey: ["saved-words", telegramId] })

      const previousWords = queryClient.getQueryData<SavedWord[]>(
        ["saved-words", telegramId]
      )

      queryClient.setQueryData<SavedWord[]>(
        ["saved-words", telegramId],
        (old = []) => old.filter(w => w.id !== wordId)
      )

      return { previousWords, wordId }
    },

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["review-stats", telegramId] })
      onSuccess?.()
    },

    onError: (error, _variables, context) => {
      if (context?.previousWords) {
        queryClient.setQueryData(
          ["saved-words", telegramId],
          context.previousWords
        )
      }
      onError?.(error as Error)
    },
  })
}

// ============================================================================
// Review Answer Mutation with Optimistic Updates
// ============================================================================

interface UseReviewAnswerMutationOptions {
  telegramId: number
  onSuccess?: (data: ReviewAnswerResponse, currentWord: ReviewWord) => void
  onError?: (error: Error) => void
}

export function useReviewAnswerMutation({
  telegramId,
  onSuccess,
  onError
}: UseReviewAnswerMutationOptions) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ wordId, quality }: { wordId: number; quality: 0 | 1 | 2 | 3 }) =>
      apiClient.submitReviewAnswer(wordId, quality),

    // Optimistic update - move to next word immediately
    onMutate: async ({ wordId }) => {
      await queryClient.cancelQueries({ queryKey: ["words-for-review", telegramId] })

      const previousWords = queryClient.getQueryData<ReviewWord[]>(
        ["words-for-review", telegramId]
      )

      // Find current word for callback
      const currentWord = previousWords?.find(w => w.id === wordId)

      // Optimistically remove the reviewed word from the queue
      queryClient.setQueryData<ReviewWord[]>(
        ["words-for-review", telegramId],
        (old = []) => old.filter(w => w.id !== wordId)
      )

      return { previousWords, currentWord }
    },

    onSuccess: (data, _variables, context) => {
      // Update review stats
      queryClient.invalidateQueries({ queryKey: ["review-stats", telegramId] })

      if (context?.currentWord) {
        onSuccess?.(data, context.currentWord)
      }
    },

    onError: (error, _variables, context) => {
      if (context?.previousWords) {
        queryClient.setQueryData(
          ["words-for-review", telegramId],
          context.previousWords
        )
      }
      onError?.(error as Error)
    },
  })
}

// ============================================================================
// Translate Word Mutation (no optimistic update needed - just loading state)
// ============================================================================

interface UseTranslateWordOptions {
  targetLanguage?: "ru" | "uk"
  onSuccess?: (data: WordTranslation) => void
  onError?: (error: Error) => void
}

export function useTranslateWordMutation({
  targetLanguage = "ru",
  onSuccess,
  onError
}: UseTranslateWordOptions = {}) {
  return useMutation({
    mutationFn: (word: string) => apiClient.translateWord(word, targetLanguage) as Promise<WordTranslation>,
    onSuccess,
    onError: (error) => onError?.(error as Error),
  })
}
