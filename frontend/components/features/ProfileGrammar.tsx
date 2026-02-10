"use client"

import { useState, useEffect, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import {
  BookOpen, ChevronRight, ChevronDown, Trophy,
  Target, CheckCircle2, AlertTriangle, Sparkles,
  RotateCcw, ArrowRight,
} from "lucide-react"
import { apiClient } from "@/lib/api-client"

// ===== Types =====

interface GrammarRule {
  id: number
  code: string
  category: string
  subcategory?: string
  level: string
  title_cs: string
  rule_cs: string
  explanation_cs?: string
  examples?: Array<{ correct: string; incorrect?: string; note?: string }>
  mnemonic?: string
  common_mistakes?: Array<{ wrong: string; correct: string; note?: string }>
  source_ref?: string
}

interface CategoryInfo {
  category: string
  count: number
}

interface ProgressSummary {
  total_rules: number
  practiced_rules: number
  mastered_rules: number
  weak_rules: number
  average_accuracy: number
}

interface ProfileGrammarProps {
  userId: number
  telegramId: number
  level?: string
}

// Category display names
const CATEGORY_LABELS: Record<string, { label: string; emoji: string }> = {
  pravopis_hlasky: { label: "Pravopis – hlásky", emoji: "🔤" },
  pravopis_interpunkce: { label: "Interpunkce", emoji: "✏️" },
  pravopis_velka_pismena: { label: "Velká písmena", emoji: "🔠" },
  tvaroslovi_podstatna: { label: "Podstatná jména", emoji: "📝" },
  tvaroslovi_pridavna: { label: "Přídavná jména", emoji: "📋" },
  tvaroslovi_zajmena: { label: "Zájmena", emoji: "👆" },
  tvaroslovi_slovesa: { label: "Slovesa", emoji: "🏃" },
  tvaroslovi_cislovky: { label: "Číslovky", emoji: "🔢" },
  skladba: { label: "Skladba", emoji: "🧱" },
  stylistika: { label: "Stylistika", emoji: "🎨" },
  vyslovnost: { label: "Výslovnost", emoji: "🗣️" },
}

type TabState = "daily" | "categories" | "progress"

// ===== Main Component =====

export function ProfileGrammar({
  userId,
  telegramId,
  level = "beginner",
}: ProfileGrammarProps) {
  const [tab, setTab] = useState<TabState>("daily")
  const [dailyRule, setDailyRule] = useState<GrammarRule | null>(null)
  const [categories, setCategories] = useState<CategoryInfo[]>([])
  const [progress, setProgress] = useState<ProgressSummary | null>(null)
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)
  const [categoryRules, setCategoryRules] = useState<GrammarRule[]>([])
  const [expandedRule, setExpandedRule] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Fetch daily rule
  const fetchDailyRule = useCallback(async () => {
    try {
      const data = await apiClient.get(`/api/v1/grammar/daily-rule/${telegramId}`)
      if (data.rule) setDailyRule(data.rule)
    } catch (e) {
      console.error("Failed to fetch daily rule:", e)
    }
  }, [telegramId])

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const data = await apiClient.get("/api/v1/grammar/categories")
      setCategories(data)
    } catch (e) {
      console.error("Failed to fetch categories:", e)
    }
  }, [])

  // Fetch progress
  const fetchProgress = useCallback(async () => {
    try {
      const data = await apiClient.get(`/api/v1/grammar/progress/${telegramId}`)
      setProgress(data)
    } catch (e) {
      console.error("Failed to fetch progress:", e)
    }
  }, [telegramId])

  // Load data for current tab
  useEffect(() => {
    if (tab === "daily") fetchDailyRule()
    else if (tab === "categories") fetchCategories()
    else if (tab === "progress") fetchProgress()
  }, [tab, fetchDailyRule, fetchCategories, fetchProgress])

  // Fetch rules for a category
  const loadCategoryRules = async (category: string) => {
    if (expandedCategory === category) {
      setExpandedCategory(null)
      setCategoryRules([])
      return
    }
    setIsLoading(true)
    try {
      const data = await apiClient.get(`/api/v1/grammar/rules?category=${category}&limit=20`)
      setCategoryRules(data)
      setExpandedCategory(category)
    } catch (e) {
      console.error("Failed to fetch category rules:", e)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="illustrated-card p-4 mb-6">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="w-5 h-5 text-emerald-500" />
        <h3 className="font-semibold text-foreground">Gramatika</h3>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
        {([
          { key: "daily", label: "Pravidlo dne", icon: "💡" },
          { key: "categories", label: "Přehled", icon: "📚" },
          { key: "progress", label: "Pokrok", icon: "📊" },
        ] as { key: TabState; label: string; icon: string }[]).map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 text-xs font-medium py-2 px-2 rounded-md transition-all ${
              tab === t.key
                ? "bg-white dark:bg-gray-700 shadow-sm text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            {t.icon} {t.label}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* === DAILY RULE === */}
        {tab === "daily" && (
          <motion.div
            key="daily"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {dailyRule ? (
              <div className="space-y-3">
                {/* Rule title */}
                <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-4">
                  <div className="flex items-start gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    <h4 className="font-bold text-sm text-foreground">
                      {dailyRule.title_cs}
                    </h4>
                  </div>
                  <p className="text-sm text-foreground/80 leading-relaxed">
                    {dailyRule.rule_cs}
                  </p>
                </div>

                {/* Explanation */}
                {dailyRule.explanation_cs && (
                  <p className="text-xs text-muted-foreground px-1">
                    💬 {dailyRule.explanation_cs}
                  </p>
                )}

                {/* Examples */}
                {dailyRule.examples && dailyRule.examples.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-xs font-medium text-muted-foreground px-1">Příklady:</p>
                    {dailyRule.examples.slice(0, 3).map((ex, i) => (
                      <div key={i} className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-lg px-3 py-2 text-sm">
                        <span className="text-green-600 dark:text-green-400">✓ {ex.correct}</span>
                        {ex.incorrect && (
                          <span className="text-red-500 ml-2 text-xs">✗ {ex.incorrect}</span>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Mnemonic */}
                {dailyRule.mnemonic && (
                  <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg px-3 py-2 text-xs">
                    🧠 <strong>Pomůcka:</strong> {dailyRule.mnemonic}
                  </div>
                )}

                {/* Source */}
                <p className="text-[10px] text-muted-foreground text-right">
                  📖 {dailyRule.source_ref || "Internetová jazyková příručka ÚJČ"}
                </p>

                {/* Refresh button */}
                <button
                  onClick={fetchDailyRule}
                  className="w-full py-2 rounded-lg text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors flex items-center justify-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" />
                  Další pravidlo
                </button>
              </div>
            ) : (
              <div className="text-center py-6">
                <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Načítám pravidlo dne...</p>
              </div>
            )}
          </motion.div>
        )}

        {/* === CATEGORIES === */}
        {tab === "categories" && (
          <motion.div
            key="categories"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-1"
          >
            {categories.length > 0 ? (
              categories.map((cat) => {
                const info = CATEGORY_LABELS[cat.category] || { label: cat.category, emoji: "📘" }
                const isExpanded = expandedCategory === cat.category
                return (
                  <div key={cat.category}>
                    <button
                      onClick={() => loadCategoryRules(cat.category)}
                      className="w-full flex items-center gap-2 p-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
                    >
                      <span className="text-lg">{info.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{info.label}</p>
                        <p className="text-xs text-muted-foreground">{cat.count} pravidel</p>
                      </div>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                      )}
                    </button>

                    {/* Expanded rules for this category */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          {isLoading ? (
                            <div className="py-4 text-center">
                              <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-emerald-500 mx-auto" />
                            </div>
                          ) : (
                            <div className="pl-8 pb-2 space-y-1">
                              {categoryRules.map((rule) => (
                                <div key={rule.id}>
                                  <button
                                    onClick={() => setExpandedRule(expandedRule === rule.id ? null : rule.id)}
                                    className="w-full text-left text-xs py-1.5 px-2 rounded hover:bg-emerald-50 dark:hover:bg-emerald-900/10 transition-colors text-foreground"
                                  >
                                    <span className="font-medium">{rule.title_cs}</span>
                                    <span className="text-muted-foreground ml-1">({rule.level})</span>
                                  </button>
                                  <AnimatePresence>
                                    {expandedRule === rule.id && (
                                      <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                      >
                                        <div className="ml-2 mb-2 p-2 bg-gray-50 dark:bg-gray-800 rounded-lg text-xs space-y-1">
                                          <p className="text-foreground/80">{rule.rule_cs}</p>
                                          {rule.examples && rule.examples.length > 0 && (
                                            <p className="text-green-600 dark:text-green-400">
                                              ✓ {rule.examples[0].correct}
                                            </p>
                                          )}
                                        </div>
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </div>
                              ))}
                            </div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )
              })
            ) : (
              <div className="text-center py-6">
                <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Načítám kategorie...</p>
              </div>
            )}
          </motion.div>
        )}

        {/* === PROGRESS === */}
        {tab === "progress" && (
          <motion.div
            key="progress"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {progress ? (
              <div className="space-y-3">
                {/* Stats grid */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-lg p-3 text-center">
                    <Target className="w-5 h-5 text-emerald-500 mx-auto mb-1" />
                    <p className="text-lg font-bold text-foreground">{progress.practiced_rules}</p>
                    <p className="text-[10px] text-muted-foreground">Procvičeno</p>
                  </div>
                  <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3 text-center">
                    <Trophy className="w-5 h-5 text-amber-500 mx-auto mb-1" />
                    <p className="text-lg font-bold text-foreground">{progress.mastered_rules}</p>
                    <p className="text-[10px] text-muted-foreground">Zvládnuto</p>
                  </div>
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 text-center">
                    <CheckCircle2 className="w-5 h-5 text-blue-500 mx-auto mb-1" />
                    <p className="text-lg font-bold text-foreground">{progress.average_accuracy}%</p>
                    <p className="text-[10px] text-muted-foreground">Přesnost</p>
                  </div>
                  <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 text-center">
                    <AlertTriangle className="w-5 h-5 text-red-400 mx-auto mb-1" />
                    <p className="text-lg font-bold text-foreground">{progress.weak_rules}</p>
                    <p className="text-[10px] text-muted-foreground">K opakování</p>
                  </div>
                </div>

                {/* Progress bar */}
                <div>
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>Celkový pokrok</span>
                    <span>{progress.practiced_rules} / {progress.total_rules}</span>
                  </div>
                  <div className="h-2.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-emerald-400 to-emerald-600 rounded-full"
                      initial={{ width: 0 }}
                      animate={{
                        width: `${progress.total_rules > 0
                          ? (progress.practiced_rules / progress.total_rules) * 100
                          : 0
                        }%`,
                      }}
                      transition={{ duration: 0.8 }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-6">
                <Target className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">
                  Začni hrát hry a tvůj pokrok se tu zobrazí!
                </p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
