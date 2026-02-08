"use client"

import { useEffect } from "react"
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
} from "lucide-react"

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

                <div className="grid gap-3 sm:grid-cols-2">
                  <button
                    onClick={() => updateProfileMutation.mutate({ native_language: "ru" })}
                    disabled={updateProfileMutation.isPending}
                    className={`rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${user?.native_language === "ru"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">🇷🇺</span>
                        <div>
                          <div className="font-medium text-foreground">Ruština</div>
                          <div className="text-sm text-muted-foreground">Русский</div>
                        </div>
                      </div>
                      {user?.native_language === "ru" && <Check className="h-5 w-5 text-primary" />}
                    </div>
                  </button>

                  <button
                    onClick={() => updateProfileMutation.mutate({ native_language: "uk" })}
                    disabled={updateProfileMutation.isPending}
                    className={`rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${user?.native_language === "uk"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">🇺🇦</span>
                        <div>
                          <div className="font-medium text-foreground">Ukrajinština</div>
                          <div className="text-sm text-muted-foreground">Українська</div>
                        </div>
                      </div>
                      {user?.native_language === "uk" && <Check className="h-5 w-5 text-primary" />}
                    </div>
                  </button>
                </div>
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
                      value={user.native_language === "ru" ? "Ruština" : "Ukrajinština"}
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
