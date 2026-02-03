"use client"

import { useState, useRef, useCallback } from "react"
import { Send, Mic, Keyboard } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * Чешские символы с диакритикой.
 * Разделены на строчные и заглавные для удобного переключения.
 */
const CZECH_CHARS_LOWER = ["á", "č", "ď", "é", "ě", "í", "ň", "ó", "ř", "š", "ť", "ú", "ů", "ý", "ž"]
const CZECH_CHARS_UPPER = ["Á", "Č", "Ď", "É", "Ě", "Í", "Ň", "Ó", "Ř", "Š", "Ť", "Ú", "Ů", "Ý", "Ž"]

interface CzechTextInputProps {
  /** Callback при отправке текста */
  onSubmit: (text: string) => void
  /** Callback при начале записи голоса */
  onVoiceStart?: () => void
  /** Флаг загрузки/обработки */
  isLoading: boolean
  /** Текущий режим ввода */
  mode: "text" | "voice"
  /** Callback для смены режима */
  onModeChange: (mode: "text" | "voice") => void
  /** Placeholder для текстового поля */
  placeholder?: string
  /** Максимальная длина текста */
  maxLength?: number
  /** Дополнительные классы для контейнера */
  className?: string
}

/**
 * Компонент ввода текста с чешской клавиатурой (диакритика).
 *
 * Особенности:
 * - Встроенные кнопки для чешских символов (á, č, ř, š, ž и др.)
 * - Переключение между строчными и заглавными символами (Shift)
 * - Переключение между текстовым и голосовым режимом
 * - Enter для отправки, Shift+Enter для новой строки
 *
 * @example
 * ```tsx
 * <CzechTextInput
 *   onSubmit={(text) => console.log(text)}
 *   isLoading={false}
 *   mode="text"
 *   onModeChange={(mode) => setMode(mode)}
 * />
 * ```
 */
export function CzechTextInput({
  onSubmit,
  onVoiceStart,
  isLoading,
  mode,
  onModeChange,
  placeholder = "Napiš zprávu v češtině...",
  maxLength = 2000,
  className,
}: CzechTextInputProps) {
  const [text, setText] = useState("")
  const [isShiftPressed, setIsShiftPressed] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Выбираем набор символов в зависимости от Shift
  const czechChars = isShiftPressed ? CZECH_CHARS_UPPER : CZECH_CHARS_LOWER

  /**
   * Вставить чешский символ в текущую позицию курсора.
   */
  const insertChar = useCallback((char: string) => {
    if (textareaRef.current) {
      const start = textareaRef.current.selectionStart
      const end = textareaRef.current.selectionEnd
      const newText = text.slice(0, start) + char + text.slice(end)

      if (newText.length <= maxLength) {
        setText(newText)

        // Устанавливаем курсор после вставленного символа
        setTimeout(() => {
          textareaRef.current?.setSelectionRange(start + 1, start + 1)
          textareaRef.current?.focus()
        }, 0)
      }
    }
  }, [text, maxLength])

  /**
   * Обработка отправки сообщения.
   */
  const handleSubmit = useCallback(() => {
    if (text.trim() && !isLoading) {
      onSubmit(text.trim())
      setText("")
    }
  }, [text, isLoading, onSubmit])

  /**
   * Обработка нажатия клавиш.
   * Enter - отправка, Shift+Enter - новая строка.
   */
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  /**
   * Обработка изменения текста.
   */
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    if (newValue.length <= maxLength) {
      setText(newValue)
    }
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Переключатель режима Text/Voice */}
      <div className="flex items-center justify-center gap-2">
        <button
          type="button"
          onClick={() => onModeChange("text")}
          disabled={isLoading}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg transition-all font-medium text-sm",
            mode === "text"
              ? "bg-blue-600 text-white shadow-md"
              : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
          )}
        >
          <Keyboard className="h-4 w-4" />
          Text
        </button>
        <button
          type="button"
          onClick={() => onModeChange("voice")}
          disabled={isLoading}
          className={cn(
            "flex items-center gap-2 px-4 py-2 rounded-lg transition-all font-medium text-sm",
            mode === "voice"
              ? "bg-blue-600 text-white shadow-md"
              : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
          )}
        >
          <Mic className="h-4 w-4" />
          Hlas
        </button>
      </div>

      {mode === "text" ? (
        <>
          {/* Чешская клавиатура (диакритика) */}
          <div className="space-y-2">
            {/* Shift toggle */}
            <div className="flex items-center justify-center gap-2">
              <button
                type="button"
                onClick={() => setIsShiftPressed(!isShiftPressed)}
                className={cn(
                  "px-3 py-1 rounded text-xs font-medium transition-all",
                  isShiftPressed
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                )}
              >
                {isShiftPressed ? "ABC" : "abc"} ⇧
              </button>
            </div>

            {/* Кнопки чешских символов */}
            <div className="flex flex-wrap gap-1 justify-center">
              {czechChars.map((char) => (
                <button
                  key={char}
                  type="button"
                  onClick={() => insertChar(char)}
                  disabled={isLoading}
                  className={cn(
                    "w-8 h-8 rounded font-medium text-sm transition-all",
                    "bg-blue-100 dark:bg-blue-900/50 hover:bg-blue-200 dark:hover:bg-blue-800",
                    "text-blue-800 dark:text-blue-200",
                    "active:scale-95 disabled:opacity-50"
                  )}
                >
                  {char}
                </button>
              ))}
            </div>
          </div>

          {/* Текстовое поле */}
          <div className="relative">
            <textarea
              ref={textareaRef}
              value={text}
              onChange={handleTextChange}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={isLoading}
              rows={3}
              className={cn(
                "w-full p-4 pr-14 rounded-xl resize-none",
                "border-2 border-gray-200 dark:border-gray-700",
                "bg-white dark:bg-gray-800",
                "text-gray-900 dark:text-gray-100",
                "placeholder:text-gray-400 dark:placeholder:text-gray-500",
                "focus:border-blue-500 dark:focus:border-blue-400 focus:outline-none",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "transition-colors"
              )}
            />

            {/* Кнопка отправки */}
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!text.trim() || isLoading}
              className={cn(
                "absolute right-3 bottom-3 p-2.5 rounded-full",
                "bg-blue-600 text-white",
                "hover:bg-blue-700 active:scale-95",
                "disabled:opacity-50 disabled:cursor-not-allowed",
                "transition-all"
              )}
            >
              <Send className="h-5 w-5" />
            </button>
          </div>

          {/* Подсказки */}
          <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
            <span>Enter = odeslat • Shift+Enter = nový řádek</span>
            <span>{text.length}/{maxLength}</span>
          </div>
        </>
      ) : (
        /* Голосовой режим - placeholder для VoiceRecorder */
        <div className="text-center py-8">
          <button
            type="button"
            onClick={onVoiceStart}
            disabled={isLoading}
            className={cn(
              "w-20 h-20 rounded-full mx-auto flex items-center justify-center",
              "bg-blue-600 text-white shadow-lg",
              "hover:bg-blue-700 active:scale-95",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-all"
            )}
          >
            <Mic className="h-10 w-10" />
          </button>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-3">
            🎤 Klepni pro nahrání (max 60 sekund)
          </p>
        </div>
      )}
    </div>
  )
}

export default CzechTextInput
