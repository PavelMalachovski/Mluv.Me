"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import {
  isTelegramWebApp,
  getTelegramUser,
  authenticateWebApp,
  initTelegramWebApp
} from "@/lib/telegram-web-app"
import { loginWithTelegram, authenticateWithBackend } from "@/lib/telegram-auth"
import { useAuthStore } from "@/lib/auth-store"

export default function LoginPage() {
  const router = useRouter()
  const setUser = useAuthStore((state) => state.setUser)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isWebApp, setIsWebApp] = useState(false)

  useEffect(() => {
    // Check if running in Telegram Web App
    if (isTelegramWebApp()) {
      setIsWebApp(true)
      setIsLoading(false)  // Don't auto-login, let user click button
    } else {
      setIsWebApp(false)
      setIsLoading(false)
      // Load Telegram Login Widget script for browser
      const script = document.createElement("script")
      script.src = "https://telegram.org/js/telegram-widget.js?22"
      script.async = true
      document.body.appendChild(script)

      return () => {
        document.body.removeChild(script)
      }
    }
  }, [])

  const handleWebAppLogin = async () => {
    setIsLoading(true)
    setError(null)

    try {
      console.log("Starting Web App authentication...")

      // Initialize Telegram Web App
      const webApp = initTelegramWebApp()

      if (!webApp) {
        throw new Error("Failed to initialize Telegram Web App")
      }

      console.log("Web App initialized:", {
        platform: webApp.platform,
        version: webApp.version
      })

      const user = getTelegramUser()

      if (!user) {
        throw new Error("No user data from Telegram. Please restart the bot.")
      }

      console.log("Telegram user:", user.id, user.first_name)

      // Authenticate with backend
      console.log("Authenticating with backend...")
      const result = await authenticateWebApp()

      console.log("Auth result:", result)

      if (!result.success) {
        throw new Error(result.error || "Authentication failed")
      }

      // Store user data and token
      setUser(result.user)
      if (result.token) {
        useAuthStore.getState().setToken(result.token)
      }

      console.log("User authenticated, redirecting to dashboard...")

      // Redirect to dashboard
      router.push("/dashboard")
    } catch (err) {
      console.error("Web App login failed:", err)
      setError(
        err instanceof Error ? err.message : "Login failed. Please try again."
      )
      setIsLoading(false)
    }
  }

  const handleLogin = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Step 1: Get Telegram auth data
      const telegramUser = await loginWithTelegram()

      // Step 2: Authenticate with backend
      const data = await authenticateWithBackend(telegramUser)

      // Step 3: Store user data and token
      setUser(data.user)
      if (data.access_token) {
        useAuthStore.getState().setToken(data.access_token)
      }

      // Step 4: Redirect to dashboard
      router.push("/dashboard")
    } catch (err) {
      console.error("Login failed:", err)
      setError(
        err instanceof Error ? err.message : "Login failed. Please try again."
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden" style={{ backgroundColor: '#90D0EB' }}>
      {/* Soft gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/5" />

      <div className="relative z-10 w-full max-w-md space-y-6 px-4">
        {/* Character illustration area */}
        <div className="relative mx-auto mb-2 flex flex-col items-center justify-center">
          {/* Speech bubble */}
          <div className="mb-4 rounded-2xl bg-white px-6 py-3 shadow-lg">
            <p className="text-center text-2xl font-bold text-gray-800">
              Ahoj 👋
            </p>
          </div>

          {/* Characters image */}
          <div className="relative w-64 h-52">
            <Image
              src="/images/mascot/characters-login.png"
              alt="Honzík & Nováková"
              fill
              className="object-contain"
              priority
            />
          </div>
        </div>

        {/* Main content card */}
        <div className="relative rounded-3xl bg-white p-8 shadow-2xl">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-[#7d3bed] drop-shadow-sm">
              Mluv.Me
            </h1>
            <p className="mt-3 text-lg font-medium text-gray-700">
              Learn Languages with AI-powered conversations
            </p>
            <div className="mt-2 text-sm text-gray-500">
              Practice speaking with Honzík & Nováková 🇨🇿
            </div>
          </div>

          {error && (
            <div className="mt-6 rounded-xl border-2 border-red-300 bg-red-50 p-4 shadow-md">
              <p className="text-sm font-medium text-red-800">{error}</p>
            </div>
          )}

          {isWebApp ? (
            // Telegram Web App - show button
            <div className="mt-6 space-y-4">
              <button
                onClick={handleWebAppLogin}
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-[#7d3bed] px-6 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:bg-[#6b32cc] hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 active:scale-95"
              >
                {isLoading ? (
                  <>
                    <div className="h-6 w-6 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <svg
                      className="h-6 w-6"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18.717-.962 3.778-1.36 5.016-.168.525-.5 1.15-.877 1.15-.286 0-.637-.124-.907-.291-.502-.31-1.555-.9-2.114-1.243-.142-.087-.142-.28 0-.366.56-.343 2.228-1.928 2.63-2.285.099-.088.049-.145-.062-.086-.75.395-3.26 2.154-3.59 2.388-.1.071-.197.12-.508.037-.502-.133-1.064-.266-1.559-.396-.495-.131-.637-.4-.013-.595 2.873-.894 6.36-1.846 6.968-2.086.558-.22.99-.22 1.134.195z" />
                    </svg>
                    <span>Continue with Telegram</span>
                  </>
                )}
              </button>

              <div className="text-center text-sm font-medium text-gray-500">
                One tap to start learning! 🎉
              </div>
            </div>
          ) : (
            // Browser - show login button
            <div className="mt-6 space-y-4">
              <button
                onClick={handleLogin}
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-[#7d3bed] px-6 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:bg-[#6b32cc] hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 active:scale-95"
              >
                {isLoading ? (
                  <>
                    <div className="h-6 w-6 animate-spin rounded-full border-2 border-white border-t-transparent" />
                    <span>Authenticating...</span>
                  </>
                ) : (
                  <>
                    <svg
                      className="h-6 w-6"
                      viewBox="0 0 24 24"
                      fill="currentColor"
                    >
                      <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18.717-.962 3.778-1.36 5.016-.168.525-.5 1.15-.877 1.15-.286 0-.637-.124-.907-.291-.502-.31-1.555-.9-2.114-1.243-.142-.087-.142-.28 0-.366.56-.343 2.228-1.928 2.63-2.285.099-.088.049-.145-.062-.086-.75.395-3.26 2.154-3.59 2.388-.1.071-.197.12-.508.037-.502-.133-1.064-.266-1.559-.396-.495-.131-.637-.4-.013-.595 2.873-.894 6.36-1.846 6.968-2.086.558-.22.99-.22 1.134.195z" />
                    </svg>
                    <span>Login with Telegram</span>
                  </>
                )}
              </button>

              <div className="text-center text-sm font-medium text-gray-500">
                By logging in, you agree to practice and have fun! 🎉
              </div>
            </div>
          )}

          {/* Features section - redesigned */}
          <div className="mt-8 space-y-3 rounded-2xl bg-[#f5f0ff] p-6">
            <h3 className="text-center text-xl font-bold text-[#7d3bed]">
              Why Mluv.Me?
            </h3>
            <ul className="space-y-2 text-sm text-gray-700">
              <li className="flex items-center gap-2">
                <span className="text-lg">📚</span>
                <span>Practice with AI-powered Characters</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-lg">✨</span>
                <span>Get instant feedback on your language</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-lg">⭐</span>
                <span>Track your progress and earn stars</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-lg">🚀</span>
                <span>Learn at your own pace</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
