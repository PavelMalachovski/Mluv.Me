"use client"

import { useEffect, useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Toast, ToastContainer } from "@/components/ui/toast"
import { useToast } from "@/lib/use-toast"
import { useThemeStore } from "@/lib/theme-store"
import { IllustratedHeader } from "@/components/ui/IllustratedHeader"
import {
  Settings as SettingsIcon,
  User,
  Volume2,
  MessageSquare,
  Bell,
  LogOut,
  Check,
  Loader2,
  Moon,
  Sun,
  Globe,
  Search,
} from "lucide-react"

// ---------- Full language list ----------
// Pinned languages come first, then the rest alphabetically by Czech name

interface NativeLang {
  code: string
  flag: string
  name: string      // Czech name
  native: string    // Name in the language itself
  pinned?: boolean
}

const PINNED_LANGUAGES: NativeLang[] = [
  { code: "ru", flag: "🇷🇺", name: "Ruština",       native: "Русский",    pinned: true },
  { code: "uk", flag: "🇺🇦", name: "Ukrajinština",  native: "Українська", pinned: true },
  { code: "pl", flag: "🇵🇱", name: "Polština",      native: "Polski",     pinned: true },
  { code: "vi", flag: "🇻🇳", name: "Vietnamština",  native: "Tiếng Việt", pinned: true },
  { code: "hi", flag: "🇮🇳", name: "Hindština",     native: "हिन्दी",       pinned: true },
]

const OTHER_LANGUAGES: NativeLang[] = [
  { code: "af", flag: "🇿🇦", name: "Afrikánština",     native: "Afrikaans" },
  { code: "sq", flag: "🇦🇱", name: "Albánština",       native: "Shqip" },
  { code: "en", flag: "🇬🇧", name: "Angličtina",       native: "English" },
  { code: "ar", flag: "🇸🇦", name: "Arabština",        native: "العربية" },
  { code: "hy", flag: "🇦🇲", name: "Arménština",       native: "Հայերեն" },
  { code: "az", flag: "🇦🇿", name: "Ázerbájdžánština", native: "Azərbaycan" },
  { code: "be", flag: "🇧🇾", name: "Běloruština",      native: "Беларуская" },
  { code: "bn", flag: "🇧🇩", name: "Bengálština",      native: "বাংলা" },
  { code: "bg", flag: "🇧🇬", name: "Bulharština",      native: "Български" },
  { code: "zh", flag: "🇨🇳", name: "Čínština",         native: "中文" },
  { code: "da", flag: "🇩🇰", name: "Dánština",         native: "Dansk" },
  { code: "et", flag: "🇪🇪", name: "Estonština",       native: "Eesti" },
  { code: "fi", flag: "🇫🇮", name: "Finština",         native: "Suomi" },
  { code: "fr", flag: "🇫🇷", name: "Francouzština",    native: "Français" },
  { code: "ka", flag: "🇬🇪", name: "Gruzínština",      native: "ქართული" },
  { code: "he", flag: "🇮🇱", name: "Hebrejština",      native: "עברית" },
  { code: "nl", flag: "🇳🇱", name: "Holandština",      native: "Nederlands" },
  { code: "hr", flag: "🇭🇷", name: "Chorvatština",     native: "Hrvatski" },
  { code: "id", flag: "🇮🇩", name: "Indonéština",      native: "Bahasa Indonesia" },
  { code: "ga", flag: "🇮🇪", name: "Irština",          native: "Gaeilge" },
  { code: "it", flag: "🇮🇹", name: "Italština",        native: "Italiano" },
  { code: "ja", flag: "🇯🇵", name: "Japonština",       native: "日本語" },
  { code: "kk", flag: "🇰🇿", name: "Kazaština",        native: "Қазақша" },
  { code: "ko", flag: "🇰🇷", name: "Korejština",       native: "한국어" },
  { code: "ky", flag: "🇰🇬", name: "Kyrgyzština",      native: "Кыргызча" },
  { code: "lo", flag: "🇱🇦", name: "Laoština",         native: "ລາວ" },
  { code: "lt", flag: "🇱🇹", name: "Litevština",       native: "Lietuvių" },
  { code: "lv", flag: "🇱🇻", name: "Lotyšština",       native: "Latviešu" },
  { code: "hu", flag: "🇭🇺", name: "Maďarština",       native: "Magyar" },
  { code: "mn", flag: "🇲🇳", name: "Mongolština",      native: "Монгол" },
  { code: "my", flag: "🇲🇲", name: "Myanmarština",     native: "မြန်မာ" },
  { code: "de", flag: "🇩🇪", name: "Němčina",          native: "Deutsch" },
  { code: "no", flag: "🇳🇴", name: "Norština",         native: "Norsk" },
  { code: "pa", flag: "🇮🇳", name: "Paňdžábština",     native: "ਪੰਜਾਬੀ" },
  { code: "fa", flag: "🇮🇷", name: "Perština",         native: "فارسی" },
  { code: "pt", flag: "🇵🇹", name: "Portugalština",     native: "Português" },
  { code: "ro", flag: "🇷🇴", name: "Rumunština",       native: "Română" },
  { code: "el", flag: "🇬🇷", name: "Řečtina",          native: "Ελληνικά" },
  { code: "sk", flag: "🇸🇰", name: "Slovenčina",       native: "Slovenčina" },
  { code: "sl", flag: "🇸🇮", name: "Slovinština",      native: "Slovenščina" },
  { code: "sr", flag: "🇷🇸", name: "Srbština",         native: "Српски" },
  { code: "su", flag: "🇮🇩", name: "Sundánština",      native: "Basa Sunda" },
  { code: "sw", flag: "🇰🇪", name: "Svahilština",      native: "Kiswahili" },
  { code: "es", flag: "🇪🇸", name: "Španělština",      native: "Español" },
  { code: "sv", flag: "🇸🇪", name: "Švédština",        native: "Svenska" },
  { code: "tg", flag: "🇹🇯", name: "Tádžičtina",      native: "Тоҷикӣ" },
  { code: "tl", flag: "🇵🇭", name: "Tagalogština",     native: "Tagalog" },
  { code: "th", flag: "🇹🇭", name: "Thajština",        native: "ไทย" },
  { code: "tr", flag: "🇹🇷", name: "Turečtina",        native: "Türkçe" },
  { code: "uz", flag: "🇺🇿", name: "Uzbečtina",        native: "O'zbek" },
]

const ALL_NATIVE_LANGUAGES: NativeLang[] = [...PINNED_LANGUAGES, ...OTHER_LANGUAGES]

interface UserSettings {
  conversation_style: string
  voice_speed: string
  corrections_level: string
  notifications_enabled: boolean
}

export default function SettingsPage() {
  const router = useRouter()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const updateUser = useAuthStore((state) => state.updateUser)
  const queryClient = useQueryClient()
  const { toasts, toast, removeToast } = useToast()
  const { theme, setTheme } = useThemeStore()

  const { data: settings, isLoading } = useQuery<UserSettings>({
    queryKey: ["user-settings", user?.id],
    queryFn: () => apiClient.get(`/api/v1/users/${user?.id}/settings`),
    enabled: !!user?.id,
  })

  // Apply theme on mount and when it changes
  useEffect(() => {
    if (typeof document !== 'undefined') {
      const root = document.documentElement
      root.classList.remove('light', 'dark')
      root.classList.add(theme)
    }
  }, [theme])

  const updateSettingsMutation = useMutation({
    mutationFn: (newSettings: Partial<UserSettings>) =>
      apiClient.patch(`/api/v1/users/${user?.id}/settings`, newSettings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-settings", user?.id] })
      toast({
        title: "Nastavení uloženo",
        description: "Tvé preference byly úspěšně uloženy.",
        variant: "success",
      })
    },
    onError: (error: any) => {
      console.error("Settings update error:", error)
      toast({
        title: "Chyba",
        description: error?.response?.data?.detail || "Nepodařilo se uložit nastavení. Zkus to znovu.",
        variant: "error",
      })
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: (data: { level?: string; native_language?: string }) =>
      apiClient.patch(`/api/v1/users/${user?.id}`, data),
    onSuccess: (updatedUser) => {
      queryClient.invalidateQueries({ queryKey: ["user-stats"] })
      updateUser(updatedUser)
      toast({
        title: "Profil upraven",
        description: "Tvůj profil byl upraven.",
        variant: "success",
      })
    },
    onError: (error: any) => {
      console.error("Profile update error:", error)
      toast({
        title: "Chyba",
        description: error?.response?.data?.detail || "Nepodařilo se upravit profil. Zkus to znovu.",
        variant: "error",
      })
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

  const handleLogout = () => {
    logout()
    router.push("/login")
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center cream-bg">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <>
      <ToastContainer>
        {toasts.map((t) => (
          <Toast key={t.id} {...t} onClose={() => removeToast(t.id)} />
        ))}
      </ToastContainer>

      <div className="min-h-screen cream-bg landscape-bg pb-20">
        {/* Purple Header */}
        <div className="illustrated-header">
          <h1 className="illustrated-header-title">Nastavení</h1>
        </div>

        <div className="mx-auto max-w-2xl px-4 pt-6">
          <Tabs defaultValue="learning" className="space-y-6">
            <TabsList className="w-full grid grid-cols-4 bg-white dark:bg-gray-800 rounded-xl p-1 shadow-sm">
              <TabsTrigger value="learning" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Učení
              </TabsTrigger>
              <TabsTrigger value="voice" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Hlas
              </TabsTrigger>
              <TabsTrigger value="appearance" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Vzhled
              </TabsTrigger>
              <TabsTrigger value="account" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Účet
              </TabsTrigger>
            </TabsList>

            {/* Learning Settings */}
            <TabsContent value="learning" className="space-y-4">
              {/* Czech Level */}
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <span className="text-xl">🇨🇿</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Úroveň češtiny</h3>
                    <p className="text-sm text-muted-foreground">Tvá aktuální úroveň</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { value: "beginner", label: "Začátečník", emoji: "🌱", description: "Základní fráze a slovíčka" },
                    { value: "intermediate", label: "Středně pokročilý", emoji: "📚", description: "Běžná konverzace" },
                    { value: "advanced", label: "Pokročilý", emoji: "🎯", description: "Složitější témata" },
                    { value: "native", label: "Rodilý", emoji: "⭐", description: "Plynulá čeština" },
                  ].map((level) => (
                    <button
                      key={level.value}
                      onClick={() => updateProfileMutation.mutate({ level: level.value })}
                      disabled={updateProfileMutation.isPending}
                      className={`w-full rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${user.level === level.value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                        }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{level.emoji}</span>
                          <div>
                            <div className="font-medium text-foreground">{level.label}</div>
                            <div className="text-sm text-muted-foreground">{level.description}</div>
                          </div>
                        </div>
                        {user.level === level.value && (
                          <Check className="h-5 w-5 text-primary" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Correction Level */}
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <SettingsIcon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Úroveň oprav</h3>
                    <p className="text-sm text-muted-foreground">Kolik zpětné vazby chceš</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { value: "minimal", label: "Minimální", description: "Pouze kritické chyby" },
                    { value: "balanced", label: "Vyvážený", description: "Důležité chyby s vysvětlením" },
                    { value: "detailed", label: "Detailní", description: "Všechny chyby opravené" },
                  ].map((level) => (
                    <button
                      key={level.value}
                      onClick={() => updateSettingsMutation.mutate({ corrections_level: level.value })}
                      disabled={updateSettingsMutation.isPending}
                      className={`w-full rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${settings?.corrections_level === level.value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                        }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-foreground">{level.label}</div>
                          <div className="text-sm text-muted-foreground">{level.description}</div>
                        </div>
                        {settings?.corrections_level === level.value && (
                          <Check className="h-5 w-5 text-primary" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Conversation Style */}
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
                    <MessageSquare className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Styl konverzace</h3>
                    <p className="text-sm text-muted-foreground">Osobnost Honzíka</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { value: "friendly", label: "Přátelský", emoji: "😊", description: "Přátelský a podporující" },
                    { value: "tutor", label: "Učitel", emoji: "👨‍🏫", description: "Více oprav a tipů" },
                    { value: "casual", label: "Kamarád", emoji: "🍺", description: "Jako s kamarádem" },
                  ].map((style) => (
                    <button
                      key={style.value}
                      onClick={() => updateSettingsMutation.mutate({ conversation_style: style.value })}
                      disabled={updateSettingsMutation.isPending}
                      className={`w-full rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${settings?.conversation_style === style.value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                        }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{style.emoji}</span>
                          <div>
                            <div className="font-medium text-foreground">{style.label}</div>
                            <div className="text-sm text-muted-foreground">{style.description}</div>
                          </div>
                        </div>
                        {settings?.conversation_style === style.value && (
                          <Check className="h-5 w-5 text-primary" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </TabsContent>

            {/* Voice Settings */}
            <TabsContent value="voice" className="space-y-4">
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/30">
                    <Volume2 className="h-5 w-5 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Rychlost hlasu</h3>
                    <p className="text-sm text-muted-foreground">Rychlost řeči Honzíka</p>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {[
                    { value: "very_slow", label: "Velmi pomalu", sublabel: "0.7×" },
                    { value: "slow", label: "Pomalu", sublabel: "0.85×" },
                    { value: "normal", label: "Normálně", sublabel: "1×" },
                    { value: "native", label: "Rodilý", sublabel: "1.2×" },
                  ].map((speed) => (
                    <button
                      key={speed.value}
                      onClick={() => updateSettingsMutation.mutate({ voice_speed: speed.value })}
                      disabled={updateSettingsMutation.isPending}
                      className={`rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${settings?.voice_speed === speed.value
                        ? "border-primary bg-primary/10"
                        : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                        }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-foreground">{speed.label}</div>
                          <div className="text-sm text-muted-foreground">{speed.sublabel}</div>
                        </div>
                        {settings?.voice_speed === speed.value && (
                          <Check className="h-5 w-5 text-primary" />
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30">
                    <Bell className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Upozornění</h3>
                    <p className="text-sm text-muted-foreground">Denní připomínky procvičování</p>
                  </div>
                </div>

                <button
                  onClick={() =>
                    updateSettingsMutation.mutate({
                      notifications_enabled: !settings?.notifications_enabled,
                    })
                  }
                  disabled={updateSettingsMutation.isPending}
                  className={`w-full rounded-xl border-2 p-4 transition-all disabled:opacity-50 ${settings?.notifications_enabled
                    ? "border-primary bg-primary/10"
                    : "border-border bg-white dark:bg-gray-800"
                    }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="text-left">
                      <div className="font-medium text-foreground">
                        {settings?.notifications_enabled ? "Zapnuto" : "Vypnuto"}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Dostávej denní připomínky procvičovat češtinu
                      </div>
                    </div>
                    {settings?.notifications_enabled && (
                      <Check className="h-5 w-5 text-primary" />
                    )}
                  </div>
                </button>
              </div>
            </TabsContent>

            {/* Appearance Settings */}
            <TabsContent value="appearance" className="space-y-4">
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/30">
                    {theme === "light" ? (
                      <Sun className="h-5 w-5 text-indigo-600" />
                    ) : (
                      <Moon className="h-5 w-5 text-indigo-600" />
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Téma</h3>
                    <p className="text-sm text-muted-foreground">Vyber si preferované barevné schéma</p>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <button
                    onClick={() => setTheme("light")}
                    className={`rounded-xl border-2 p-4 text-left transition-all ${theme === "light"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Sun className="h-5 w-5 text-yellow-600" />
                        <div>
                          <div className="font-medium text-foreground">Světlé</div>
                          <div className="text-sm text-muted-foreground">Světlé téma</div>
                        </div>
                      </div>
                      {theme === "light" && <Check className="h-5 w-5 text-primary" />}
                    </div>
                  </button>

                  <button
                    onClick={() => setTheme("dark")}
                    className={`rounded-xl border-2 p-4 text-left transition-all ${theme === "dark"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Moon className="h-5 w-5 text-indigo-600" />
                        <div>
                          <div className="font-medium text-foreground">Tmavé</div>
                          <div className="text-sm text-muted-foreground">Tmavé téma</div>
                        </div>
                      </div>
                      {theme === "dark" && <Check className="h-5 w-5 text-primary" />}
                    </div>
                  </button>
                </div>
              </div>

              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30">
                    <Globe className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Rodný jazyk</h3>
                    <p className="text-sm text-muted-foreground">Pro vysvětlení chyb</p>
                  </div>
                </div>

                <NativeLanguagePicker
                  currentLanguage={user?.native_language || "ru"}
                  onSelect={(code) => {
                    updateProfileMutation.mutate({ native_language: code })
                    // Re-translate all saved words to the new language
                    if (user?.telegram_id) {
                      apiClient.retranslateWords(user.telegram_id, code)
                        .then(() => {
                          queryClient.invalidateQueries({ queryKey: ["saved-words"] })
                        })
                        .catch((err) => console.error("Retranslate error:", err))
                    }
                  }}
                  disabled={updateProfileMutation.isPending}
                />
              </div>
            </TabsContent>

            {/* Account Settings */}
            <TabsContent value="account" className="space-y-4">
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
                    <User className="h-5 w-5 text-gray-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Informace o účtu</h3>
                    <p className="text-sm text-muted-foreground">Tvoje údaje profilu</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Jméno
                    </label>
                    <input
                      type="text"
                      value={`${user.first_name} ${user.last_name || ""}`}
                      disabled
                      className="w-full rounded-xl border border-border bg-cream-alt px-4 py-2 text-sm text-foreground"
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Uživatelské jméno
                    </label>
                    <input
                      type="text"
                      value={user.username || "N/A"}
                      disabled
                      className="w-full rounded-xl border border-border bg-cream-alt px-4 py-2 text-sm text-foreground"
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Telegram ID
                    </label>
                    <input
                      type="text"
                      value={user.telegram_id}
                      disabled
                      className="w-full rounded-xl border border-border bg-cream-alt px-4 py-2 text-sm text-foreground"
                    />
                  </div>

                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Rodný jazyk
                    </label>
                    <input
                      type="text"
                      value={ALL_NATIVE_LANGUAGES.find(l => l.code === user.native_language)?.name || user.native_language}
                      disabled
                      className="w-full rounded-xl border border-border bg-cream-alt px-4 py-2 text-sm text-foreground"
                    />
                  </div>
                </div>
              </div>

              <div className="illustrated-card border-2 border-red-200 dark:border-red-800 p-6">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 dark:bg-red-900/30">
                    <LogOut className="h-5 w-5 text-red-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Nebezpečná zóna</h3>
                    <p className="text-sm text-muted-foreground">Nevratné akce</p>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="w-full rounded-xl border-2 border-red-300 dark:border-red-700 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 py-3 font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Odhlásit se
                </button>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </>
  )
}

// ---------- Native Language Picker Component ----------

function NativeLanguagePicker({
  currentLanguage,
  onSelect,
  disabled,
}: {
  currentLanguage: string
  onSelect: (code: string) => void
  disabled: boolean
}) {
  const [search, setSearch] = useState("")
  const [showAll, setShowAll] = useState(false)

  const lowerSearch = search.toLowerCase()

  const filteredPinned = PINNED_LANGUAGES.filter(
    (l) =>
      !search ||
      l.name.toLowerCase().includes(lowerSearch) ||
      l.native.toLowerCase().includes(lowerSearch) ||
      l.code.toLowerCase().includes(lowerSearch)
  )

  const filteredOther = OTHER_LANGUAGES.filter(
    (l) =>
      !search ||
      l.name.toLowerCase().includes(lowerSearch) ||
      l.native.toLowerCase().includes(lowerSearch) ||
      l.code.toLowerCase().includes(lowerSearch)
  )

  // Current language info for collapsed view
  const currentLang = ALL_NATIVE_LANGUAGES.find((l) => l.code === currentLanguage)

  return (
    <div className="space-y-3">
      {/* Current selection / toggle button */}
      <button
        onClick={() => setShowAll(!showAll)}
        className="w-full rounded-xl border-2 border-primary bg-primary/10 p-4 text-left transition-all"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{currentLang?.flag || "🌐"}</span>
            <div>
              <div className="font-medium text-foreground">{currentLang?.name || currentLanguage}</div>
              <div className="text-sm text-muted-foreground">{currentLang?.native}</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Check className="h-5 w-5 text-primary" />
            <span className="text-xs text-muted-foreground">{showAll ? "▲" : "▼"}</span>
          </div>
        </div>
      </button>

      {showAll && (
        <>
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Hledat jazyk..."
              className="w-full rounded-xl border border-border bg-white dark:bg-gray-800 pl-10 pr-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          {/* Pinned languages */}
          {filteredPinned.length > 0 && (
            <div className="grid grid-cols-2 gap-2">
              {filteredPinned.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    onSelect(lang.code)
                    setShowAll(false)
                    setSearch("")
                  }}
                  disabled={disabled}
                  className={`rounded-xl border-2 p-3 text-left transition-all disabled:opacity-50 ${
                    currentLanguage === lang.code
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{lang.flag}</span>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-sm text-foreground truncate">{lang.name}</div>
                      <div className="text-xs text-muted-foreground truncate">{lang.native}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Divider */}
          {filteredPinned.length > 0 && filteredOther.length > 0 && (
            <div className="flex items-center gap-3">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-muted-foreground">Všechny jazyky</span>
              <div className="flex-1 h-px bg-border" />
            </div>
          )}

          {/* All other languages */}
          {filteredOther.length > 0 && (
            <div className="grid grid-cols-2 gap-2 max-h-[320px] overflow-y-auto pr-1">
              {filteredOther.map((lang) => (
                <button
                  key={lang.code}
                  onClick={() => {
                    onSelect(lang.code)
                    setShowAll(false)
                    setSearch("")
                  }}
                  disabled={disabled}
                  className={`rounded-xl border-2 p-3 text-left transition-all disabled:opacity-50 ${
                    currentLanguage === lang.code
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{lang.flag}</span>
                    <div className="min-w-0 flex-1">
                      <div className="font-medium text-sm text-foreground truncate">{lang.name}</div>
                      <div className="text-xs text-muted-foreground truncate">{lang.native}</div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}

          {filteredPinned.length === 0 && filteredOther.length === 0 && (
            <p className="text-center text-sm text-muted-foreground py-4">
              Jazyk nenalezen
            </p>
          )}
        </>
      )}
    </div>
  )
}
