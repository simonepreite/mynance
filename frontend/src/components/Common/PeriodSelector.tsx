import { ChevronLeft, ChevronRight } from "lucide-react"

import { Chip } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import { PERIODS, type Period, periodLabel, shiftAnchor } from "@/lib/periodo"

export function PeriodSelector({
  period,
  anchor,
  onChange,
}: {
  period: Period
  anchor: string
  onChange: (next: { period: Period; anchor: string }) => void
}) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-2">
        {PERIODS.map((p) => (
          <Chip
            key={p.value}
            selected={p.value === period}
            onClick={() => onChange({ period: p.value, anchor })}
          >
            {p.label}
          </Chip>
        ))}
      </div>
      <div className="flex items-center justify-between gap-2">
        <Button
          variant="ghost"
          size="icon"
          aria-label="Periodo precedente"
          onClick={() =>
            onChange({ period, anchor: shiftAnchor(period, anchor, -1) })
          }
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <span
          className="type-body font-medium text-ink"
          data-testid="period-label"
        >
          {periodLabel(period, anchor)}
        </span>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Periodo successivo"
          onClick={() =>
            onChange({ period, anchor: shiftAnchor(period, anchor, 1) })
          }
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>
    </div>
  )
}
