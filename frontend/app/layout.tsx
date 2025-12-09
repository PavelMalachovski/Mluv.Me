import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"

const inter = Inter({ subsets: ["latin"], display: "swap" })

export const metadata: Metadata = {
  title: "Mluv.Me - Learn Czech with AI",
  description: "Learn Czech with Honzík - AI-powered conversations",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        {/* Preload critical images for faster loading */}
        <link rel="preload" href="/images/backgrounds/fantasy-landscape.png" as="image" />
        <link rel="preload" href="/images/mascot/honzik-waving.png" as="image" />
        {/* Telegram Web App SDK */}
        <script src="https://telegram.org/js/telegram-web-app.js" async />
      </head>
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}

