import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { PeriodSelector } from "@/components/Common/PeriodSelector"
import { Card } from "@/components/morbido"
import { Skeleton } from "@/components/ui/skeleton"
import {
  type CategoriaSpesa,
  RiepilogoService,
  type TrendPunto,
} from "@/lib/api"
import { formatEurFromCents } from "@/lib/format"
import { type Period, todayIso } from "@/lib/periodo"

export const Route = createFileRoute("/_layout/statistiche")({
  component: Statistiche,
  head: () => ({
    meta: [{ title: "Statistiche - mynance" }],
  }),
})

// Calm, distinct slice colors (warm + cool); legend carries the label so colour
// is never the only signifier.
const PALETTE = [
  "#7C9885",
  "#C58B6B",
  "#8A7CA8",
  "#D4A55E",
  "#6B9AC4",
  "#B5705F",
  "#9DB17C",
  "#A88FB0",
]

function Statistiche() {
  const [period, setPeriod] = useState<Period>("month")
  const [anchor, setAnchor] = useState(todayIso())

  const { data, isPending } = useQuery({
    queryKey: ["statistiche", period, anchor],
    queryFn: () => RiepilogoService.statistiche({ anchor, period }),
  })

  return (
    <div className="flex flex-col gap-6">
      <h1 className="type-h1 text-ink">Statistiche</h1>
      <PeriodSelector
        period={period}
        anchor={anchor}
        onChange={(n) => {
          setPeriod(n.period)
          setAnchor(n.anchor)
        }}
      />

      {isPending || !data ? (
        <Skeleton className="h-64 w-full rounded-card" />
      ) : !data.has_trend && !data.has_pie ? (
        <Card className="py-12 text-center">
          <p className="type-body text-ink-soft">
            Servono più dati per i grafici.
          </p>
        </Card>
      ) : (
        <>
          {data.has_trend ? (
            <Card className="flex flex-col gap-4">
              <h2 className="type-eyebrow">Andamento (ultimi 6 mesi)</h2>
              <TrendChart trend={data.trend} />
              <Legend
                items={[
                  { label: "Entrate", color: "var(--color-positive-ink)" },
                  { label: "Spese", color: "var(--color-negative)" },
                  { label: "Netto", color: "var(--color-ink)" },
                ]}
              />
            </Card>
          ) : null}

          {data.has_pie ? (
            <Card className="flex flex-col gap-4">
              <h2 className="type-eyebrow">Spese per categoria</h2>
              <PieChart slices={data.pie} />
            </Card>
          ) : (
            <Card className="py-8 text-center">
              <p className="type-body text-ink-soft">
                Nessuna spesa in questo periodo.
              </p>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

function TrendChart({ trend }: { trend: TrendPunto[] }) {
  const W = 320
  const H = 160
  const pad = 8
  const entrate = trend.map((t) => t.entrate_cents)
  const spese = trend.map((t) => t.spese_cents)
  const netto = trend.map((t) => t.netto_cents)
  const all = [...entrate, ...spese, ...netto, 0]
  const min = Math.min(...all)
  const max = Math.max(...all)
  const span = max - min || 1
  const n = trend.length

  const xy = (i: number, v: number): [number, number] => {
    const x = n === 1 ? W / 2 : pad + (i / (n - 1)) * (W - 2 * pad)
    const y = H - pad - ((v - min) / span) * (H - 2 * pad)
    return [x, y]
  }
  const line = (vals: number[]) =>
    vals.map((v, i) => xy(i, v).join(",")).join(" ")
  const zeroY = xy(0, 0)[1]

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full"
      role="img"
      aria-label="Andamento di entrate, spese e netto negli ultimi sei mesi"
    >
      <line
        x1={pad}
        x2={W - pad}
        y1={zeroY}
        y2={zeroY}
        stroke="currentColor"
        className="text-border"
        strokeDasharray="3 3"
      />
      <polyline
        fill="none"
        stroke="var(--color-positive-ink)"
        strokeWidth="2"
        points={line(entrate)}
      />
      <polyline
        fill="none"
        stroke="var(--color-negative)"
        strokeWidth="2"
        points={line(spese)}
      />
      <polyline
        fill="none"
        stroke="var(--color-ink)"
        strokeWidth="2"
        points={line(netto)}
      />
      {trend.map((t, i) => (
        <text
          key={t.mese}
          x={xy(i, min)[0]}
          y={H - 1}
          textAnchor="middle"
          className="fill-ink-soft"
          style={{ fontSize: "8px" }}
        >
          {t.mese.slice(5)}
        </text>
      ))}
    </svg>
  )
}

function PieChart({ slices }: { slices: CategoriaSpesa[] }) {
  const total = slices.reduce((s, x) => s + x.total_cents, 0)
  const R = 80
  const C = 100
  let acc = 0

  const arc = (frac: number, start: number) => {
    const a0 = start * 2 * Math.PI - Math.PI / 2
    const a1 = (start + frac) * 2 * Math.PI - Math.PI / 2
    const x0 = C + R * Math.cos(a0)
    const y0 = C + R * Math.sin(a0)
    const x1 = C + R * Math.cos(a1)
    const y1 = C + R * Math.sin(a1)
    const large = frac > 0.5 ? 1 : 0
    return `M ${C} ${C} L ${x0} ${y0} A ${R} ${R} 0 ${large} 1 ${x1} ${y1} Z`
  }

  return (
    <div className="flex flex-col items-center gap-4 sm:flex-row sm:items-start">
      <svg
        viewBox="0 0 200 200"
        className="h-44 w-44 shrink-0"
        role="img"
        aria-label="Ripartizione delle spese per categoria"
      >
        {slices.length === 1 ? (
          <circle cx={C} cy={C} r={R} fill={PALETTE[0]} />
        ) : (
          slices.map((s, i) => {
            const frac = s.total_cents / total
            const d = arc(frac, acc)
            acc += frac
            return (
              <path
                key={s.categoria_id}
                d={d}
                fill={PALETTE[i % PALETTE.length]}
              />
            )
          })
        )}
      </svg>
      <ul className="flex w-full flex-col gap-1">
        {slices.map((s, i) => (
          <li
            key={s.categoria_id}
            className="flex items-center justify-between gap-2"
          >
            <span className="flex items-center gap-2 type-caption text-ink">
              <span
                aria-hidden="true"
                className="inline-block size-3 rounded-sm"
                style={{ backgroundColor: PALETTE[i % PALETTE.length] }}
              />
              {s.nome}
            </span>
            <span className="type-caption tabular-nums text-ink-soft">
              {total > 0 ? Math.round((s.total_cents / total) * 100) : 0}% ·{" "}
              {formatEurFromCents(s.total_cents)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <ul className="flex flex-wrap gap-4">
      {items.map((it) => (
        <li
          key={it.label}
          className="flex items-center gap-2 type-caption text-ink-soft"
        >
          <span
            aria-hidden="true"
            className="inline-block h-1 w-4 rounded-pill"
            style={{ backgroundColor: it.color }}
          />
          {it.label}
        </li>
      ))}
    </ul>
  )
}
