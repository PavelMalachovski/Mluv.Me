"use client";

/**
 * CorrectionExplanation - Компонент для отображения исправлений с двуязычными объяснениями.
 *
 * Концепция Language Immersion:
 * - Объяснения сначала на простом чешском (A2)
 * - Перевод на родной язык скрыт по умолчанию
 * - Пользователь может раскрыть перевод при необходимости
 */

import { useState } from "react";
import { ChevronDown, Languages } from "lucide-react";
import { cn } from "@/lib/utils";
import CS_TEXTS from "@/lib/localization/cs";

interface Mistake {
  original: string;
  corrected: string;
  explanation_cs?: string;
  explanation_native?: string;
  // Fallback для старого формата
  explanation?: string;
}

interface CorrectionExplanationProps {
  mistake: Mistake;
  index?: number;
  className?: string;
}

/**
 * Отображение одного исправления с раскрывающимся переводом.
 */
export function CorrectionExplanation({
  mistake,
  index = 1,
  className,
}: CorrectionExplanationProps) {
  const [showNative, setShowNative] = useState(false);

  // Получаем объяснения (с fallback на старый формат)
  const explanationCs = mistake.explanation_cs || mistake.explanation || "";
  const explanationNative = mistake.explanation_native || "";

  return (
    <div
      className={cn(
        "rounded-xl bg-red-50 dark:bg-red-900/20 p-4 space-y-3 border border-red-100 dark:border-red-800/30",
        className
      )}
    >
      {/* Номер исправления */}
      <div className="flex items-start gap-3">
        <span className="flex-shrink-0 w-6 h-6 rounded-full bg-red-100 dark:bg-red-800/40 flex items-center justify-center text-xs font-medium text-red-600 dark:text-red-400">
          {index}
        </span>

        <div className="flex-1 space-y-2">
          {/* Оригинал → Исправление */}
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="line-through text-red-600 dark:text-red-400 bg-red-100/50 dark:bg-red-800/30 px-2 py-0.5 rounded">
              {mistake.original}
            </span>
            <span className="text-gray-400">→</span>
            <span className="font-medium text-green-600 dark:text-green-400 bg-green-100/50 dark:bg-green-800/30 px-2 py-0.5 rounded">
              {mistake.corrected}
            </span>
          </div>

          {/* Объяснение на чешском */}
          {explanationCs && (
            <p className="text-sm text-gray-700 dark:text-gray-300 flex items-start gap-2">
              <span className="text-yellow-500 flex-shrink-0">💡</span>
              <span>{explanationCs}</span>
            </p>
          )}

          {/* Кнопка для показа перевода */}
          {explanationNative && (
            <>
              <button
                onClick={() => setShowNative(!showNative)}
                className="flex items-center gap-1.5 text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
              >
                <Languages className="h-3.5 w-3.5" />
                {showNative
                  ? CS_TEXTS.correction.hideTranslation
                  : CS_TEXTS.correction.showTranslation}
                <ChevronDown
                  className={cn(
                    "h-3.5 w-3.5 transition-transform duration-200",
                    showNative && "rotate-180"
                  )}
                />
              </button>

              {/* Перевод на родной язык (с CSS анимацией) */}
              <div
                className={cn(
                  "overflow-hidden transition-all duration-200 ease-in-out",
                  showNative ? "max-h-40 opacity-100" : "max-h-0 opacity-0"
                )}
              >
                <p className="text-xs text-gray-500 dark:text-gray-400 italic border-l-2 border-blue-300 dark:border-blue-600 pl-3 py-1 bg-blue-50/50 dark:bg-blue-900/20 rounded-r">
                  🌐 {explanationNative}
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Список всех исправлений.
 */
interface CorrectionListProps {
  mistakes: Mistake[];
  className?: string;
}

export function CorrectionList({ mistakes, className }: CorrectionListProps) {
  if (!mistakes || mistakes.length === 0) {
    return (
      <div
        className={cn(
          "rounded-xl bg-green-50 dark:bg-green-900/20 p-4 text-center border border-green-100 dark:border-green-800/30",
          className
        )}
      >
        <span className="text-2xl mb-2 block">🎉</span>
        <p className="text-green-700 dark:text-green-400 font-medium">
          {CS_TEXTS.practice.noCorrections}
        </p>
      </div>
    );
  }

  return (
    <div className={cn("space-y-3", className)}>
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
        <span>📝</span>
        {CS_TEXTS.practice.correctionsHeader}
      </h3>
      {mistakes.map((mistake, index) => (
        <CorrectionExplanation
          key={`${mistake.original}-${index}`}
          mistake={mistake}
          index={index + 1}
        />
      ))}
    </div>
  );
}

/**
 * Подсказка от Хонзика.
 */
interface SuggestionBoxProps {
  suggestion: string;
  className?: string;
}

export function SuggestionBox({ suggestion, className }: SuggestionBoxProps) {
  if (!suggestion) return null;

  return (
    <div
      className={cn(
        "rounded-xl bg-blue-50 dark:bg-blue-900/20 p-4 border border-blue-100 dark:border-blue-800/30",
        className
      )}
    >
      <p className="text-sm text-blue-700 dark:text-blue-400 flex items-start gap-2">
        <span className="text-lg flex-shrink-0">💬</span>
        <span>
          <strong>Tip od Honzíka:</strong> {suggestion}
        </span>
      </p>
    </div>
  );
}

export default CorrectionExplanation;
