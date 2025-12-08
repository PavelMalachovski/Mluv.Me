export interface User {
  id: number
  telegram_id: number
  username?: string
  first_name: string
  ui_language: "ru" | "uk"
  level: string
  created_at: string
}

export interface UserStats {
  streak: number
  stars: number
  words_said: number
  correct_percent: number
  messages_count: number
}

export interface ProgressData {
  date: string
  correctness_score: number
  messages_count: number
}

export interface Message {
  id: number
  user_id: number
  role: "user" | "assistant"
  text: string
  correctness_score?: number
  created_at: string
  user_mistakes?: string[]
  audio_file_path?: string
  transcript_raw?: string
}

export interface LessonResponse {
  honzik_text: string
  honzik_transcript: string
  user_mistakes: string[]
  suggestions: string[]
  stars_earned: number
  correctness_score: number
}

export interface SavedWord {
  id: number
  word_czech: string
  translation: string
  context_sentence: string
  phonetics?: string
  times_reviewed: number
  created_at: string
}

export interface WordTranslation {
  word: string
  translation: string
  target_language: "ru" | "uk"
  phonetics?: string
}
