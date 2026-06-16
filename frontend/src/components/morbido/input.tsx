import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"
import { focusRing } from "./styles"

// Generic Morbido text input. ≥44px tall, token-styled, keyboard focus ring.
export function Input({ className, ...props }: ComponentProps<"input">) {
  return (
    <input
      data-tap-target
      className={cn(
        focusRing,
        "min-h-11 w-full rounded-lg border border-border bg-surface px-4 type-body text-ink placeholder:text-ink-soft",
        className,
      )}
      {...props}
    />
  )
}
