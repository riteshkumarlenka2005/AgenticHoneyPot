import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Agentic HoneyPot - Scam Detection System',
  description: 'Autonomous AI honeypot for scam detection and intelligence extraction',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <div className="min-h-screen bg-background text-foreground">
          <nav className="border-b border-border bg-secondary/50">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <Link href="/dashboard" className="text-2xl font-bold text-primary">
                  🍯 Agentic HoneyPot
                </Link>
                <div className="flex gap-6">
                  <Link href="/dashboard" className="hover:text-primary transition-colors">
                    Dashboard
                  </Link>
                  <Link href="/conversations" className="hover:text-primary transition-colors">
                    Conversations
                  </Link>
                  <Link href="/intelligence" className="hover:text-primary transition-colors">
                    Intelligence
                  </Link>
                  <Link href="/analytics" className="hover:text-primary transition-colors">
                    Analytics
                  </Link>
                  <Link href="/settings" className="hover:text-primary transition-colors">
                    Settings
                  </Link>
                </div>
              </div>
            </div>
          </nav>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
