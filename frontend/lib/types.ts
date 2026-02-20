export interface User {
  id: number
  telegram_id: number
  username?: string
  first_name: string
  native_language: string
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

export interface Mistake {
  original: string
  corrected: string
  explanation_cs?: string
  explanation_native?: string
}

export interface LessonResponse {
  honzik_text: string
  honzik_transcript: string
  user_mistakes: Mistake[]
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

// Spaced Repetition Types
export interface ReviewWord {
  id: number
  word_czech: string
  translation: string
  context_sentence?: string
  phonetics?: string
  ease_factor: number
  interval_days: number
  sr_review_count: number
  mastery_level: "new" | "learning" | "familiar" | "known" | "mastered"
}

export interface ReviewSession {
  words: ReviewWord[]
  total_due: number
  estimated_minutes: number
}

export interface ReviewAnswerResponse {
  id: number
  word_czech: string
  new_ease_factor: number
  new_interval_days: number
  next_review_date: string
  sr_review_count: number
  mastery_level: string
}

export interface ReviewStats {
  total_words: number
  due_today: number
  mastery_breakdown: {
    new: number
    learning: number
    familiar: number
    known: number
    mastered: number
  }
  next_review_in_days: number
}

export type ReviewQuality = 0 | 1 | 2 | 3 // again, hard, good, easy

// Achievement Types
export interface Achievement {
  id: number
  code: string
  name: string
  description: string
  icon: string
  category: string
  threshold: number
  stars_reward: number
  is_unlocked: boolean
  unlocked_at: string | null
  progress: number
}

export interface AchievementProgress {
  total_achievements: number
  unlocked_achievements: number
  completion_percent: number
  category_progress: Record<string, number>
}

