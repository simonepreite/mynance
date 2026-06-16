import type { MouseEventHandler, ReactNode } from "react"
import { cn } from "@/lib/utils"
import { focusRing } from "./styles"

type ListRowProps = {
  label: ReactNode
  value?: ReactNode
  /** When provided, the row becomes an interactive button with a focus ring. */
  onSelect?: MouseEventHandler<HTMLButtonElement>
  className?: string
}

// A list row: label on the left, optional value on the right. ≥44px tall.
// Interactive variant is a real button with the keyboard focus ring.
export function ListRow({ label, value, onSelect, className }: ListRowProps) {
  const content = (
    <>
      <span className="type-body text-ink">{label}</span>
      {value !== undefined ? (
        <span className="type-body text-ink-soft">{value}</span>
      ) : null}
    </>
  )

  const base =
    "flex min-h-11 w-full items-center justify-between gap-4 px-4 py-2 text-left"

  if (onSelect) {
    return (
      <button
        type="button"
        data-tap-target
        onClick={onSelect}
        className={cn(focusRing, base, className)}
      >
        {content}
      </button>
    )
  }

  return <div className={cn(base, className)}>{content}</div>
}
