import type { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { focusRing } from "./styles"

export type BottomNavItem = {
  id: string
  label: string
  icon?: ReactNode
}

type BottomNavProps = {
  items: BottomNavItem[]
  activeId: string
  onSelect?: (id: string) => void
  className?: string
}

// Bottom navigation. Each slot is a ≥44px button with the keyboard focus ring;
// the active slot uses the legible accent-ink (Story 1.2, AC2/AC3/AC4).
export function BottomNav({
  items,
  activeId,
  onSelect,
  className,
}: BottomNavProps) {
  return (
    <nav
      aria-label="Primary"
      className={cn(
        "flex items-stretch gap-1 rounded-panel bg-surface p-2 shadow-[var(--shadow-card)]",
        className,
      )}
    >
      {items.map((item) => {
        const active = item.id === activeId
        return (
          <button
            key={item.id}
            type="button"
            data-tap-target
            aria-current={active ? "page" : undefined}
            onClick={() => onSelect?.(item.id)}
            className={cn(
              focusRing,
              "flex min-h-11 min-w-11 flex-1 flex-col items-center justify-center gap-1 rounded-lg type-caption",
              active ? "text-accent-ink" : "text-ink-soft",
            )}
          >
            {item.icon ? <span aria-hidden="true">{item.icon}</span> : null}
            <span>{item.label}</span>
          </button>
        )
      })}
    </nav>
  )
}
