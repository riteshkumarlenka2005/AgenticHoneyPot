'use client'

export function LoadingSpinner({ size = 'default' }: { size?: 'small' | 'default' | 'large' }) {
  const sizes = {
    small: 'h-4 w-4 border-2',
    default: 'h-8 w-8 border-2',
    large: 'h-12 w-12 border-3'
  }

  return (
    <div className="flex items-center justify-center">
      <div
        className={`${sizes[size]} border-primary border-t-transparent rounded-full animate-spin`}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
    </div>
  )
}
