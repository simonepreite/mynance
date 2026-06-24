import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Pencil, Receipt, Trash2 } from "lucide-react"
import { useState } from "react"
import { PeriodSelector } from "@/components/Common/PeriodSelector"
import { BalanceBlock, Card } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import {
  type CategoriaSpesa,
  MovimentiService,
  type MovimentoPublic,
  RiepilogoService,
} from "@/lib/api"
import { formatDateIt, formatEurFromCents } from "@/lib/format"
import { parseEurToCents } from "@/lib/money"
import { type Period, periodLabel, todayIso } from "@/lib/periodo"
import { handleError } from "@/utils"

const MOV_KEYS = [
  "movimenti",
  "bilancio",
  "liquidita",
  "allocazione",
  "patrimonio",
]

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
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [editing, setEditing] = useState<MovimentoPublic | null>(null)

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

  const invalidate = () => {
    for (const k of MOV_KEYS) queryClient.invalidateQueries({ queryKey: [k] })
  }

  const del = useMutation({
    mutationFn: (id: string) =>
      MovimentiService.deleteMovimento({ movimentoId: id }),
    onSuccess: () => showSuccessToast("Spesa eliminata"),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  return (
    <>
      <Sheet open={categoria !== null} onOpenChange={(o) => !o && onClose()}>
        <SheetContent side="bottom" className="rounded-t-panel">
          <SheetHeader>
            <SheetTitle>{categoria?.nome ?? "Categoria"}</SheetTitle>
            <SheetDescription>Spese del periodo selezionato.</SheetDescription>
          </SheetHeader>
          <div className="px-4 pb-6">
            {categoria?.sottocategorie?.length ? (
              <ul className="mb-3 flex flex-col gap-1">
                {categoria.sottocategorie.map((s) => (
                  <li
                    key={`${s.categoria_id}-${s.nome}`}
                    className="flex justify-between type-caption text-ink-soft"
                  >
                    <span>{s.nome}</span>
                    <span className="tabular-nums">
                      {formatEurFromCents(s.total_cents)}
                    </span>
                  </li>
                ))}
              </ul>
            ) : null}
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
                    <div className="flex items-center gap-1">
                      <span className="type-body tabular-nums text-ink">
                        {formatEurFromCents(m.amount_cents)}
                      </span>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label="Modifica spesa"
                        onClick={() => setEditing(m)}
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        aria-label="Elimina spesa"
                        onClick={() => del.mutate(m.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </SheetContent>
      </Sheet>
      <EditMovimento
        movimento={editing}
        onClose={() => setEditing(null)}
        onSaved={invalidate}
      />
    </>
  )
}

function EditMovimento({
  movimento,
  onClose,
  onSaved,
}: {
  movimento: MovimentoPublic | null
  onClose: () => void
  onSaved: () => void
}) {
  return (
    <Sheet open={movimento !== null} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="rounded-t-panel">
        <SheetHeader>
          <SheetTitle>Modifica spesa</SheetTitle>
        </SheetHeader>
        {movimento ? (
          <EditMovimentoForm
            key={movimento.id}
            movimento={movimento}
            onClose={onClose}
            onSaved={onSaved}
          />
        ) : null}
      </SheetContent>
    </Sheet>
  )
}

function EditMovimentoForm({
  movimento,
  onClose,
  onSaved,
}: {
  movimento: MovimentoPublic
  onClose: () => void
  onSaved: () => void
}) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [importo, setImporto] = useState(
    (movimento.amount_cents / 100).toFixed(2).replace(".", ","),
  )
  const [data, setData] = useState(movimento.data)
  const [note, setNote] = useState(movimento.note ?? "")
  const cents = parseEurToCents(importo)

  const mutation = useMutation({
    mutationFn: () =>
      MovimentiService.updateMovimento({
        movimentoId: movimento.id,
        requestBody: {
          amount_cents: cents ?? movimento.amount_cents,
          data,
          note: note.trim() === "" ? null : note,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Spesa aggiornata")
      onSaved()
      onClose()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="flex flex-col gap-3 px-4 pb-6">
      <Input
        inputMode="decimal"
        placeholder="Importo €"
        value={importo}
        onChange={(e) => setImporto(e.target.value)}
        aria-label="Importo"
      />
      <Input
        type="date"
        value={data}
        onChange={(e) => setData(e.target.value)}
        aria-label="Data"
      />
      <Input
        placeholder="Nota (facoltativa)"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        aria-label="Nota"
      />
      <LoadingButton
        loading={mutation.isPending}
        disabled={cents === null || cents <= 0}
        onClick={() => mutation.mutate()}
      >
        Salva
      </LoadingButton>
    </div>
  )
}
