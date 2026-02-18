"use client"

import { useState, useCallback } from "react"
import { useQuery } from "@tanstack/react-query"
import { motion, AnimatePresence } from "framer-motion"
import {
  BookOpen, ChevronRight, ChevronDown,
  Sparkles,
  RotateCcw, RefreshCw, AlertCircle,
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

interface DailyRuleResponse {
  rule: GrammarRule | null
  message?: string
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

type TabState = "daily" | "categories"

// ===== Error / Empty inline components =====

function InlineError({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="text-center py-6 space-y-2">
      <AlertCircle className="w-8 h-8 text-red-400 mx-auto" />
      <p className="text-sm text-red-500">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-1 text-xs font-medium text-primary hover:underline"
        >
          <RefreshCw className="w-3 h-3" /> Zkusit znovu
        </button>
      )}
    </div>
  )
}

function InlineLoading({ message }: { message: string }) {
  return (
    <div className="text-center py-6 space-y-2">
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-gray-300 border-t-emerald-500 mx-auto" />
      <p className="text-sm text-muted-foreground">{message}</p>
    </div>
  )
}

// ===== Main Component =====

export function ProfileGrammar({
  userId,
  telegramId,
  level = "beginner",
}: ProfileGrammarProps) {
  const [tab, setTab] = useState<TabState>("daily")
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null)
  const [expandedRule, setExpandedRule] = useState<number | null>(null)
  const [dailyRuleIndex, setDailyRuleIndex] = useState(0)

  // --- React Query: Daily Rule ---
  const {
    data: dailyData,
    isLoading: dailyLoading,
    isError: dailyError,
    refetch: refetchDaily,
  } = useQuery<DailyRuleResponse>({
    queryKey: ["grammar-daily-rule", telegramId, dailyRuleIndex],
    queryFn: () => apiClient.get(`/api/v1/grammar/daily-rule/${telegramId}`),
    enabled: tab === "daily",
    staleTime: 0,
    retry: 2,
  })

  // --- React Query: Categories ---
  const {
    data: categories,
    isLoading: categoriesLoading,
    isError: categoriesError,
    refetch: refetchCategories,
  } = useQuery<CategoryInfo[]>({
    queryKey: ["grammar-categories"],
    queryFn: () => apiClient.get("/api/v1/grammar/categories"),
    enabled: tab === "categories",
    staleTime: 10 * 60 * 1000,
    retry: 2,
  })

  // --- React Query: Category Rules (when expanded) ---
  const {
    data: categoryRules,
    isLoading: rulesLoading,
  } = useQuery<GrammarRule[]>({
    queryKey: ["grammar-rules", expandedCategory],
    queryFn: () => apiClient.get(`/api/v1/grammar/rules?category=${expandedCategory}&limit=20`),
    enabled: !!expandedCategory,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })

  const toggleCategory = useCallback((category: string) => {
    setExpandedCategory((prev) => (prev === category ? null : category))
    setExpandedRule(null)
  }, [])

  const dailyRule = dailyData?.rule ?? null

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
            {dailyLoading ? (
              <InlineLoading message="Načítám pravidlo dne..." />
            ) : dailyError ? (
              <InlineError message="Nepodařilo se načíst pravidlo" onRetry={() => refetchDaily()} />
            ) : dailyRule ? (
              <div className="space-y-3">
                <div className="bg-emerald-50 dark:bg-emerald-900/20 rounded-xl p-4">
                  <div className="flex items-start gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                    <h4 className="font-bold text-sm text-foreground">{dailyRule.title_cs}</h4>
                  </div>
                  <p className="text-sm text-foreground/80 leading-relaxed">{dailyRule.rule_cs}</p>
                </div>

                {dailyRule.explanation_cs && (
                  <p className="text-xs text-muted-foreground px-1">💬 {dailyRule.explanation_cs}</p>
                )}

                {dailyRule.examples && dailyRule.examples.length > 0 && (
                  <div className="space-y-1.5">
                    <p className="text-xs font-medium text-muted-foreground px-1">Příklady:</p>
                    {dailyRule.examples.slice(0, 3).map((ex, i) => (
                      <div key={i} className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-lg px-3 py-2 text-sm">
                        <span className="text-green-600 dark:text-green-400">✓ {ex.correct}</span>
                        {ex.incorrect && <span className="text-red-500 ml-2 text-xs">✗ {ex.incorrect}</span>}
                      </div>
                    ))}
                  </div>
                )}

                {dailyRule.mnemonic && (
                  <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg px-3 py-2 text-xs">
                    🧠 <strong>Pomůcka:</strong> {dailyRule.mnemonic}
                  </div>
                )}

                <button
                  onClick={() => setDailyRuleIndex((i) => i + 1)}
                  className="w-full py-2 rounded-lg text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors flex items-center justify-center gap-1"
                >
                  <RotateCcw className="w-3 h-3" />
                  Další pravidlo
                </button>
              </div>
            ) : (
              <div className="text-center py-6">
                <BookOpen className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Žádné pravidlo k zobrazení</p>
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
            {categoriesLoading ? (
              <InlineLoading message="Načítám kategorie..." />
            ) : categoriesError ? (
              <InlineError message="Nepodařilo se načíst kategorie" onRetry={() => refetchCategories()} />
            ) : categories && categories.length > 0 ? (
              categories.map((cat) => {
                const info = CATEGORY_LABELS[cat.category] || { label: cat.category, emoji: "📘" }
                const isExpanded = expandedCategory === cat.category
                return (
                  <div key={cat.category}>
                    <button
                      onClick={() => toggleCategory(cat.category)}
                      className="w-full flex items-center gap-2 p-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors text-left"
                    >
                      <span className="text-lg">{info.emoji}</span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{info.label}</p>
                        <p className="text-xs text-muted-foreground">{cat.count} pravidel</p>
                      </div>
                      {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                    </button>

                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          {rulesLoading ? (
                            <div className="py-4 text-center">
                              <div className="h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-emerald-500 mx-auto" />
                            </div>
                          ) : categoryRules && categoryRules.length > 0 ? (
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
                                            <p className="text-green-600 dark:text-green-400">✓ {rule.examples[0].correct}</p>
                                          )}
                                        </div>
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="pl-8 py-2 text-xs text-muted-foreground">Žádná pravidla</p>
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
                <p className="text-sm text-muted-foreground">Žádné kategorie</p>
              </div>
            )}
          </motion.div>
        )}


      </AnimatePresence>
    </div>
  )
}
