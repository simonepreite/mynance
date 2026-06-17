import type { ReactNode } from "react"
import { Card } from "@/components/morbido"

// Calm placeholder for bottom-nav destinations whose feature lands in a later
// epic (Story 1.6, AC2 — "destinations stubbed for later epics"). No nagging,
// no false data; just a gentle "in arrivo" surface.
export function ComingSoon({
  title,
  icon,
  children,
}: {
  title: string
  icon?: ReactNode
  children?: ReactNode
}) {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="type-h1 text-ink">{title}</h1>
      <Card className="flex flex-col items-center gap-3 py-12 text-center">
        {icon ? (
          <span aria-hidden="true" className="text-ink-soft">
            {icon}
          </span>
        ) : null}
        <p className="type-body text-ink-soft">
          {children ?? "Questa sezione arriverà a breve."}
        </p>
      </Card>
    </div>
  )
}
