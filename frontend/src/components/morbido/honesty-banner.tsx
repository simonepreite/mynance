import type { ComponentProps } from "react"
import { cn } from "@/lib/utils"

// Surfaced-truth banner: warm amber on amber-bg, never alarm-red (Story 1.2,
// AC5). Carries a subtle entrance that is neutralized under Reduce Motion (AC6).
export function HonestyBanner({
  children,
  className,
  ...props
}: ComponentProps<"div">) {
  return (
    // biome-ignore lint/a11y/useSemanticElements: a status live-region on a banner container is the idiomatic pattern; <output> is for form results
    <div
      role="status"
      data-testid="honesty-banner"
      className={cn(
        "flex animate-[m-fade-in_240ms_ease-out] items-center gap-3 rounded-panel bg-honesty-bg px-5 py-4 type-body text-honesty",
        className,
      )}
      {...props}
    >
      <span aria-hidden="true">⚠</span>
      <span>{children}</span>
    </div>
  )
}
