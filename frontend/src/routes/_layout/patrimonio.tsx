import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, Link as RouterLink } from "@tanstack/react-router"
import { Plus, Trash2 } from "lucide-react"
import { useState } from "react"

import { BalanceBlock, Card } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { type InvestimentoPublic, PatrimonioService } from "@/lib/api"
import { formatEurFromCents } from "@/lib/format"
import { parseEurToCents } from "@/lib/money"
import { todayIso } from "@/lib/periodo"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/patrimonio")({
  component: Patrimonio,
  head: () => ({ meta: [{ title: "Patrimonio - mynance" }] }),
})

function useInvalidatePatrimonio() {
  const qc = useQueryClient()
  return () => {
    for (const k of [
      "patrimonio",
      "liquidita",
      "investimenti",
      "immobili",
      "mobili",
    ]) {
      qc.invalidateQueries({ queryKey: [k] })
    }
  }
}

function Patrimonio() {
  const { data, isPending } = useQuery({
    queryKey: ["patrimonio"],
    queryFn: () => PatrimonioService.patrimonio(),
  })

  return (
    <div className="flex flex-col gap-6">
      <h1 className="type-h1 text-ink">Patrimonio</h1>

      {isPending || !data ? (
        <Skeleton className="h-28 w-full rounded-card" />
      ) : (
        <>
          <BalanceBlock label="PATRIMONIO TOTALE" cents={data.totale_cents} />
          <div className="grid grid-cols-2 gap-3">
            <RouterLink to="/liquidita">
              <Card className="p-4">
                <p className="type-eyebrow">Liquidità</p>
                <p className="type-h2 tabular-nums text-ink">
                  {formatEurFromCents(data.liquidita_cents)}
                </p>
              </Card>
            </RouterLink>
            <Card className="p-4">
              <p className="type-eyebrow">Investimenti (capitale versato)</p>
              <p className="type-h2 tabular-nums text-ink">
                {formatEurFromCents(data.capitale_versato_cents)}
              </p>
            </Card>
            <Card className="p-4">
              <p className="type-eyebrow">Beni immobili</p>
              <p className="type-h2 tabular-nums text-ink">
                {formatEurFromCents(data.beni_immobili_cents)}
              </p>
            </Card>
            <Card className="p-4">
              <p className="type-eyebrow">Beni mobili</p>
              <p className="type-h2 tabular-nums text-ink">
                {formatEurFromCents(data.beni_mobili_cents)}
              </p>
            </Card>
          </div>
          <p className="type-caption text-ink-soft">
            Registrare un bene non tocca la liquidità: la spesa per l'acquisto
            va registrata a parte.
          </p>
        </>
      )}

      <InvestimentiSection />
      <ImmobiliSection />
      <MobiliSection />
    </div>
  )
}

// --- Investimenti ----------------------------------------------------------

function InvestimentiSection() {
  const invalidate = useInvalidatePatrimonio()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [nome, setNome] = useState("")
  const [versamentoFor, setVersamentoFor] = useState<InvestimentoPublic | null>(
    null,
  )

  const { data } = useQuery({
    queryKey: ["investimenti"],
    queryFn: () => PatrimonioService.listInvestimenti(),
  })

  const createInv = useMutation({
    mutationFn: () =>
      PatrimonioService.createInvestimento({ requestBody: { nome } }),
    onSuccess: () => {
      showSuccessToast("Investimento creato")
      setNome("")
    },
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  const delInv = useMutation({
    mutationFn: (id: string) =>
      PatrimonioService.deleteInvestimento({ investimentoId: id }),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  return (
    <section className="flex flex-col gap-3">
      <h2 className="type-eyebrow">Investimenti (PAC)</h2>
      <div className="flex gap-2">
        <Input
          placeholder="Nome (es. ETF World)"
          value={nome}
          onChange={(e) => setNome(e.target.value)}
        />
        <LoadingButton
          loading={createInv.isPending}
          disabled={nome.trim().length === 0}
          onClick={() => createInv.mutate()}
        >
          <Plus className="mr-1 h-4 w-4" />
          Aggiungi
        </LoadingButton>
      </div>
      {data && data.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {data.map((inv) => (
            <li key={inv.id}>
              <Card className="flex items-center justify-between gap-2 p-4">
                <div className="flex flex-col">
                  <span className="type-body text-ink">{inv.nome}</span>
                  <span className="type-caption text-ink-soft">
                    Capitale versato:{" "}
                    {formatEurFromCents(inv.capitale_versato_cents)}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="outline"
                    onClick={() => setVersamentoFor(inv)}
                  >
                    Versa
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Elimina ${inv.nome}`}
                    onClick={() => delInv.mutate(inv.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      ) : null}
      <VersamentoSheet
        investimento={versamentoFor}
        onClose={() => setVersamentoFor(null)}
      />
    </section>
  )
}

function VersamentoSheet({
  investimento,
  onClose,
}: {
  investimento: InvestimentoPublic | null
  onClose: () => void
}) {
  const invalidate = useInvalidatePatrimonio()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [importo, setImporto] = useState("")
  const cents = parseEurToCents(importo)

  const mutation = useMutation({
    mutationFn: () =>
      PatrimonioService.createVersamento({
        investimentoId: investimento?.id ?? "",
        requestBody: { importo_cents: cents ?? 0, data: todayIso() },
      }),
    onSuccess: () => {
      showSuccessToast("Versamento registrato")
      setImporto("")
      onClose()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  return (
    <Sheet open={investimento !== null} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="rounded-t-panel">
        <SheetHeader>
          <SheetTitle>Versamento — {investimento?.nome}</SheetTitle>
        </SheetHeader>
        <div className="flex flex-col gap-3 px-4 pb-6">
          <Input
            inputMode="decimal"
            placeholder="Importo €, es. 200,00"
            value={importo}
            onChange={(e) => setImporto(e.target.value)}
          />
          <p className="type-caption text-ink-soft">
            Il versamento riduce la liquidità dello stesso importo.
          </p>
          <LoadingButton
            loading={mutation.isPending}
            disabled={cents === null || cents <= 0}
            onClick={() => mutation.mutate()}
          >
            Registra versamento
          </LoadingButton>
        </div>
      </SheetContent>
    </Sheet>
  )
}

// --- Beni immobili ---------------------------------------------------------

function ImmobiliSection() {
  const invalidate = useInvalidatePatrimonio()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [open, setOpen] = useState(false)
  const [nome, setNome] = useState("")
  const [prezzo, setPrezzo] = useState("")
  const cents = parseEurToCents(prezzo)

  const { data } = useQuery({
    queryKey: ["immobili"],
    queryFn: () => PatrimonioService.listImmobili(),
  })

  const create = useMutation({
    mutationFn: () =>
      PatrimonioService.createImmobile({
        requestBody: { nome, prezzo_cents: cents ?? 0 },
      }),
    onSuccess: () => {
      showSuccessToast("Bene immobile registrato")
      setNome("")
      setPrezzo("")
      setOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  const del = useMutation({
    mutationFn: (id: string) =>
      PatrimonioService.deleteImmobile({ beneId: id }),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="type-eyebrow">Beni immobili</h2>
        <Button variant="outline" onClick={() => setOpen(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Aggiungi
        </Button>
      </div>
      {data && data.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {data.map((b) => (
            <li key={b.id}>
              <Card className="flex items-center justify-between gap-2 p-4">
                <span className="type-body text-ink">{b.nome}</span>
                <div className="flex items-center gap-2">
                  <span className="type-body tabular-nums text-ink">
                    {formatEurFromCents(b.prezzo_cents)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Elimina ${b.nome}`}
                    onClick={() => del.mutate(b.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      ) : null}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="bottom" className="rounded-t-panel">
          <SheetHeader>
            <SheetTitle>Nuovo bene immobile</SheetTitle>
          </SheetHeader>
          <div className="flex flex-col gap-3 px-4 pb-6">
            <Input
              placeholder="Nome (es. Casa)"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
            />
            <Input
              inputMode="decimal"
              placeholder="Prezzo pagato €"
              value={prezzo}
              onChange={(e) => setPrezzo(e.target.value)}
            />
            <LoadingButton
              loading={create.isPending}
              disabled={
                nome.trim().length === 0 || cents === null || cents <= 0
              }
              onClick={() => create.mutate()}
            >
              Registra
            </LoadingButton>
          </div>
        </SheetContent>
      </Sheet>
    </section>
  )
}

// --- Beni mobili -----------------------------------------------------------

const SVAL_PRESETS = [
  { label: "Auto (18%)", value: 18 },
  { label: "Moto (10%)", value: 10 },
]

function MobiliSection() {
  const invalidate = useInvalidatePatrimonio()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [open, setOpen] = useState(false)
  const [nome, setNome] = useState("")
  const [prezzo, setPrezzo] = useState("")
  const [data_acquisto, setData] = useState(todayIso())
  const [sval, setSval] = useState("18")
  const cents = parseEurToCents(prezzo)
  const svalNum = Number(sval)
  const svalValid = Number.isFinite(svalNum) && svalNum >= 0 && svalNum <= 100

  const { data } = useQuery({
    queryKey: ["mobili"],
    queryFn: () => PatrimonioService.listMobili(),
  })

  const create = useMutation({
    mutationFn: () =>
      PatrimonioService.createMobile({
        requestBody: {
          nome,
          prezzo_cents: cents ?? 0,
          data_acquisto,
          svalutazione_percentuale: svalNum,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Bene mobile registrato")
      setNome("")
      setPrezzo("")
      setOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  const del = useMutation({
    mutationFn: (id: string) => PatrimonioService.deleteMobile({ beneId: id }),
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  return (
    <section className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="type-eyebrow">Beni mobili</h2>
        <Button variant="outline" onClick={() => setOpen(true)}>
          <Plus className="mr-1 h-4 w-4" />
          Aggiungi
        </Button>
      </div>
      {data && data.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {data.map((b) => (
            <li key={b.id}>
              <Card className="flex items-center justify-between gap-2 p-4">
                <div className="flex flex-col">
                  <span className="type-body text-ink">{b.nome}</span>
                  <span className="type-caption text-ink-soft">
                    Acquisto {formatEurFromCents(b.prezzo_cents)} ·{" "}
                    {b.svalutazione_percentuale}%/anno
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="type-body tabular-nums text-ink">
                    {formatEurFromCents(b.valore_cents)}
                  </span>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Elimina ${b.nome}`}
                    onClick={() => del.mutate(b.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      ) : null}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetContent side="bottom" className="rounded-t-panel">
          <SheetHeader>
            <SheetTitle>Nuovo bene mobile</SheetTitle>
          </SheetHeader>
          <div className="flex flex-col gap-3 px-4 pb-6">
            <Input
              placeholder="Nome (es. Auto)"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
            />
            <Input
              inputMode="decimal"
              placeholder="Prezzo d'acquisto €"
              value={prezzo}
              onChange={(e) => setPrezzo(e.target.value)}
            />
            <Input
              type="date"
              value={data_acquisto}
              onChange={(e) => setData(e.target.value)}
            />
            <div className="flex flex-wrap items-center gap-2">
              <Input
                inputMode="decimal"
                className="max-w-28"
                value={sval}
                onChange={(e) => setSval(e.target.value)}
                aria-label="Svalutazione % annua"
              />
              <span className="type-caption text-ink-soft">%/anno</span>
              {SVAL_PRESETS.map((p) => (
                <Button
                  key={p.value}
                  type="button"
                  variant="ghost"
                  onClick={() => setSval(String(p.value))}
                >
                  {p.label}
                </Button>
              ))}
            </div>
            <LoadingButton
              loading={create.isPending}
              disabled={
                nome.trim().length === 0 ||
                cents === null ||
                cents <= 0 ||
                !svalValid
              }
              onClick={() => create.mutate()}
            >
              Registra
            </LoadingButton>
          </div>
        </SheetContent>
      </Sheet>
    </section>
  )
}
