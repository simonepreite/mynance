import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"
import { focusRing } from "./styles"

type ChipProps = ComponentProps<"button"> & {
  selected?: boolean
}

// Pill chip. ≥44px tap target, keyboard focus ring; selected uses the tenuous
// accent-soft fill (never the focus token) — Story 1.2, AC2/AC3/AC4.
export function Chip({ selected = false, className, ...props }: ChipProps) {
  return (
    <button
      type="button"
      data-tap-target
      aria-pressed={selected}
      className={cn(
        focusRing,
        "inline-flex min-h-11 min-w-11 items-center justify-center rounded-pill px-4 type-caption",
        selected ? "bg-accent-soft text-ink" : "bg-surface-2 text-ink-soft",
        className,
      )}
      {...props}
    />
  )
}
