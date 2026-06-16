import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"
import { focusRing } from "./styles"

type ButtonProps = ComponentProps<"button"> & {
  variant?: "primary" | "secondary"
}

// Generic Morbido button. ≥44px tap target + keyboard focus ring, token colours.
export function Button({
  variant = "primary",
  className,
  ...props
}: ButtonProps) {
  return (
    <button
      type="button"
      data-tap-target
      className={cn(
        focusRing,
        "inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg px-5 type-body",
        variant === "primary"
          ? "bg-primary text-primary-foreground"
          : "bg-surface-2 text-ink",
        className,
      )}
      {...props}
    />
  )
}
