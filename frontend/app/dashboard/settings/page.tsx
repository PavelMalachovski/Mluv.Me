"use client"

import { useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import Image from "next/image"
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
        title: "Settings updated",
        description: "Your preferences have been saved successfully.",
        variant: "success",
      })
    },
    onError: (error: any) => {
      console.error("Settings update error:", error)
      toast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to update settings. Please try again.",
        variant: "error",
      })
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: (data: { level?: string; ui_language?: string }) =>
      apiClient.patch(`/api/v1/users/${user?.id}`, data),
    onSuccess: (updatedUser) => {
      queryClient.invalidateQueries({ queryKey: ["user-stats"] })
      updateUser(updatedUser)
      toast({
        title: "Profile updated",
        description: "Your profile has been updated.",
        variant: "success",
      })
    },
    onError: (error: any) => {
      console.error("Profile update error:", error)
      toast({
        title: "Error",
        description: error?.response?.data?.detail || "Failed to update profile. Please try again.",
        variant: "error",
      })
    },
  })

  if (!user) {
    router.push("/login")
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
        {/* Purple Header with Mascot */}
        <div className="illustrated-header relative pb-16">
          <h1 className="illustrated-header-title">Settings</h1>
          <div className="absolute -bottom-12 left-1/2 -translate-x-1/2">
            <Image
              src="/images/mascot/honzik-waving.png"
              alt="Honzík"
              width={80}
              height={80}
              className="drop-shadow-lg"
            />
          </div>
        </div>

        <div className="mx-auto max-w-2xl px-4 pt-16">
          <Tabs defaultValue="learning" className="space-y-6">
            <TabsList className="w-full grid grid-cols-4 bg-white dark:bg-gray-800 rounded-xl p-1 shadow-sm">
              <TabsTrigger value="learning" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Learning
              </TabsTrigger>
              <TabsTrigger value="voice" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Voice
              </TabsTrigger>
              <TabsTrigger value="appearance" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Appearance
              </TabsTrigger>
              <TabsTrigger value="account" className="rounded-lg data-[state=active]:bg-primary data-[state=active]:text-white">
                Account
              </TabsTrigger>
            </TabsList>

            {/* Learning Settings */}
            <TabsContent value="learning" className="space-y-4">
              {/* Czech Level */}
              <div className="illustrated-card p-6">
                <div className="mb-6 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10">
                    <span className="text-xl">💬</span>
                  </div>
                  <div>
                    <h3 className="font-semibold text-foreground">Czech Level</h3>
                    <p className="text-sm text-muted-foreground">Your current proficiency</p>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {[
                    { value: "beginner", label: "Začátečník", image: "/images/mascot/honzik-waving.png" },
                    { value: "intermediate", label: "Středně pokročilý", image: "/images/mascot/honzik-running.png" },
                    { value: "advanced", label: "Pokročilý", image: "/images/mascot/honzik-reading.png" },
                    { value: "native", label: "Rodilý", image: "/images/mascot/honzik-stars.png" },
                  ].map((level) => (
                    <button
                      key={level.value}
                      onClick={() => updateProfileMutation.mutate({ level: level.value })}
                      disabled={updateProfileMutation.isPending}
                      className={`level-card ${user.level === level.value ? "active" : ""}`}
                    >
                      <Image
                        src={level.image}
                        alt={level.label}
                        width={80}
                        height={80}
                        className="mx-auto mb-2"
                      />
                      <span className="level-name">{level.label}</span>
                      {updateProfileMutation.isPending && user.level !== level.value ? null : (
                        user.level === level.value && (
                          <Check className="h-5 w-5 text-primary mx-auto mt-1" />
                        )
                      )}
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
                    <h3 className="font-semibold text-foreground">Correction Level</h3>
                    <p className="text-sm text-muted-foreground">How much feedback you want</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { value: "minimal", label: "Minimální", description: "Only critical mistakes" },
                    { value: "balanced", label: "Vyvážený", description: "Important mistakes with explanations" },
                    { value: "detailed", label: "Detailní", description: "All mistakes corrected" },
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
                    <h3 className="font-semibold text-foreground">Conversation Style</h3>
                    <p className="text-sm text-muted-foreground">Honzík&apos;s personality</p>
                  </div>
                </div>

                <div className="space-y-3">
                  {[
                    { value: "friendly", label: "Přátelský", emoji: "😊", description: "Casual and supportive" },
                    { value: "tutor", label: "Učitel", emoji: "👨‍🏫", description: "More corrections and tips" },
                    { value: "casual", label: "Kamarád", emoji: "🍺", description: "Like chatting with a friend" },
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
                    <h3 className="font-semibold text-foreground">Voice Speed</h3>
                    <p className="text-sm text-muted-foreground">Honzík&apos;s speaking speed</p>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {[
                    { value: "very_slow", label: "Velmi pomalu", sublabel: "Very Slow" },
                    { value: "slow", label: "Pomalu", sublabel: "Slow" },
                    { value: "normal", label: "Normálně", sublabel: "Normal" },
                    { value: "native", label: "Rodilý", sublabel: "Native Speed" },
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
                    <h3 className="font-semibold text-foreground">Notifications</h3>
                    <p className="text-sm text-muted-foreground">Daily practice reminders</p>
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
                        {settings?.notifications_enabled ? "Enabled" : "Disabled"}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Get daily reminders to practice Czech
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
                    <h3 className="font-semibold text-foreground">Тема / Theme</h3>
                    <p className="text-sm text-muted-foreground">Choose your preferred color scheme</p>
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
                          <div className="font-medium text-foreground">Светлая</div>
                          <div className="text-sm text-muted-foreground">Bright theme</div>
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
                          <div className="font-medium text-foreground">Тёмная</div>
                          <div className="text-sm text-muted-foreground">Dark theme</div>
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
                    <h3 className="font-semibold text-foreground">Язык интерфейса / Interface Language</h3>
                    <p className="text-sm text-muted-foreground">Choose your interface language</p>
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  <button
                    onClick={() => updateProfileMutation.mutate({ ui_language: "ru" })}
                    disabled={updateProfileMutation.isPending}
                    className={`rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${user?.ui_language === "ru"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">🇷🇺</span>
                        <div>
                          <div className="font-medium text-foreground">Русский</div>
                          <div className="text-sm text-muted-foreground">Russian</div>
                        </div>
                      </div>
                      {user?.ui_language === "ru" && <Check className="h-5 w-5 text-primary" />}
                    </div>
                  </button>

                  <button
                    onClick={() => updateProfileMutation.mutate({ ui_language: "uk" })}
                    disabled={updateProfileMutation.isPending}
                    className={`rounded-xl border-2 p-4 text-left transition-all disabled:opacity-50 ${user?.ui_language === "uk"
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/50 bg-white dark:bg-gray-800"
                      }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">🇺🇦</span>
                        <div>
                          <div className="font-medium text-foreground">Українська</div>
                          <div className="text-sm text-muted-foreground">Ukrainian</div>
                        </div>
                      </div>
                      {user?.ui_language === "uk" && <Check className="h-5 w-5 text-primary" />}
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
                    <h3 className="font-semibold text-foreground">Account Information</h3>
                    <p className="text-sm text-muted-foreground">Your profile details</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="mb-1 block text-sm font-medium text-muted-foreground">
                      Name
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
                      Username
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
                      Interface Language
                    </label>
                    <input
                      type="text"
                      value={user.ui_language === "ru" ? "Русский" : "Українська"}
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
                    <h3 className="font-semibold text-foreground">Danger Zone</h3>
                    <p className="text-sm text-muted-foreground">Irreversible actions</p>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="w-full rounded-xl border-2 border-red-300 dark:border-red-700 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 py-3 font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Log Out
                </button>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </>
  )
}
