"use client"

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useRouter } from "next/navigation"
import { useAuthStore } from "@/lib/auth-store"
import { apiClient } from "@/lib/api-client"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Settings as SettingsIcon,
  User,
  Volume2,
  MessageSquare,
  Bell,
  LogOut,
  Check,
} from "lucide-react"
import { useState } from "react"

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
  const queryClient = useQueryClient()

  const { data: settings, isLoading } = useQuery<UserSettings>({
    queryKey: ["user-settings"],
    queryFn: () => apiClient.get("/api/v1/users/me/settings"),
    enabled: !!user,
  })

  const updateSettingsMutation = useMutation({
    mutationFn: (newSettings: Partial<UserSettings>) =>
      apiClient.patch("/api/v1/users/me/settings", newSettings),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-settings"] })
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: (data: { level: string }) =>
      apiClient.patch("/api/v1/users/me", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-stats"] })
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

  return (
    <div className="mx-auto max-w-2xl p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-sm text-gray-500">Customize your learning experience</p>
      </div>

      <Tabs defaultValue="learning" className="space-y-6">
        <TabsList className="w-full">
          <TabsTrigger value="learning" className="flex-1">
            Learning
          </TabsTrigger>
          <TabsTrigger value="voice" className="flex-1">
            Voice
          </TabsTrigger>
          <TabsTrigger value="account" className="flex-1">
            Account
          </TabsTrigger>
        </TabsList>

        {/* Learning Settings */}
        <TabsContent value="learning" className="space-y-4">
          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                <MessageSquare className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Czech Level</h3>
                <p className="text-sm text-gray-500">Your current proficiency</p>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {[
                { value: "beginner", label: "Začátečník", sublabel: "Beginner" },
                { value: "intermediate", label: "Středně pokročilý", sublabel: "Intermediate" },
                { value: "advanced", label: "Pokročilý", sublabel: "Advanced" },
                { value: "native", label: "Rodilý", sublabel: "Native" },
              ].map((level) => (
                <button
                  key={level.value}
                  onClick={() => updateProfileMutation.mutate({ level: level.value })}
                  className={`rounded-lg border-2 p-4 text-left transition-all ${
                    user.level === level.value
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-blue-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{level.label}</div>
                      <div className="text-sm text-gray-500">{level.sublabel}</div>
                    </div>
                    {user.level === level.value && (
                      <Check className="h-5 w-5 text-blue-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100">
                <SettingsIcon className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Correction Level</h3>
                <p className="text-sm text-gray-500">How much feedback you want</p>
              </div>
            </div>

            <div className="space-y-3">
              {[
                { value: "minimal", label: "Minimální", description: "Only critical mistakes" },
                {
                  value: "balanced",
                  label: "Vyvážený",
                  description: "Important mistakes with explanations",
                },
                { value: "detailed", label: "Detailní", description: "All mistakes corrected" },
              ].map((level) => (
                <button
                  key={level.value}
                  onClick={() =>
                    updateSettingsMutation.mutate({ corrections_level: level.value })
                  }
                  className={`w-full rounded-lg border-2 p-4 text-left transition-all ${
                    settings?.corrections_level === level.value
                      ? "border-purple-500 bg-purple-50"
                      : "border-gray-200 hover:border-purple-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{level.label}</div>
                      <div className="text-sm text-gray-500">{level.description}</div>
                    </div>
                    {settings?.corrections_level === level.value && (
                      <Check className="h-5 w-5 text-purple-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100">
                <MessageSquare className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Conversation Style</h3>
                <p className="text-sm text-gray-500">Honzík&apos;s personality</p>
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
                  onClick={() =>
                    updateSettingsMutation.mutate({ conversation_style: style.value })
                  }
                  className={`w-full rounded-lg border-2 p-4 text-left transition-all ${
                    settings?.conversation_style === style.value
                      ? "border-green-500 bg-green-50"
                      : "border-gray-200 hover:border-green-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{style.emoji}</span>
                      <div>
                        <div className="font-medium text-gray-900">{style.label}</div>
                        <div className="text-sm text-gray-500">{style.description}</div>
                      </div>
                    </div>
                    {settings?.conversation_style === style.value && (
                      <Check className="h-5 w-5 text-green-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </Card>
        </TabsContent>

        {/* Voice Settings */}
        <TabsContent value="voice" className="space-y-4">
          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-100">
                <Volume2 className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Voice Speed</h3>
                <p className="text-sm text-gray-500">Honzík&apos;s speaking speed</p>
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
                  className={`rounded-lg border-2 p-4 text-left transition-all ${
                    settings?.voice_speed === speed.value
                      ? "border-orange-500 bg-orange-50"
                      : "border-gray-200 hover:border-orange-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{speed.label}</div>
                      <div className="text-sm text-gray-500">{speed.sublabel}</div>
                    </div>
                    {settings?.voice_speed === speed.value && (
                      <Check className="h-5 w-5 text-orange-600" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100">
                <Bell className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Notifications</h3>
                <p className="text-sm text-gray-500">Daily practice reminders</p>
              </div>
            </div>

            <button
              onClick={() =>
                updateSettingsMutation.mutate({
                  notifications_enabled: !settings?.notifications_enabled,
                })
              }
              className={`w-full rounded-lg border-2 p-4 transition-all ${
                settings?.notifications_enabled
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="text-left">
                  <div className="font-medium text-gray-900">
                    {settings?.notifications_enabled ? "Enabled" : "Disabled"}
                  </div>
                  <div className="text-sm text-gray-500">
                    Get daily reminders to practice Czech
                  </div>
                </div>
                {settings?.notifications_enabled && (
                  <Check className="h-5 w-5 text-blue-600" />
                )}
              </div>
            </button>
          </Card>
        </TabsContent>

        {/* Account Settings */}
        <TabsContent value="account" className="space-y-4">
          <Card className="p-6">
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100">
                <User className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Account Information</h3>
                <p className="text-sm text-gray-500">Your profile details</p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Name
                </label>
                <input
                  type="text"
                  value={`${user.first_name} ${user.last_name || ""}`}
                  disabled
                  className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 text-sm"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Username
                </label>
                <input
                  type="text"
                  value={user.username || "N/A"}
                  disabled
                  className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 text-sm"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Telegram ID
                </label>
                <input
                  type="text"
                  value={user.telegram_id}
                  disabled
                  className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 text-sm"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Interface Language
                </label>
                <input
                  type="text"
                  value={user.ui_language === "ru" ? "Русский" : "Українська"}
                  disabled
                  className="w-full rounded-lg border border-gray-300 bg-gray-50 px-4 py-2 text-sm"
                />
              </div>
            </div>
          </Card>

          <Card className="border-red-200 p-6">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100">
                <LogOut className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Danger Zone</h3>
                <p className="text-sm text-gray-500">Irreversible actions</p>
              </div>
            </div>

            <div className="space-y-3">
              <Button
                variant="outline"
                className="w-full border-red-300 text-red-600 hover:bg-red-50"
                onClick={handleLogout}
              >
                <LogOut className="mr-2 h-4 w-4" />
                Log Out
              </Button>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
