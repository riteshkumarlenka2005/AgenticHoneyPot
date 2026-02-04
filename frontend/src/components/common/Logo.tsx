'use client'

import { Shield } from 'lucide-react'
import Link from 'next/link'

export function Logo({ size = 'default' }: { size?: 'small' | 'default' | 'large' }) {
  const iconSizes = {
    small: 'h-6 w-6',
    default: 'h-8 w-8',
    large: 'h-12 w-12'
  }
  
  const textSizes = {
    small: 'text-lg',
    default: 'text-xl',
    large: 'text-3xl'
  }

  return (
    <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
      <Shield className={`${iconSizes[size]} text-primary`} />
      <span className={`${textSizes[size]} font-bold bg-gradient-to-r from-primary to-blue-600 bg-clip-text text-transparent`}>
        HoneyPot
      </span>
    </Link>
  )
}
