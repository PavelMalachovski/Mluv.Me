"use client"

import React from "react"

interface ClickableTextProps {
  text: string
  onWordClick: (word: string, rect: DOMRect) => void
  className?: string
}

/**
 * Component that renders text with clickable words for translation.
 * Each word can be clicked to trigger a translation popup.
 */
export function ClickableText({ text, onWordClick, className = "" }: ClickableTextProps) {
  // Split text into words while preserving punctuation
  const words = text.split(/(\s+)/)

  const handleWordClick = (e: React.MouseEvent<HTMLSpanElement>, word: string) => {
    // Clean the word from punctuation for translation
    const cleanWord = word.replace(/[.,!?;:"""''„‟«»()[\]{}]/g, "").trim()
    if (cleanWord.length > 0) {
      const rect = e.currentTarget.getBoundingClientRect()
      onWordClick(cleanWord, rect)
    }
  }

  return (
    <p className={`whitespace-pre-wrap leading-relaxed ${className}`}>
      {words.map((segment, index) => {
        // Check if segment is whitespace
        if (/^\s+$/.test(segment)) {
          return <span key={index}>{segment}</span>
        }

        // It's a word - make it clickable
        return (
          <span
            key={index}
            onClick={(e) => handleWordClick(e, segment)}
            className="cursor-pointer hover:bg-yellow-200 dark:hover:bg-yellow-700 hover:rounded px-0.5 transition-colors duration-150"
          >
            {segment}
          </span>
        )
      })}
    </p>
  )
}
