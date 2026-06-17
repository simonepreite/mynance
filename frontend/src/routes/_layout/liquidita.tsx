import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Pencil, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { BalanceBlock, Card, HonestyBanner } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
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
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useCustomToast from "@/hooks/useCustomToast"
import {
  CategorieService,
  LiquiditaService,
  SecchielliService,
  type SecchielloPublic,
} from "@/lib/api"
import { formatDateIt, formatEurFromCents } from "@/lib/format"
import { parseEurToCents } from "@/lib/money"
import { todayIso } from "@/lib/periodo"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/liquidita")({
  component: Liquidita,
  head: () => ({ meta: [{ title: "Liquidità - mynance" }] }),
})

const PERIODICITA_LABELS: Record<string, string> = {
  monthly: "Mensile",
  quarterly: "Trimestrale",
  semiannual: "Semestrale",
  annual: "Annuale",
  custom: "Personalizzata",
}

function Liquidita() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="type-h1 text-ink">Liquidità</h1>
      <Tabs defaultValue="allocazione">
        <TabsList>
          <TabsTrigger value="allocazione">Allocazione</TabsTrigger>
          <TabsTrigger value="secchielli">Secchielli</TabsTrigger>
        </TabsList>
        <TabsContent value="allocazione" className="mt-4">
          <AllocazioneTab />
        </TabsContent>
        <TabsContent value="secchielli" className="mt-4">
          <SecchielliTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}

function AllocazioneTab() {
  const { data, isPending } = useQuery({
    queryKey: ["allocazione"],
    queryFn: () => LiquiditaService.allocazione({}),
  })

  if (isPending || !data) {
    return <Skeleton className="h-48 w-full rounded-card" />
  }

  return (
    <div className="flex flex-col gap-4">
      <BalanceBlock label="LIQUIDITÀ TOTALE" cents={data.liquidita_cents} />
      <div className="grid grid-cols-2 gap-3">
        <Card className="p-4">
          <p className="type-eyebrow">Allocata nei secchielli</p>
          <p className="type-h2 tabular-nums text-ink">
            {formatEurFromCents(data.liquidita_allocata_cents)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="type-eyebrow">Risparmio libero</p>
          <p className="type-h2 tabular-nums text-ink">
            {formatEurFromCents(data.risparmio_libero_cents)}
          </p>
        </Card>
      </div>

      <Card className="flex flex-col gap-2">
        <p className="type-eyebrow">
          Cuscinetto di sicurezza ({data.mesi_cuscinetto} mesi)
        </p>
        <p className="type-body text-ink-soft">
          Obiettivo:{" "}
          <span className="font-medium text-ink">
            {formatEurFromCents(data.cuscinetto_cents)}
          </span>{" "}
          (spesa media mensile{" "}
          {formatEurFromCents(data.spesa_media_mensile_cents)})
        </p>
        {data.sotto_cuscinetto ? (
          <HonestyBanner>
            Risparmio libero sotto il Cuscinetto di sicurezza (
            {data.mesi_cuscinetto} mesi).
          </HonestyBanner>
        ) : (
          <p className="type-caption text-ink-soft">
            Il risparmio libero copre il cuscinetto. ✓
          </p>
        )}
      </Card>
    </div>
  )
}

function SecchielliTab() {
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<SecchielloPublic | null>(null)
  const [paying, setPaying] = useState<SecchielloPublic | null>(null)

  const { data: secchielli, isPending } = useQuery({
    queryKey: ["secchielli"],
    queryFn: () => SecchielliService.listSecchielli(),
  })

  const openCreate = () => {
    setEditing(null)
    setFormOpen(true)
  }
  const openEdit = (s: SecchielloPublic) => {
    setEditing(s)
    setFormOpen(true)
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex justify-end">
        <Button onClick={openCreate} data-testid="add-secchiello">
          <Plus className="mr-2" />
          Nuovo secchiello
        </Button>
      </div>

      {isPending || !secchielli ? (
        <div className="flex flex-col gap-2">
          <Skeleton className="h-20 w-full" />
          <Skeleton className="h-20 w-full" />
        </div>
      ) : secchielli.length === 0 ? (
        <Card className="py-12 text-center">
          <p className="type-body text-ink-soft">
            Nessun Secchiello. Crea il primo per mettere da parte in anticipo.
          </p>
        </Card>
      ) : (
        <ul className="flex flex-col gap-2">
          {secchielli.map((s) => (
            <li key={s.id}>
              <Card className="flex flex-col gap-2 p-4">
                <div className="flex items-center justify-between gap-2">
                  <span className="type-body font-medium text-ink">
                    {s.nome}
                  </span>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label={`Modifica ${s.nome}`}
                      onClick={() => openEdit(s)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <DeleteSecchiello secchiello={s} />
                  </div>
                </div>
                <div className="flex flex-wrap gap-x-6 gap-y-1 type-caption text-ink-soft">
                  <span>
                    Saldo:{" "}
                    <span
                      className={
                        s.saldo_cents < 0
                          ? "font-medium text-honesty"
                          : "font-medium text-ink"
                      }
                    >
                      {s.saldo_cents < 0 ? "−" : ""}
                      {formatEurFromCents(Math.abs(s.saldo_cents))}
                    </span>
                  </span>
                  <span>Quota/mese: {formatEurFromCents(s.quota_cents)}</span>
                  <span>Scadenza: {formatDateIt(s.prossima_scadenza)}</span>
                  <span>
                    {PERIODICITA_LABELS[s.periodicita] ?? s.periodicita}
                  </span>
                </div>
                {s.saldo_cents < 0 ? (
                  <HonestyBanner>
                    Secchiello in rosso di{" "}
                    {formatEurFromCents(Math.abs(s.saldo_cents))} — la Quota
                    salirà per recuperare.
                  </HonestyBanner>
                ) : null}
                <div className="flex justify-end">
                  <Button variant="outline" onClick={() => setPaying(s)}>
                    Registra pagamento
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <SecchielloForm
        open={formOpen}
        editing={editing}
        onClose={() => setFormOpen(false)}
      />
      <PagamentoSheet secchiello={paying} onClose={() => setPaying(null)} />
    </div>
  )
}

function PagamentoSheet({
  secchiello,
  onClose,
}: {
  secchiello: SecchielloPublic | null
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [importo, setImporto] = useState("")
  const [data, setData] = useState(todayIso())
  const [categoriaId, setCategoriaId] = useState("")

  const { data: categorie } = useQuery({
    queryKey: ["categorie"],
    queryFn: () => CategorieService.listCategorie(),
    enabled: secchiello !== null,
  })

  const cents = parseEurToCents(importo)
  const valid = cents !== null && cents > 0 && categoriaId !== ""

  const mutation = useMutation({
    mutationFn: () =>
      SecchielliService.registraPagamento({
        secchielloId: secchiello?.id ?? "",
        requestBody: {
          amount_cents: cents ?? 0,
          data,
          categoria_id: categoriaId,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Pagamento registrato: ciclo aggiornato.")
      setImporto("")
      setCategoriaId("")
      onClose()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      for (const k of [
        "secchielli",
        "liquidita",
        "allocazione",
        "bilancio",
        "movimenti",
      ]) {
        queryClient.invalidateQueries({ queryKey: [k] })
      }
    },
  })

  return (
    <Sheet open={secchiello !== null} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="rounded-t-panel">
        <SheetHeader>
          <SheetTitle>Registra pagamento — {secchiello?.nome}</SheetTitle>
          <SheetDescription>
            Crea la spesa collegata e fa avanzare la prossima scadenza.
          </SheetDescription>
        </SheetHeader>
        <div className="flex flex-col gap-3 px-4 pb-6">
          <Input
            inputMode="decimal"
            placeholder="Importo pagato €"
            value={importo}
            onChange={(e) => setImporto(e.target.value)}
          />
          <Input
            type="date"
            value={data}
            onChange={(e) => setData(e.target.value)}
            aria-label="Data del pagamento"
          />
          <Select value={categoriaId} onValueChange={setCategoriaId}>
            <SelectTrigger>
              <SelectValue placeholder="Categoria di spesa" />
            </SelectTrigger>
            <SelectContent>
              {(categorie?.spesa ?? []).map((c) => (
                <SelectItem key={c.id} value={c.id}>
                  {c.nome}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <LoadingButton
            loading={mutation.isPending}
            disabled={!valid}
            onClick={() => mutation.mutate()}
          >
            Registra pagamento
          </LoadingButton>
        </div>
      </SheetContent>
    </Sheet>
  )
}

const schema = z
  .object({
    nome: z.string().min(1, { message: "Inserisci un nome" }),
    importo: z
      .string()
      .min(1, { message: "Inserisci l'importo previsto" })
      .refine(
        (v) => {
          const c = parseEurToCents(v)
          return c !== null && c > 0
        },
        { message: "Importo non valido" },
      ),
    periodicita: z.enum([
      "monthly",
      "quarterly",
      "semiannual",
      "annual",
      "custom",
    ]),
    intervallo_mesi: z.string().optional(),
    prossima_scadenza: z
      .string()
      .min(1, { message: "Inserisci la prossima scadenza" }),
  })
  .refine(
    (d) =>
      d.periodicita !== "custom" ||
      (d.intervallo_mesi != null &&
        Number.isInteger(Number(d.intervallo_mesi)) &&
        Number(d.intervallo_mesi) >= 1),
    {
      message:
        "La periodicità personalizzata richiede un intervallo in mesi (≥1)",
      path: ["intervallo_mesi"],
    },
  )

type FormData = z.infer<typeof schema>

function SecchielloForm({
  open,
  editing,
  onClose,
}: {
  open: boolean
  editing: SecchielloPublic | null
  onClose: () => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: "onBlur",
    values: {
      nome: editing?.nome ?? "",
      importo: editing
        ? (editing.importo_previsto_cents / 100).toFixed(2).replace(".", ",")
        : "",
      periodicita:
        (editing?.periodicita as FormData["periodicita"]) ?? "monthly",
      intervallo_mesi: editing?.intervallo_mesi
        ? String(editing.intervallo_mesi)
        : "",
      prossima_scadenza: editing?.prossima_scadenza ?? "",
    },
  })
  const periodicita = form.watch("periodicita")

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["secchielli"] })
    queryClient.invalidateQueries({ queryKey: ["allocazione"] })
    queryClient.invalidateQueries({ queryKey: ["liquidita"] })
  }

  const mutation = useMutation({
    mutationFn: (values: FormData) => {
      const body = {
        nome: values.nome,
        importo_previsto_cents: parseEurToCents(values.importo) ?? 0,
        periodicita: values.periodicita,
        intervallo_mesi:
          values.periodicita === "custom"
            ? Number(values.intervallo_mesi)
            : null,
        prossima_scadenza: values.prossima_scadenza,
      }
      return editing
        ? SecchielliService.updateSecchiello({
            secchielloId: editing.id,
            requestBody: body,
          })
        : SecchielliService.createSecchiello({ requestBody: body })
    },
    onSuccess: () => {
      showSuccessToast(editing ? "Secchiello aggiornato" : "Secchiello creato")
      onClose()
    },
    onError: handleError.bind(showErrorToast),
    onSettled: invalidate,
  })

  return (
    <Sheet open={open} onOpenChange={(o) => !o && onClose()}>
      <SheetContent side="bottom" className="rounded-t-panel">
        <SheetHeader>
          <SheetTitle>
            {editing ? "Modifica secchiello" : "Nuovo secchiello"}
          </SheetTitle>
          <SheetDescription>
            Metti da parte in anticipo per una spesa ricorrente nota.
          </SheetDescription>
        </SheetHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
            className="grid gap-4 px-4 pb-6"
          >
            <FormField
              control={form.control}
              name="nome"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome</FormLabel>
                  <FormControl>
                    <Input placeholder="Es. Assicurazione auto" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="importo"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Importo previsto (€)</FormLabel>
                  <FormControl>
                    <Input inputMode="decimal" placeholder="0,00" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="periodicita"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Periodicità</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="monthly">Mensile</SelectItem>
                      <SelectItem value="quarterly">Trimestrale</SelectItem>
                      <SelectItem value="semiannual">Semestrale</SelectItem>
                      <SelectItem value="annual">Annuale</SelectItem>
                      <SelectItem value="custom">Personalizzata</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />
            {periodicita === "custom" ? (
              <FormField
                control={form.control}
                name="intervallo_mesi"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Intervallo (mesi)</FormLabel>
                    <FormControl>
                      <Input
                        inputMode="numeric"
                        placeholder="Es. 2"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            ) : null}
            <FormField
              control={form.control}
              name="prossima_scadenza"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Prossima scadenza</FormLabel>
                  <FormControl>
                    <Input type="date" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            {editing ? (
              <p className="type-caption text-ink-soft">
                Quota consigliata: {formatEurFromCents(editing.quota_cents)}
                /mese (calcolata automaticamente)
              </p>
            ) : null}
            <LoadingButton type="submit" loading={mutation.isPending}>
              {editing ? "Salva" : "Crea"}
            </LoadingButton>
          </form>
        </Form>
      </SheetContent>
    </Sheet>
  )
}

function DeleteSecchiello({ secchiello }: { secchiello: SecchielloPublic }) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const mutation = useMutation({
    mutationFn: () =>
      SecchielliService.deleteSecchiello({ secchielloId: secchiello.id }),
    onSuccess: () => showSuccessToast("Secchiello eliminato"),
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["secchielli"] })
      queryClient.invalidateQueries({ queryKey: ["allocazione"] })
    },
  })
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={`Elimina ${secchiello.nome}`}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      <Trash2 className="h-4 w-4" />
    </Button>
  )
}
