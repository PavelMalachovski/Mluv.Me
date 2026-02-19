"use client"

import React from "react"

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div
          role="alert"
          className="flex min-h-[60vh] flex-col items-center justify-center gap-4 p-8 text-center"
        >
          <div className="text-4xl">😿</div>
          <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200">
            Něco se pokazilo
          </h2>
          <p className="max-w-md text-sm text-gray-600 dark:text-gray-400">
            Omlouváme se za nepříjemnosti. Zkuste obnovit stránku.
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null })
              window.location.reload()
            }}
            className="rounded-lg bg-purple-600 px-6 py-2 text-sm font-medium text-white transition hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2"
            aria-label="Obnovit stránku"
          >
            Obnovit stránku
          </button>
          {process.env.NODE_ENV === "development" && this.state.error && (
            <pre className="mt-4 max-w-lg overflow-auto rounded bg-gray-100 p-3 text-left text-xs text-red-600 dark:bg-gray-800 dark:text-red-400">
              {this.state.error.message}
            </pre>
          )}
        </div>
      )
    }

    return this.props.children
  }
}
