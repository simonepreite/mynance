import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Plus, Trash2 } from "lucide-react"
import { useState } from "react"

import { Card } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import {
  CategorieService,
  PatrimonioService,
  RegoleRicorrentiService,
} from "@/lib/api"
import { formatEurFromCents } from "@/lib/format"
import { parseEurToCents } from "@/lib/money"
import { todayIso } from "@/lib/periodo"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/regole")({
  component: Regole,
  head: () => ({ meta: [{ title: "Regole ricorrenti - mynance" }] }),
})

const PERIODICITA: Record<string, string> = {
  monthly: "Mensile",
  quarterly: "Trimestrale",
  semiannual: "Semestrale",
  annual: "Annuale",
  custom: "Personalizzata",
}

function Regole() {
  const [open, setOpen] = useState(false)
  const { data } = useQuery({
    queryKey: ["regole"],
    queryFn: () => RegoleRicorrentiService.listRegole(),
  })
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const del = useMutation({
    mutationFn: (id: string) =>
      RegoleRicorrentiService.deleteRegola({ regolaId: id }),
    onSuccess: () => showSuccessToast("Regola eliminata"),
    onError: handleError.bind(showErrorToast),
    onSettled: () => queryClient.invalidateQueries({ queryKey: ["regole"] }),
  })

  const regole = data?.items ?? []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="type-h1 text-ink">Regole ricorrenti</h1>
          <p className="type-body text-ink-soft">
            Automatizza entrate e versamenti PAC prevedibili.
          </p>
        </div>
        <Button onClick={() => setOpen(true)} data-testid="add-regola">
          <Plus className="mr-1 h-4 w-4" />
          Nuova
        </Button>
      </div>

      <p className="type-caption text-ink-soft">
        Gli elementi vengono creati automaticamente solo fino a oggi (nessun
        movimento futuro), e restano modificabili e saltabili: saltarne uno non
        crea scostamenti.
      </p>

      {data === undefined ? (
        <Skeleton className="h-20 w-full" />
      ) : regole.length === 0 ? (
        <Card className="py-12 text-center">
          <p className="type-body text-ink-soft">
            Nessuna regola. Creane una per ciò che è prevedibile (stipendio,
            PAC) e riduci l'inserimento manuale.
          </p>
        </Card>
      ) : (
        <ul className="flex flex-col gap-2">
          {regole.map((r) => (
            <li key={r.id}>
              <Card className="flex items-center justify-between gap-2 p-4">
                <div className="flex flex-col">
                  <span className="type-body font-medium text-ink">
                    {formatEurFromCents(r.importo_cents)} ·{" "}
                    {r.kind === "entrata" ? "Entrata" : "Versamento PAC"}
                  </span>
                  <span className="type-caption text-ink-soft">
                    {PERIODICITA[r.periodicita] ?? r.periodicita} · giorno{" "}
                    {r.day_of_period}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="Elimina regola"
                  onClick={() => del.mutate(r.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <RegolaForm open={open} onClose={() => setOpen(false)} />
    </div>
  )
}

function RegolaForm({ open, onClose }: { open: boolean; onClose: () => void }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const [importo, setImporto] = useState("")
  const [periodicita, setPeriodicita] = useState("monthly")
  const [intervallo, setIntervallo] = useState("2")
  const [day, setDay] = useState("1")
  const [kind, setKind] = useState<"entrata" | "versamento_pac">("entrata")
  const [categoriaId, setCategoriaId] = useState("")
  const [investimentoId, setInvestimentoId] = useState("")
  const [startDate, setStartDate] = useState(todayIso())

  const { data: categorie } = useQuery({
    queryKey: ["categorie"],
    queryFn: () => CategorieService.listCategorie(),
    enabled: open,
  })
  const { data: investimenti } = useQuery({
    queryKey: ["investimenti"],
    queryFn: () => PatrimonioService.listInvestimenti(),
    enabled: open,
  })

  const cents = parseEurToCents(importo)
  const dayNum = Number(day)
  const valid =
    cents !== null &&
    cents > 0 &&
    Number.isInteger(dayNum) &&
    dayNum >= 1 &&
    dayNum <= 31 &&
    (kind === "entrata" ? categoriaId !== "" : investimentoId !== "")

  const mutation = useMutation({
    mutationFn: () =>
      RegoleRicorrentiService.createRegola({
        requestBody: {
          importo_cents: cents ?? 0,
          periodicita: periodicita as
            | "monthly"
            | "quarterly"
            | "semiannual"
            | "annual"
            | "custom",
          intervallo_mesi: periodicita === "custom" ? Number(intervallo) : null,
          day_of_period: dayNum,
          kind,
          categoria_id: kind === "entrata" ? categoriaId : null,
          investimento_id: kind === "versamento_pac" ? investimentoId : null,
          start_date: startDate,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Regola creata")
      setImporto("")
      onClose()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      for (const k of ["regole", "movimenti", "liquidita", "patrimonio"]) {
        queryClient.invalidateQueries({ queryKey: [k] })
      }
    },
  })

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="rounded-t-panel">
        <SheetHeader>
          <SheetTitle>Nuova regola ricorrente</SheetTitle>
        </SheetHeader>
        <div className="flex flex-col gap-3 px-4 pb-6">
          <Input
            inputMode="decimal"
            placeholder="Importo €, es. 1.500,00"
            value={importo}
            onChange={(e) => setImporto(e.target.value)}
          />
          <div className="flex gap-2">
            <Select
              value={kind}
              onValueChange={(v) => setKind(v as "entrata" | "versamento_pac")}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="entrata">Entrata</SelectItem>
                <SelectItem value="versamento_pac">Versamento PAC</SelectItem>
              </SelectContent>
            </Select>
            {kind === "entrata" ? (
              <Select value={categoriaId} onValueChange={setCategoriaId}>
                <SelectTrigger>
                  <SelectValue placeholder="Categoria" />
                </SelectTrigger>
                <SelectContent>
                  {(categorie?.entrata ?? []).map((c) => (
                    <SelectItem key={c.id} value={c.id}>
                      {c.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Select value={investimentoId} onValueChange={setInvestimentoId}>
                <SelectTrigger>
                  <SelectValue placeholder="Investimento" />
                </SelectTrigger>
                <SelectContent>
                  {(investimenti ?? []).map((i) => (
                    <SelectItem key={i.id} value={i.id}>
                      {i.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
          <div className="flex gap-2">
            <Select value={periodicita} onValueChange={setPeriodicita}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="monthly">Mensile</SelectItem>
                <SelectItem value="quarterly">Trimestrale</SelectItem>
                <SelectItem value="semiannual">Semestrale</SelectItem>
                <SelectItem value="annual">Annuale</SelectItem>
                <SelectItem value="custom">Personalizzata</SelectItem>
              </SelectContent>
            </Select>
            {periodicita === "custom" ? (
              <Input
                inputMode="numeric"
                className="max-w-28"
                aria-label="Intervallo mesi"
                value={intervallo}
                onChange={(e) => setIntervallo(e.target.value)}
              />
            ) : null}
          </div>
          <div className="flex items-center gap-2">
            <Input
              inputMode="numeric"
              className="max-w-28"
              aria-label="Giorno del periodo"
              value={day}
              onChange={(e) => setDay(e.target.value)}
            />
            <span className="type-caption text-ink-soft">
              giorno del periodo
            </span>
          </div>
          <Input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            aria-label="Data di inizio"
          />
          <LoadingButton
            loading={mutation.isPending}
            disabled={!valid}
            onClick={() => mutation.mutate()}
          >
            Crea regola
          </LoadingButton>
        </div>
      </SheetContent>
    </Sheet>
  )
}
