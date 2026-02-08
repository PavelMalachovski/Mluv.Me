"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import Image from "next/image"
import { motion, AnimatePresence } from "framer-motion"
import { Volume2, VolumeX, X } from "lucide-react"

/**
 * Video scenes for Honzík's animated avatar introduction.
 * Each scene has a mascot emotion, speech text, and duration.
 */
interface VideoScene {
  emotion: string
  imageSrc: string
  textCs: string
  textRu: string
  durationMs: number
}

type VideoType = "welcome" | "achievement"

interface HonzikVideoAvatarProps {
  type: VideoType
  achievementName?: string
  language?: "cs" | "ru"
  onComplete?: () => void
  onDismiss?: () => void
  autoPlay?: boolean
  className?: string
}

// ===== Welcome Video Scenes (10-12 seconds total) =====
const WELCOME_SCENES: VideoScene[] = [
  {
    emotion: "waving",
    imageSrc: "/images/mascot/honzik-waving.png",
    textCs: "Ahoj! Já jsem Honzík! 👋",
    textRu: "Привет! Я Хонзик! 👋",
    durationMs: 2500,
  },
  {
    emotion: "happy",
    imageSrc: "/images/mascot/honzik-happy.png",
    textCs: "Jsem tvůj kamarád z Česka 🇨🇿",
    textRu: "Я твой друг из Чехии 🇨🇿",
    durationMs: 2500,
  },
  {
    emotion: "reading",
    imageSrc: "/images/mascot/honzik-reading.png",
    textCs: "Miluju pivo, knedlíky a češtinu! 🍺📚",
    textRu: "Люблю пиво, кнедлики и чешский! 🍺📚",
    durationMs: 2500,
  },
  {
    emotion: "encouraging",
    imageSrc: "/images/mascot/honzik-encouraging.png",
    textCs: "Můžeš mi psát nebo mluvit hlasem 🎤✍️",
    textRu: "Можешь писать или говорить голосом 🎤✍️",
    durationMs: 2500,
  },
  {
    emotion: "stars",
    imageSrc: "/images/mascot/honzik-stars.png",
    textCs: "Pojďme se učit česky! Tak jo? ⭐",
    textRu: "Давай учить чешский! Начнём? ⭐",
    durationMs: 2000,
  },
]

// ===== Achievement Celebration Scenes (2-3 seconds) =====
const ACHIEVEMENT_SCENES: VideoScene[] = [
  {
    emotion: "stars",
    imageSrc: "/images/mascot/honzik-stars.png",
    textCs: "🎉 Gratuluju! Máš nový úspěch!",
    textRu: "🎉 Поздравляю! Новое достижение!",
    durationMs: 1500,
  },
  {
    emotion: "happy",
    imageSrc: "/images/mascot/honzik-happy.png",
    textCs: "Jsi úžasný! Pokračuj! 💪",
    textRu: "Ты молодец! Продолжай! 💪",
    durationMs: 1500,
  },
]

// Cache key for storing video seen state
const WELCOME_VIDEO_SEEN_KEY = "honzik_welcome_seen"
const VIDEO_CACHE_PREFIX = "honzik_video_cache_"

/**
 * Check if welcome video has been seen
 */
export function hasSeenWelcomeVideo(): boolean {
  if (typeof window === "undefined") return true
  return localStorage.getItem(WELCOME_VIDEO_SEEN_KEY) === "true"
}

/**
 * Mark welcome video as seen
 */
export function markWelcomeVideoSeen(): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(WELCOME_VIDEO_SEEN_KEY, "true")
  }
}

/**
 * Cache video scene data for faster subsequent loads
 */
function cacheVideoScenes(type: VideoType): void {
  if (typeof window === "undefined") return
  const scenes = type === "welcome" ? WELCOME_SCENES : ACHIEVEMENT_SCENES
  const cacheKey = `${VIDEO_CACHE_PREFIX}${type}`
  try {
    localStorage.setItem(cacheKey, JSON.stringify({
      scenes,
      cachedAt: Date.now(),
      version: "1.0",
    }))
  } catch {
    // localStorage full — ignore
  }
}

/**
 * Preload mascot images for smooth playback
 */
export function preloadVideoImages(type: VideoType = "welcome"): void {
  if (typeof window === "undefined") return
  const scenes = type === "welcome" ? WELCOME_SCENES : ACHIEVEMENT_SCENES
  const uniqueImages = [...new Set(scenes.map((s) => s.imageSrc))]
  uniqueImages.forEach((src) => {
    const img = new window.Image()
    img.src = src
  })
}

/**
 * Honzík Video Avatar — animated mascot "video" intro.
 *
 * Creates a cinematic feel using Honzík's mascot images,
 * framer-motion animations, and timed speech bubbles.
 */
export function HonzikVideoAvatar({
  type,
  achievementName,
  language = "cs",
  onComplete,
  onDismiss,
  autoPlay = true,
  className = "",
}: HonzikVideoAvatarProps) {
  const scenes = type === "welcome" ? WELCOME_SCENES : ACHIEVEMENT_SCENES
  const [currentScene, setCurrentScene] = useState(0)
  const [isPlaying, setIsPlaying] = useState(autoPlay)
  const [isMuted, setIsMuted] = useState(false)
  const [showOverlay, setShowOverlay] = useState(true)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const sceneStartRef = useRef<number>(Date.now())

  // Cache scenes on mount
  useEffect(() => {
    cacheVideoScenes(type)
    preloadVideoImages(type)
  }, [type])

  // Scene progression
  useEffect(() => {
    if (!isPlaying || !showOverlay) return

    sceneStartRef.current = Date.now()
    const scene = scenes[currentScene]

    timerRef.current = setTimeout(() => {
      if (currentScene < scenes.length - 1) {
        setCurrentScene((prev) => prev + 1)
      } else {
        // Video complete
        setIsPlaying(false)
        if (type === "welcome") {
          markWelcomeVideoSeen()
        }
        // Auto-dismiss after last scene
        setTimeout(() => {
          setShowOverlay(false)
          onComplete?.()
        }, 1000)
      }
    }, scene.durationMs)

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [currentScene, isPlaying, showOverlay, scenes, type, onComplete])

  const handleDismiss = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    setShowOverlay(false)
    if (type === "welcome") {
      markWelcomeVideoSeen()
    }
    onDismiss?.()
  }, [type, onDismiss])

  const handleSkip = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current)
    if (currentScene < scenes.length - 1) {
      setCurrentScene((prev) => prev + 1)
    } else {
      handleDismiss()
    }
  }, [currentScene, scenes.length, handleDismiss])

  if (!showOverlay) return null

  const scene = scenes[currentScene]
  const text = language === "ru" ? scene.textRu : scene.textCs
  const progress = ((currentScene + 1) / scenes.length) * 100

  // For achievement, customize text
  const displayText = type === "achievement" && achievementName
    ? text.replace("!", `: ${achievementName}!`)
    : text

  return (
    <AnimatePresence>
      {showOverlay && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className={`fixed inset-0 z-[100] flex items-center justify-center ${className}`}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

          {/* Video Container */}
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: "spring", damping: 20, stiffness: 300 }}
            className="relative z-10 mx-4 w-full max-w-sm"
          >
            {/* Card */}
            <div className="rounded-3xl bg-gradient-to-b from-purple-50 to-amber-50 dark:from-gray-800 dark:to-gray-900 shadow-2xl overflow-hidden border-2 border-purple-200 dark:border-purple-800">
              {/* Progress Bar */}
              <div className="h-1 bg-gray-200 dark:bg-gray-700">
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-500 to-amber-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>

              {/* Controls Bar */}
              <div className="flex items-center justify-between px-4 py-2">
                <button
                  onClick={() => setIsMuted(!isMuted)}
                  className="p-1.5 rounded-full hover:bg-purple-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label={isMuted ? "Unmute" : "Mute"}
                >
                  {isMuted ? (
                    <VolumeX className="w-4 h-4 text-gray-500" />
                  ) : (
                    <Volume2 className="w-4 h-4 text-purple-500" />
                  )}
                </button>

                <span className="text-xs text-gray-400">
                  {currentScene + 1} / {scenes.length}
                </span>

                <button
                  onClick={handleDismiss}
                  className="p-1.5 rounded-full hover:bg-purple-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Close"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              </div>

              {/* Mascot Scene */}
              <div className="relative px-8 pt-4 pb-6">
                {/* Floating Particles */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                  {[...Array(6)].map((_, i) => (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 rounded-full bg-purple-300/40"
                      initial={{
                        x: Math.random() * 300,
                        y: Math.random() * 300,
                        scale: 0,
                      }}
                      animate={{
                        y: [null, -50, 0],
                        scale: [0, 1, 0],
                        opacity: [0, 0.6, 0],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        delay: i * 0.5,
                      }}
                    />
                  ))}
                </div>

                {/* Mascot Image */}
                <div className="flex justify-center mb-4">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={scene.emotion}
                      initial={{ scale: 0.5, opacity: 0, y: 20 }}
                      animate={{ scale: 1, opacity: 1, y: 0 }}
                      exit={{ scale: 0.5, opacity: 0, y: -20 }}
                      transition={{ type: "spring", damping: 15, stiffness: 200 }}
                    >
                      <div className="relative">
                        {/* Glow effect */}
                        <div className="absolute -inset-4 bg-gradient-to-r from-purple-400/20 to-amber-400/20 rounded-full blur-xl" />
                        <Image
                          src={scene.imageSrc}
                          alt={`Honzík - ${scene.emotion}`}
                          width={160}
                          height={160}
                          className="relative drop-shadow-2xl"
                          priority
                        />
                      </div>
                    </motion.div>
                  </AnimatePresence>
                </div>

                {/* Speech Bubble */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentScene}
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.3 }}
                    className="relative"
                  >
                    {/* Speech bubble pointer */}
                    <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white dark:bg-gray-700 rotate-45 border-l border-t border-purple-200 dark:border-purple-700" />

                    <div className="bg-white dark:bg-gray-700 rounded-2xl px-6 py-4 shadow-lg border border-purple-200 dark:border-purple-700 text-center">
                      <p className="text-lg font-medium text-gray-800 dark:text-gray-100 leading-relaxed">
                        {displayText}
                      </p>
                    </div>
                  </motion.div>
                </AnimatePresence>

                {/* Tap to skip hint */}
                <motion.button
                  onClick={handleSkip}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 }}
                  className="mt-4 w-full text-center text-xs text-gray-400 dark:text-gray-500 hover:text-purple-500 transition-colors"
                >
                  {currentScene < scenes.length - 1
                    ? "Tap to skip →"
                    : "Tap to close"
                  }
                </motion.button>
              </div>

              {/* Scene Dots */}
              <div className="flex justify-center gap-1.5 pb-4">
                {scenes.map((_, idx) => (
                  <div
                    key={idx}
                    className={`h-1.5 rounded-full transition-all duration-300 ${
                      idx === currentScene
                        ? "w-6 bg-purple-500"
                        : idx < currentScene
                        ? "w-1.5 bg-purple-300"
                        : "w-1.5 bg-gray-300 dark:bg-gray-600"
                    }`}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * Compact inline achievement celebration (non-blocking)
 */
export function HonzikAchievementToast({
  achievementName,
  language = "cs",
  onComplete,
}: {
  achievementName: string
  language?: "cs" | "ru"
  onComplete?: () => void
}) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setVisible(false)
      onComplete?.()
    }, 3000)
    return () => clearTimeout(timer)
  }, [onComplete])

  if (!visible) return null

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ type: "spring", damping: 20 }}
          className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[90] max-w-xs w-full mx-4"
        >
          <div className="flex items-center gap-3 bg-gradient-to-r from-purple-500 to-amber-500 rounded-2xl px-4 py-3 shadow-lg text-white">
            <Image
              src="/images/mascot/honzik-stars.png"
              alt="Honzík"
              width={48}
              height={48}
              className="drop-shadow-lg"
            />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold">
                {language === "ru" ? "🎉 Новое достижение!" : "🎉 Nový úspěch!"}
              </p>
              <p className="text-xs opacity-90 truncate">{achievementName}</p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
