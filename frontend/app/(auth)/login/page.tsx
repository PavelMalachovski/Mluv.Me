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
      // Auto-login with Web App data
      handleWebAppLogin()
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
    try {
      // Initialize Telegram Web App
      const webApp = initTelegramWebApp()

      if (!webApp) {
        throw new Error("Failed to initialize Telegram Web App")
      }

      const user = getTelegramUser()

      if (!user) {
        throw new Error("No user data from Telegram")
      }

      // Authenticate with backend
      const result = await authenticateWebApp()

      if (!result.success) {
        throw new Error(result.error || "Authentication failed")
      }

      // Store user data
      setUser(result.user)

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
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-blue-100">
      <div className="w-full max-w-md space-y-8 rounded-lg bg-white p-8 shadow-lg">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-blue-600">Mluv.Me</h1>
          <p className="mt-2 text-lg text-gray-600">
            Learn Czech with AI-powered conversations
          </p>
          <div className="mt-4 text-sm text-gray-500">
            Practice speaking Czech with Honzík 🇨🇿
          </div>
        </div>

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {isWebApp ? (
          // Telegram Web App - auto-authenticating
          <div className="space-y-4 text-center">
            <div className="flex items-center justify-center">
              <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
            </div>
            <p className="text-gray-600">
              {isLoading ? "Authenticating with Telegram..." : "Welcome!"}
            </p>
          </div>
        ) : (
          // Browser - show login button
          <div className="space-y-4">
            <button
              onClick={handleLogin}
              disabled={isLoading}
              className="flex w-full items-center justify-center gap-3 rounded-lg bg-blue-500 px-4 py-3 text-white transition-colors hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
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

            <div className="text-center text-xs text-gray-500">
              By logging in, you agree to practice Czech and have fun!
            </div>
          </div>
        )}

        <div className="mt-8 space-y-2 rounded-md bg-blue-50 p-4">
          <h3 className="font-semibold text-blue-900">Why Mluv.Me?</h3>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>✅ Practice with AI-powered Honzík</li>
            <li>✅ Get instant feedback on your Czech</li>
            <li>✅ Track your progress and earn stars</li>
            <li>✅ Learn at your own pace</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
