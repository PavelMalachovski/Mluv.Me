"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
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

      // Store user data
      setUser(result.user)

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

      // Step 3: Store user data
      setUser(data.user)

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
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-b from-sky-200 via-green-100 to-amber-50">
      {/* Decorative background elements - nature theme */}
      <div className="absolute inset-0 overflow-hidden">
        {/* Mountains in background */}
        <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-purple-300/30 to-transparent" />
        {/* Trees silhouette */}
        <div className="absolute bottom-0 left-10 h-24 w-24 rounded-t-full bg-green-600/20" />
        <div className="absolute bottom-0 right-20 h-32 w-32 rounded-t-full bg-green-700/20" />
        {/* Path */}
        <div className="absolute bottom-0 left-1/2 h-16 w-64 -translate-x-1/2 rounded-t-full bg-amber-200/30" />
      </div>

      <div className="relative z-10 w-full max-w-md space-y-6 px-4">
        {/* Book Character Illustration Area */}
        <div className="relative mx-auto mb-4 flex h-48 items-center justify-center">
          {/* Book Character - SVG illustration */}
          <div className="relative">
            {/* Speech bubble */}
            <div className="absolute -top-16 left-1/2 -translate-x-1/2 rounded-2xl rounded-bl-none bg-white px-4 py-3 shadow-lg">
              <p className="text-center font-bold text-amber-800">
                <span className="text-lg">Ahoj!</span>
                <br />
                <span className="text-sm">Český jazyk.</span>
              </p>
            </div>

            {/* Book character */}
            <div className="relative">
              {/* Book body */}
              <div className="relative h-32 w-24 rounded-lg bg-gradient-to-br from-amber-700 to-amber-900 shadow-xl">
                {/* Book pages */}
                <div className="absolute inset-x-0 top-0 h-28 rounded-t-lg bg-amber-50" />
                {/* Book binding */}
                <div className="absolute left-0 top-0 h-full w-2 rounded-l-lg bg-amber-950" />

                {/* Glasses */}
                <div className="absolute left-1/2 top-8 -translate-x-1/2">
                  <div className="flex gap-2">
                    <div className="h-8 w-8 rounded-full border-4 border-amber-950 bg-white" />
                    <div className="h-8 w-8 rounded-full border-4 border-amber-950 bg-white" />
                  </div>
                  <div className="absolute left-1/2 top-1/2 h-0.5 w-3 -translate-x-1/2 bg-amber-950" />
                </div>

                {/* Eyes */}
                <div className="absolute left-1/2 top-10 -translate-x-1/2">
                  <div className="flex gap-2">
                    <div className="h-3 w-3 rounded-full bg-blue-500" />
                    <div className="h-3 w-3 rounded-full bg-blue-500" />
                  </div>
                </div>

                {/* Smile */}
                <div className="absolute left-1/2 top-16 -translate-x-1/2">
                  <svg className="h-6 w-12" viewBox="0 0 48 24">
                    <path
                      d="M 4 12 Q 12 20 24 12 Q 36 4 44 12"
                      stroke="currentColor"
                      strokeWidth="3"
                      fill="none"
                      className="text-amber-950"
                    />
                  </svg>
                </div>

                {/* Cheeks */}
                <div className="absolute left-2 top-14 h-3 w-3 rounded-full bg-pink-300" />
                <div className="absolute right-2 top-14 h-3 w-3 rounded-full bg-pink-300" />

                {/* Arms */}
                <div className="absolute -left-4 top-12 h-6 w-4 rounded-full bg-amber-700" />
                <div className="absolute -right-4 top-12 h-6 w-4 rounded-full bg-amber-700" />

                {/* Legs */}
                <div className="absolute -bottom-2 left-6 h-4 w-3 rounded-full bg-amber-800" />
                <div className="absolute -bottom-2 right-6 h-4 w-3 rounded-full bg-amber-800" />

                {/* Sandals */}
                <div className="absolute -bottom-3 left-5 h-2 w-5 rounded-full bg-amber-950" />
                <div className="absolute -bottom-3 right-5 h-2 w-5 rounded-full bg-amber-950" />
              </div>
            </div>
          </div>
        </div>

        {/* Main content card */}
        <div className="relative rounded-3xl bg-white/95 p-8 shadow-2xl backdrop-blur-sm">
          <div className="text-center">
            <h1 className="text-5xl font-bold text-amber-800 drop-shadow-sm">
              Mluv.Me
            </h1>
            <p className="mt-3 text-lg font-medium text-amber-700">
              Learn Czech with AI-powered conversations
            </p>
            <div className="mt-2 text-sm text-amber-600">
              Practice speaking Czech with Honzík 🇨🇿
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
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:from-blue-600 hover:to-blue-700 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 active:scale-95"
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

              <div className="text-center text-sm font-medium text-amber-700">
                One tap to start learning Czech! 🎉
              </div>
            </div>
          ) : (
            // Browser - show login button
            <div className="mt-6 space-y-4">
              <button
                onClick={handleLogin}
                disabled={isLoading}
                className="flex w-full items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:from-blue-600 hover:to-blue-700 hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-50 active:scale-95"
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

              <div className="text-center text-sm font-medium text-amber-700">
                By logging in, you agree to practice Czech and have fun! 🎉
              </div>
            </div>
          )}

          {/* Features section - redesigned */}
          <div className="mt-8 space-y-3 rounded-2xl bg-gradient-to-br from-green-50 to-amber-50 p-6 shadow-inner">
            <h3 className="text-center text-xl font-bold text-green-800">
              Why Mluv.Me?
            </h3>
            <ul className="space-y-2 text-sm text-green-700">
              <li className="flex items-center gap-2">
                <span className="text-lg">📚</span>
                <span>Practice with AI-powered Honzík</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="text-lg">✨</span>
                <span>Get instant feedback on your Czech</span>
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
