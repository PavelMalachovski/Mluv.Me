"use client"

import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api-client"
import { SubscriptionInfo } from "@/lib/types"
import { AlertTriangle, Crown, Zap } from "lucide-react"

/**
 * Banner that shows remaining daily quota.
 * Warns when approaching limit, blocks when exceeded.
 */
export function QuotaBanner() {
  const [sub, setSub] = useState<SubscriptionInfo | null>(null)

  useEffect(() => {
    apiClient
      .getSubscription()
      .then(setSub)
      .catch(() => {})
  }, [])

  if (!sub) return null

  // Pro users don't need the banner
  if (sub.plan === "pro") {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-yellow-500/10 text-yellow-300 text-xs mb-3">
        <Crown className="h-3.5 w-3.5 flex-shrink-0" />
        <span>
          Pro aktivní do{" "}
          {sub.expires_at
            ? new Date(sub.expires_at).toLocaleDateString("cs-CZ")
            : "—"}
        </span>
      </div>
    )
  }

  const textRemaining = sub.text_quota.remaining
  const voiceRemaining = sub.voice_quota.remaining
  const totalRemaining = textRemaining + voiceRemaining

  // All good — don't show anything
  if (textRemaining > 2 && voiceRemaining > 2) return null

  // Low
  if (totalRemaining > 0) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-orange-500/10 text-orange-300 text-xs mb-3">
        <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
        <span>
          Zbývá: {textRemaining} text. / {voiceRemaining} hlas. zpráv dnes
        </span>
      </div>
    )
  }

  // Exhausted
  return (
    <div className="flex flex-col gap-2 px-3 py-3 rounded-lg bg-red-500/10 text-red-300 text-sm mb-3">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 flex-shrink-0" />
        <span className="font-semibold">Denní limit vyčerpán</span>
      </div>
      <p className="text-xs text-red-300/70">
        Free plán: 6 textových + 5 hlasových zpráv denně.
        Přejdi na Pro pro neomezený přístup — přes Telegram bota /subscribe
      </p>
    </div>
  )
}

/**
 * Compact quota indicator for the practice page header.
 */
export function QuotaIndicator() {
  const [sub, setSub] = useState<SubscriptionInfo | null>(null)

  useEffect(() => {
    apiClient
      .getSubscription()
      .then(setSub)
      .catch(() => {})
  }, [])

  if (!sub) return null
  if (sub.plan === "pro") {
    return (
      <span className="inline-flex items-center gap-1 text-xs text-yellow-400">
        <Crown className="h-3 w-3" /> Pro
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1 text-xs text-zinc-400">
      <Zap className="h-3 w-3" />
      {sub.text_quota.remaining}✏️ {sub.voice_quota.remaining}🎤
    </span>
  )
}
