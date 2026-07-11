"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams } from "next/navigation"
import { useMutation } from "@tanstack/react-query"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { ClickableText } from "@/components/ui/ClickableText"
import { TranslationPopup } from "@/components/ui/TranslationPopup"
import { WordTranslation } from "@/lib/types"
import { Button } from "@/components/ui/button"
import { Languages, ChevronDown } from "lucide-react"

// ---------- Language list (same as settings) ----------
interface LangOption {
    code: string
    flag: string
    name: string
}

const PINNED_LANGS: LangOption[] = [
    { code: "ru", flag: "🇷🇺", name: "Ruština" },
    { code: "uk", flag: "🇺🇦", name: "Ukrajinština" },
    { code: "pl", flag: "🇵🇱", name: "Polština" },
    { code: "vi", flag: "🇻🇳", name: "Vietnamština" },
    { code: "hi", flag: "🇮🇳", name: "Hindština" },
]

const OTHER_LANGS: LangOption[] = [
    { code: "af", flag: "🇿🇦", name: "Afrikánština" },
    { code: "sq", flag: "🇦🇱", name: "Albánština" },
    { code: "en", flag: "🇬🇧", name: "Angličtina" },
    { code: "ar", flag: "🇸🇦", name: "Arabština" },
    { code: "hy", flag: "🇦🇲", name: "Arménština" },
    { code: "az", flag: "🇦🇿", name: "Ázerbájdžánština" },
    { code: "be", flag: "🇧🇾", name: "Běloruština" },
    { code: "bn", flag: "🇧🇩", name: "Bengálština" },
    { code: "bg", flag: "🇧🇬", name: "Bulharština" },
    { code: "zh", flag: "🇨🇳", name: "Čínština" },
    { code: "da", flag: "🇩🇰", name: "Dánština" },
    { code: "et", flag: "🇪🇪", name: "Estonština" },
    { code: "fi", flag: "🇫🇮", name: "Finština" },
    { code: "fr", flag: "🇫🇷", name: "Francouzština" },
    { code: "ka", flag: "🇬🇪", name: "Gruzínština" },
    { code: "he", flag: "🇮🇱", name: "Hebrejština" },
    { code: "nl", flag: "🇳🇱", name: "Holandština" },
    { code: "hr", flag: "🇭🇷", name: "Chorvatština" },
    { code: "id", flag: "🇮🇩", name: "Indonéština" },
    { code: "ga", flag: "🇮🇪", name: "Irština" },
    { code: "it", flag: "🇮🇹", name: "Italština" },
    { code: "ja", flag: "🇯🇵", name: "Japonština" },
    { code: "kk", flag: "🇰🇿", name: "Kazaština" },
    { code: "ko", flag: "🇰🇷", name: "Korejština" },
    { code: "ky", flag: "🇰🇬", name: "Kyrgyzština" },
    { code: "lo", flag: "🇱🇦", name: "Laoština" },
    { code: "lt", flag: "🇱🇹", name: "Litevština" },
    { code: "lv", flag: "🇱🇻", name: "Lotyšština" },
    { code: "hu", flag: "🇭🇺", name: "Maďarština" },
    { code: "mn", flag: "🇲🇳", name: "Mongolština" },
    { code: "my", flag: "🇲🇲", name: "Myanmarština" },
    { code: "de", flag: "🇩🇪", name: "Němčina" },
    { code: "no", flag: "🇳🇴", name: "Norština" },
    { code: "pa", flag: "🇮🇳", name: "Paňdžábština" },
    { code: "fa", flag: "🇮🇷", name: "Perština" },
    { code: "pt", flag: "🇵🇹", name: "Portugalština" },
    { code: "ro", flag: "🇷🇴", name: "Rumunština" },
    { code: "el", flag: "🇬🇷", name: "Řečtina" },
    { code: "sk", flag: "🇸🇰", name: "Slovenčina" },
    { code: "sl", flag: "🇸🇮", name: "Slovinština" },
    { code: "sr", flag: "🇷🇸", name: "Srbština" },
    { code: "su", flag: "🇮🇩", name: "Sundánština" },
    { code: "sw", flag: "🇰🇪", name: "Svahilština" },
    { code: "es", flag: "🇪🇸", name: "Španělština" },
    { code: "sv", flag: "🇸🇪", name: "Švédština" },
    { code: "tg", flag: "🇹🇯", name: "Tádžičtina" },
    { code: "tl", flag: "🇵🇭", name: "Tagalogština" },
    { code: "th", flag: "🇹🇭", name: "Thajština" },
    { code: "tr", flag: "🇹🇷", name: "Turečtina" },
    { code: "uz", flag: "🇺🇿", name: "Uzbečtina" },
]

const ALL_LANGS: LangOption[] = [...PINNED_LANGS, ...OTHER_LANGS]

interface TranslationState {
    word: string
    translation: string | null
    phonetics: string | null
    isLoading: boolean
    position: { top: number; left: number }
}

function ResponsePageContent() {
    const searchParams = useSearchParams()
    const user = useAuthStore((state) => state.user)
    const updateUser = useAuthStore((state) => state.updateUser)
    const [text, setText] = useState("")
    const [translateMode, setTranslateMode] = useState(true) // Включен по умолчанию
    const [translationState, setTranslationState] = useState<TranslationState | null>(null)
    const [targetLang, setTargetLang] = useState<string>(user?.native_language || "ru")
    const [showLangPicker, setShowLangPicker] = useState(false)

    useEffect(() => {
        // Получаем текст из URL параметров
        const textParam = searchParams.get("text")
        if (textParam) {
            setText(decodeURIComponent(textParam))
        }
    }, [searchParams])

    const translateWord = useMutation({
        mutationFn: (word: string) =>
            apiClient.translateWord(word, targetLang),
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
            setTranslationState(null)
        },
    })

    const handleWordClick = (word: string, rect: DOMRect) => {
        const scrollY = typeof window !== 'undefined' ? window.scrollY : 0
        setTranslationState({
            word,
            translation: null,
            phonetics: null,
            isLoading: true,
            position: { top: rect.bottom + scrollY, left: rect.left + rect.width / 2 },
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

    if (!text) {
        return (
            <div className="min-h-screen cream-bg flex items-center justify-center">
                <p className="text-gray-600 dark:text-gray-400">Načítání...</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen cream-bg pb-16">
            <div className="container mx-auto max-w-4xl p-6">
                {/* Header */}
                <div className="mb-6 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                        Odpověď Honzíka
                    </h1>
                    <Button
                        variant={translateMode ? "default" : "outline"}
                        size="sm"
                        onClick={() => setTranslateMode(!translateMode)}
                        className={`flex items-center gap-2 ${translateMode
                            ? "bg-yellow-500 hover:bg-yellow-600 text-black"
                            : ""
                            }`}
                    >
                        <Languages className="h-4 w-4" />
                        {translateMode ? "Vypnout překlad" : "Přeložit po slovech"}
                    </Button>
                </div>

                {/* Text Content */}
                <div className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-6 shadow-sm">
                    {translateMode ? (
                        <>
                            <ClickableText
                                text={text}
                                onWordClick={handleWordClick}
                                className="text-lg leading-relaxed text-gray-800 dark:text-gray-200"
                            />
                            <div className="mt-4 rounded-md bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 p-3 text-sm text-yellow-800 dark:text-yellow-200">
                                💡 Klepni na jakékoliv slovo pro zobrazení překladu
                            </div>
                        </>
                    ) : (
                        <p className="text-lg leading-relaxed text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                            {text}
                        </p>
                    )}
                </div>
            </div>

            {/* Language Selector Bar — fixed at bottom */}
            <LanguageBar
                currentLang={targetLang}
                onSelect={(code) => {
                    setTargetLang(code)
                    // Also persist to user profile and re-translate saved words
                    if (user) {
                        apiClient.patch(`/api/v1/users/${user.id}`, { native_language: code })
                            .then((updatedUser: any) => updateUser(updatedUser))
                            .catch(() => {})
                        apiClient.retranslateWords(user.telegram_id, code)
                            .catch(() => {})
                    }
                }}
                showPicker={showLangPicker}
                setShowPicker={setShowLangPicker}
            />

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

export default function ResponsePage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen cream-bg flex items-center justify-center">
                <p className="text-gray-600 dark:text-gray-400">Načítání...</p>
            </div>
        }>
            <ResponsePageContent />
        </Suspense>
    )
}

// ---------- Language Bar Component ----------

function LanguageBar({
    currentLang,
    onSelect,
    showPicker,
    setShowPicker,
}: {
    currentLang: string
    onSelect: (code: string) => void
    showPicker: boolean
    setShowPicker: (v: boolean) => void
}) {
    const current = ALL_LANGS.find((l) => l.code === currentLang)

    return (
        <>
            {/* Backdrop */}
            {showPicker && (
                <div
                    className="fixed inset-0 bg-black/30 z-40"
                    onClick={() => setShowPicker(false)}
                />
            )}

            {/* Language picker sheet */}
            {showPicker && (
                <div className="fixed bottom-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 rounded-t-2xl shadow-2xl max-h-[70vh] flex flex-col animate-slide-up">
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
                        <div className="w-10 h-1 bg-gray-300 dark:bg-gray-600 rounded-full mx-auto mb-3" />
                        <h3 className="text-center font-semibold text-gray-900 dark:text-gray-100">
                            Vyber jazyk překladu
                        </h3>
                    </div>

                    <div className="overflow-y-auto flex-1 p-3">
                        {/* Pinned */}
                        <div className="grid grid-cols-2 gap-2 mb-3">
                            {PINNED_LANGS.map((lang) => (
                                <button
                                    key={lang.code}
                                    onClick={() => {
                                        onSelect(lang.code)
                                        setShowPicker(false)
                                    }}
                                    className={`rounded-xl border-2 p-3 text-left transition-all ${
                                        currentLang === lang.code
                                            ? "border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20"
                                            : "border-gray-200 dark:border-gray-700 hover:border-yellow-400"
                                    }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">{lang.flag}</span>
                                        <span className="font-medium text-sm text-gray-900 dark:text-gray-100">{lang.name}</span>
                                    </div>
                                </button>
                            ))}
                        </div>

                        {/* Divider */}
                        <div className="flex items-center gap-3 mb-3">
                            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
                            <span className="text-xs text-gray-400">Všechny jazyky</span>
                            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
                        </div>

                        {/* Other */}
                        <div className="grid grid-cols-2 gap-2">
                            {OTHER_LANGS.map((lang) => (
                                <button
                                    key={lang.code}
                                    onClick={() => {
                                        onSelect(lang.code)
                                        setShowPicker(false)
                                    }}
                                    className={`rounded-xl border-2 p-3 text-left transition-all ${
                                        currentLang === lang.code
                                            ? "border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20"
                                            : "border-gray-200 dark:border-gray-700 hover:border-yellow-400"
                                    }`}
                                >
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">{lang.flag}</span>
                                        <span className="font-medium text-sm text-gray-900 dark:text-gray-100">{lang.name}</span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Bottom bar — always visible */}
            <div className="fixed bottom-0 left-0 right-0 z-30 safe-area-bottom">
                <button
                    onClick={() => setShowPicker(!showPicker)}
                    className="w-full bg-gray-900 dark:bg-gray-800 text-white py-3 px-4 flex items-center justify-center gap-2 text-sm font-medium hover:bg-gray-800 dark:hover:bg-gray-700 transition-colors"
                >
                    <span className="text-lg">{current?.flag || "🌐"}</span>
                    <span>{current?.name || currentLang}</span>
                    <ChevronDown className={`h-4 w-4 transition-transform ${showPicker ? "rotate-180" : ""}`} />
                </button>
            </div>
        </>
    )
}
