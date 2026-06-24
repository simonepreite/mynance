import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useRef, useState } from "react"

import { Chip } from "@/components/morbido"
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
import useCustomToast from "@/hooks/useCustomToast"
import {
  type CategoriaTipo,
  CategorieService,
  type LiquiditaPublic,
  MovimentiService,
} from "@/lib/api"
import { parseEurToCents } from "@/lib/money"

function todayIso(): string {
  const d = new Date()
  const month = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  return `${d.getFullYear()}-${month}-${day}`
}

type SaveVars = {
  tipo: CategoriaTipo
  amount_cents: number
  categoria_id: string
}

export function QuickAdd({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const [tipo, setTipo] = useState<CategoriaTipo>("spesa")
  const [amount, setAmount] = useState("")
  const [categoriaId, setCategoriaId] = useState<string | null>(null)
  const [note, setNote] = useState("")
  const amountRef = useRef<HTMLInputElement>(null)

  const { data: categorie } = useQuery({
    queryKey: ["categorie"],
    queryFn: () => CategorieService.listCategorie(),
    enabled: open,
  })
  const options =
    tipo === "spesa" ? (categorie?.spesa ?? []) : (categorie?.entrata ?? [])

  const reset = () => {
    setAmount("")
    setCategoriaId(null)
    setTipo("spesa")
    setNote("")
  }

  const mutation = useMutation<
    unknown,
    Error,
    SaveVars,
    { prev?: LiquiditaPublic }
  >({
    mutationFn: (vars) =>
      MovimentiService.createMovimento({
        requestBody: {
          tipo: vars.tipo,
          amount_cents: vars.amount_cents,
          data: todayIso(),
          categoria_id: vars.categoria_id,
          note: note.trim() === "" ? undefined : note,
        },
      }),
    onMutate: async (vars) => {
      // Optimistic: move derived Liquidità immediately (server reconciles on
      // settle). Spesa subtracts, Entrata adds.
      await queryClient.cancelQueries({ queryKey: ["liquidita"] })
      const prev = queryClient.getQueryData<LiquiditaPublic>(["liquidita"])
      if (prev) {
        const delta =
          vars.tipo === "spesa" ? -vars.amount_cents : vars.amount_cents
        queryClient.setQueryData<LiquiditaPublic>(["liquidita"], {
          ...prev,
          value_cents: prev.value_cents + delta,
        })
      }
      return { prev }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev) {
        queryClient.setQueryData(["liquidita"], ctx.prev)
      }
      showErrorToast("Non sono riuscito a salvare il movimento. Riprova.")
    },
    onSuccess: (_data, vars) => {
      showSuccessToast(
        vars.tipo === "spesa" ? "Spesa aggiunta" : "Entrata aggiunta",
      )
      reset()
      onOpenChange(false)
    },
    onSettled: () => {
      // Derived figures always come from the server (API-3): never trust the
      // optimistic value past the round-trip.
      queryClient.invalidateQueries({ queryKey: ["liquidita"] })
      queryClient.invalidateQueries({ queryKey: ["movimenti"] })
      queryClient.invalidateQueries({ queryKey: ["bilancio"] })
      queryClient.invalidateQueries({ queryKey: ["statistiche"] })
    },
  })

  const cents = parseEurToCents(amount)
  const canSave =
    cents !== null && cents > 0 && categoriaId !== null && !mutation.isPending

  const submit = () => {
    if (cents === null || cents <= 0 || categoriaId === null) return
    mutation.mutate({ tipo, amount_cents: cents, categoria_id: categoriaId })
  }

  const selectTipo = (next: CategoriaTipo) => {
    setTipo(next)
    setCategoriaId(null) // a Categoria is type-scoped; clear on switch
  }

  return (
    <Sheet
      open={open}
      onOpenChange={(o) => {
        onOpenChange(o)
        if (!o) reset()
      }}
    >
      <SheetContent
        side="bottom"
        className="rounded-t-panel"
        onOpenAutoFocus={(e) => {
          // Amount-first capture (UX-DR4): focus the amount, not the first chip.
          e.preventDefault()
          amountRef.current?.focus()
        }}
      >
        <SheetHeader>
          <SheetTitle>Aggiungi un movimento</SheetTitle>
          <SheetDescription>
            Inserisci l'importo e scegli una categoria.
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-5 px-4 pb-6">
          <fieldset className="m-0 flex gap-2 border-0 p-0">
            <legend className="sr-only">Tipo di movimento</legend>
            <Chip
              selected={tipo === "spesa"}
              onClick={() => selectTipo("spesa")}
              className="flex-1"
            >
              Spesa
            </Chip>
            <Chip
              selected={tipo === "entrata"}
              onClick={() => selectTipo("entrata")}
              className="flex-1"
            >
              Entrata
            </Chip>
          </fieldset>

          <div className="flex flex-col gap-1">
            <label htmlFor="quick-add-amount" className="type-eyebrow">
              Importo
            </label>
            <div className="flex items-center gap-2">
              <span aria-hidden="true" className="type-h2 text-ink-soft">
                €
              </span>
              <Input
                ref={amountRef}
                id="quick-add-amount"
                inputMode="decimal"
                placeholder="0,00"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                data-testid="quick-add-amount"
                className="text-lg"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2">
            <span className="type-eyebrow">Categoria</span>
            {options.length === 0 ? (
              <p className="type-caption text-ink-soft">
                Nessuna categoria di {tipo === "spesa" ? "spesa" : "entrata"}.
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {options.map((c) => (
                  <Chip
                    key={c.id}
                    selected={categoriaId === c.id}
                    onClick={() => setCategoriaId(c.id)}
                  >
                    {c.nome}
                  </Chip>
                ))}
              </div>
            )}
          </div>

          <Input
            placeholder="Nota (facoltativa)"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            data-testid="quick-add-note"
          />

          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => onOpenChange(false)}>
              Annulla
            </Button>
            <LoadingButton
              onClick={submit}
              disabled={!canSave}
              loading={mutation.isPending}
              data-testid="quick-add-save"
            >
              Salva
            </LoadingButton>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
