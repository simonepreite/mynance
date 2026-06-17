import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Receipt } from "lucide-react"
import { useState } from "react"
import { PeriodSelector } from "@/components/Common/PeriodSelector"
import { BalanceBlock, Card } from "@/components/morbido"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import {
  type CategoriaSpesa,
  MovimentiService,
  RiepilogoService,
} from "@/lib/api"
import { formatDateIt, formatEurFromCents } from "@/lib/format"
import { type Period, periodLabel, todayIso } from "@/lib/periodo"

export const Route = createFileRoute("/_layout/")({
  component: Home,
  head: () => ({
    meta: [{ title: "Home - mynance" }],
  }),
})

function Home() {
  const [period, setPeriod] = useState<Period>("month")
  const [anchor, setAnchor] = useState(todayIso())
  const [drill, setDrill] = useState<CategoriaSpesa | null>(null)

  const { data: bilancio, isPending } = useQuery({
    queryKey: ["bilancio", period, anchor],
    queryFn: () => RiepilogoService.bilancio({ anchor, period }),
  })

  const max = bilancio?.spese_per_categoria[0]?.total_cents ?? 0

  return (
    <div className="flex flex-col gap-6">
      <PeriodSelector
        period={period}
        anchor={anchor}
        onChange={(n) => {
          setPeriod(n.period)
          setAnchor(n.anchor)
        }}
      />

      {isPending || !bilancio ? (
        <Skeleton className="h-28 w-full rounded-card" />
      ) : (
        <>
          <BalanceBlock
            label={`NETTO · ${periodLabel(period, anchor).toUpperCase()}`}
            cents={bilancio.netto_cents}
          />
          <div className="grid grid-cols-2 gap-3">
            <Card className="p-4">
              <p className="type-eyebrow">Entrate</p>
              <p className="type-h2 tabular-nums text-positive-ink">
                {formatEurFromCents(bilancio.entrate_cents)}
              </p>
            </Card>
            <Card className="p-4">
              <p className="type-eyebrow">Spese</p>
              <p className="type-h2 tabular-nums text-ink">
                {formatEurFromCents(bilancio.spese_cents)}
              </p>
            </Card>
          </div>
        </>
      )}

      <section className="flex flex-col gap-3">
        <h2 className="type-eyebrow">Spese per categoria</h2>
        {isPending || !bilancio ? (
          <div className="flex flex-col gap-2">
            <Skeleton className="h-12 w-full" />
            <Skeleton className="h-12 w-full" />
          </div>
        ) : bilancio.spese_per_categoria.length === 0 ? (
          <Card className="flex flex-col items-center gap-3 py-12 text-center">
            <span aria-hidden="true" className="text-ink-soft">
              <Receipt className="h-7 w-7" />
            </span>
            <p className="type-body text-ink-soft">
              Ancora nessuna spesa in questo periodo.
            </p>
          </Card>
        ) : (
          <ul className="flex flex-col gap-2">
            {bilancio.spese_per_categoria.map((c) => (
              <li key={c.categoria_id}>
                <button
                  type="button"
                  onClick={() => setDrill(c)}
                  data-tap-target
                  className="flex w-full min-h-11 flex-col gap-2 rounded-card bg-surface px-4 py-3 text-left outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="type-body text-ink">{c.nome}</span>
                    <span className="type-body tabular-nums text-ink">
                      {formatEurFromCents(c.total_cents)}
                    </span>
                  </div>
                  <div
                    className="h-2 rounded-pill bg-surface-2"
                    aria-hidden="true"
                  >
                    <div
                      className="h-2 rounded-pill bg-accent-soft"
                      style={{
                        width: `${max > 0 ? Math.round((c.total_cents / max) * 100) : 0}%`,
                      }}
                    />
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <CategoriaDrillDown
        categoria={drill}
        start={bilancio?.start}
        end={bilancio?.end}
        onClose={() => setDrill(null)}
      />
    </div>
  )
}

function CategoriaDrillDown({
  categoria,
  start,
  end,
  onClose,
}: {
  categoria: CategoriaSpesa | null
  start?: string
  end?: string
  onClose: () => void
}) {
  const { data: movimenti, isPending } = useQuery({
    queryKey: ["movimenti", categoria?.categoria_id, start, end],
    queryFn: () =>
      MovimentiService.listMovimenti({
        categoriaId: categoria?.categoria_id,
        start,
        end,
      }),
    enabled: categoria !== null && !!start && !!end,
  })

  return (
    <Sheet open={categoria !== null} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="rounded-t-panel">
        <SheetHeader>
          <SheetTitle>{categoria?.nome ?? "Categoria"}</SheetTitle>
          <SheetDescription>Spese del periodo selezionato.</SheetDescription>
        </SheetHeader>
        <div className="px-4 pb-6">
          {isPending ? (
            <Skeleton className="h-24 w-full" />
          ) : !movimenti || movimenti.length === 0 ? (
            <p className="type-body text-ink-soft">Nessuna spesa.</p>
          ) : (
            <ul className="flex flex-col divide-y divide-border">
              {movimenti.map((m) => (
                <li
                  key={m.id}
                  className="flex items-center justify-between gap-3 py-3"
                >
                  <div className="flex flex-col">
                    <span className="type-body text-ink">
                      {formatDateIt(m.data)}
                    </span>
                    {m.note ? (
                      <span className="type-caption text-ink-soft">
                        {m.note}
                      </span>
                    ) : null}
                  </div>
                  <span className="type-body tabular-nums text-ink">
                    {formatEurFromCents(m.amount_cents)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}
