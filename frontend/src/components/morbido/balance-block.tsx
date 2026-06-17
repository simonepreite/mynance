import type { ComponentProps } from "react"
import { formatEurFromCents } from "@/lib/format"
import { cn } from "@/lib/utils"

type BalanceBlockProps = ComponentProps<"div"> & {
  /** Eyebrow label, e.g. "BILANCIO · GIUGNO". */
  label: string
  /** Net amount in integer cents (server-derived; never recomputed here). */
  cents: number
}

// Hero Netto figure. Sign is conveyed by an explicit +/− glyph (never by colour
// alone), and colour uses the text-safe -ink variants (Story 1.2, AC4/AC5).
export function BalanceBlock({
  label,
  cents,
  className,
  ...props
}: BalanceBlockProps) {
  const negative = cents < 0
  const sign = negative ? "−" : "+" // U+2212 true minus / plus
  return (
    <div
      className={cn(
        "rounded-card bg-surface p-6 shadow-[var(--shadow-card)]",
        className,
      )}
      {...props}
    >
      <p className="type-eyebrow">{label}</p>
      <p
        data-testid="balance-amount"
        className={cn(
          "type-display mt-2 tabular-nums",
          negative ? "text-negative" : "text-positive-ink",
        )}
      >
        <span className="sr-only">{negative ? "meno " : "più "}</span>
        <span aria-hidden="true">{sign}</span>
        {formatEurFromCents(Math.abs(cents))}
      </p>
    </div>
  )
}
