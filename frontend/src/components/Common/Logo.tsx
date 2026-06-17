import { Link } from "@tanstack/react-router"

import { cn } from "@/lib/utils"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

// mynance wordmark (text, no vendored logo). Lowercase brand; the "icon"
// variant collapses to the leading glyph.
export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const text = variant === "icon" ? "m" : "mynance"
  const content = (
    <span
      className={cn(
        "text-lg font-semibold tracking-tight text-ink lowercase",
        className,
      )}
    >
      {text}
    </span>
  )

  if (!asLink) {
    return content
  }

  return (
    <Link to="/" className="inline-flex items-center">
      {content}
    </Link>
  )
}
