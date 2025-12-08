import * as React from "react"
import { cn } from "@/lib/utils"
import { X } from "lucide-react"

export interface ToastProps {
  id: string
  title?: string
  description?: string
  variant?: "default" | "success" | "error"
  duration?: number
  onClose: () => void
}

export function Toast({ title, description, variant = "default", onClose }: ToastProps) {
  return (
    <div
      className={cn(
        "pointer-events-auto flex w-full max-w-md rounded-lg shadow-lg ring-1 ring-black ring-opacity-5",
        variant === "success" && "bg-green-50 ring-green-200",
        variant === "error" && "bg-red-50 ring-red-200",
        variant === "default" && "bg-white"
      )}
    >
      <div className="w-0 flex-1 p-4">
        <div className="flex items-start">
          <div className="ml-3 flex-1">
            {title && (
              <p
                className={cn(
                  "text-sm font-medium",
                  variant === "success" && "text-green-900",
                  variant === "error" && "text-red-900",
                  variant === "default" && "text-gray-900"
                )}
              >
                {title}
              </p>
            )}
            {description && (
              <p
                className={cn(
                  "mt-1 text-sm",
                  variant === "success" && "text-green-700",
                  variant === "error" && "text-red-700",
                  variant === "default" && "text-gray-500"
                )}
              >
                {description}
              </p>
            )}
          </div>
        </div>
      </div>
      <div className="flex border-l border-gray-200">
        <button
          onClick={onClose}
          className="flex w-full items-center justify-center rounded-none rounded-r-lg border border-transparent p-4 text-sm font-medium text-gray-700 hover:text-gray-500 focus:outline-none"
        >
          <X className="h-5 w-5" />
        </button>
      </div>
    </div>
  )
}

export function ToastContainer({ children }: { children: React.ReactNode }) {
  return (
    <div className="pointer-events-none fixed bottom-0 right-0 z-50 flex flex-col gap-2 p-6 sm:bottom-0 sm:right-0">
      {children}
    </div>
  )
}
