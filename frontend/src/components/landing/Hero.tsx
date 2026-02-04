'use client'

import Link from 'next/link'
import { ArrowRight, Play } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-background to-muted/20 py-20 sm:py-32">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          {/* Badge */}
          <div className="mb-8 inline-flex items-center rounded-full border px-4 py-1.5 text-sm">
            <span className="mr-2 inline-block h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
            AI-Powered Scam Detection
          </div>

          {/* Headline */}
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl lg:text-7xl mb-6">
            AI-Powered{' '}
            <span className="bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
              Scam Detection
            </span>{' '}
            & Intelligence Extraction
          </h1>

          {/* Subheadline */}
          <p className="text-lg sm:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
            Deploy autonomous AI agents that detect scams in real-time, extract intelligence, 
            and waste scammers' time with believable personas. Turn the tables on cybercriminals.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/register">
              <Button size="lg" className="text-base px-8 group">
                Get Started
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="#how-it-works">
              <Button size="lg" variant="outline" className="text-base px-8 group">
                <Play className="mr-2 h-4 w-4" />
                Learn More
              </Button>
            </Link>
          </div>

          {/* Hero Image/Illustration Placeholder */}
          <div className="mt-16 relative">
            <div className="rounded-xl border bg-card shadow-2xl overflow-hidden">
              <div className="aspect-video bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950 dark:to-cyan-950 flex items-center justify-center">
                <div className="text-center p-8">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-primary/10 mb-4">
                    <Play className="h-10 w-10 text-primary" />
                  </div>
                  <p className="text-sm text-muted-foreground">Dashboard Preview</p>
                </div>
              </div>
            </div>
            {/* Decorative elements */}
            <div className="absolute -top-4 -right-4 w-72 h-72 bg-blue-400/20 rounded-full blur-3xl -z-10"></div>
            <div className="absolute -bottom-4 -left-4 w-72 h-72 bg-cyan-400/20 rounded-full blur-3xl -z-10"></div>
          </div>
        </div>
      </div>
    </section>
  )
}
