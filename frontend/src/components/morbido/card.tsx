import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"

// Floating Morbido surface — very rounded, warm cream, soft elevation.
// Styled solely from theme tokens (Story 1.2, AC2).
export function Card({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      className={cn(
        "rounded-card bg-surface p-6 text-ink shadow-[var(--shadow-card)]",
        className,
      )}
      {...props}
    />
  )
}
