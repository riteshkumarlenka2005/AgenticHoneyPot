'use client'

import { useEffect, useState } from 'react'

const stats = [
  { label: 'Scams Detected', value: 15420, suffix: '+' },
  { label: 'Intelligence Extracted', value: 8934, suffix: '+' },
  { label: 'Hours Wasted', value: 12567, suffix: '+' },
  { label: 'Active Users', value: 2341, suffix: '+' },
]

export function Stats() {
  const [counts, setCounts] = useState(stats.map(() => 0))
  const [hasAnimated, setHasAnimated] = useState(false)

  useEffect(() => {
    if (hasAnimated) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setHasAnimated(true)
          
          stats.forEach((stat, index) => {
            const duration = 2000
            const steps = 60
            const increment = stat.value / steps
            let current = 0

            const timer = setInterval(() => {
              current += increment
              if (current >= stat.value) {
                setCounts(prev => {
                  const newCounts = [...prev]
                  newCounts[index] = stat.value
                  return newCounts
                })
                clearInterval(timer)
              } else {
                setCounts(prev => {
                  const newCounts = [...prev]
                  newCounts[index] = Math.floor(current)
                  return newCounts
                })
              }
            }, duration / steps)
          })
        }
      },
      { threshold: 0.5 }
    )

    const element = document.getElementById('stats-section')
    if (element) observer.observe(element)

    return () => observer.disconnect()
  }, [hasAnimated])

  return (
    <section id="stats-section" className="py-20 sm:py-32 bg-primary text-primary-foreground">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 text-center">
          {stats.map((stat, index) => (
            <div key={index}>
              <div className="text-4xl sm:text-5xl font-bold mb-2">
                {counts[index].toLocaleString()}{stat.suffix}
              </div>
              <div className="text-primary-foreground/80 text-sm sm:text-base">
                {stat.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
