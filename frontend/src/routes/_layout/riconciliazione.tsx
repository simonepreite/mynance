import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"

import { BalanceBlock, Card, HonestyBanner } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import { type RiconciliazioneEsito, RiconciliazioneService } from "@/lib/api"
import { formatDateIt, formatEurFromCents } from "@/lib/format"
import { parseEurToCents } from "@/lib/money"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/riconciliazione")({
  component: Riconciliazione,
  head: () => ({ meta: [{ title: "Riconciliazione - mynance" }] }),
})

const ESITO_LABELS: Record<string, string> = {
  chiusa: "Chiusa",
  acknowledged_open: "Lasciata aperta",
}

function Riconciliazione() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [reale, setReale] = useState("")

  const cents = parseEurToCents(reale)
  const realeValid = cents !== null && cents >= 0

  const { data: preview, isFetching } = useQuery({
    queryKey: ["anteprima", cents],
    queryFn: () =>
      RiconciliazioneService.anteprima({
        requestBody: { liquidita_reale_cents: cents ?? 0 },
      }),
    enabled: realeValid,
  })

  const { data: storico } = useQuery({
    queryKey: ["riconciliazioni"],
    queryFn: () => RiconciliazioneService.history(),
  })

  const mutation = useMutation({
    mutationFn: (esito: RiconciliazioneEsito) =>
      RiconciliazioneService.confirm({
        requestBody: { liquidita_reale_cents: cents ?? 0, esito },
      }),
    onSuccess: (_data, esito) => {
      showSuccessToast(
        esito === "chiusa"
          ? "Scostamento chiuso. Liquidità riallineata."
          : "Riconciliazione registrata.",
      )
      setReale("")
      for (const key of [
        "liquidita",
        "promemoria",
        "riconciliazioni",
        "bilancio",
        "allocazione",
        "secchielli",
        "movimenti",
      ]) {
        queryClient.invalidateQueries({ queryKey: [key] })
      }
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const drift = preview?.drift_cents ?? 0

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="type-h1 text-ink">Riconciliazione</h1>
        <p className="type-body text-ink-soft">
          Confronta la liquidità calcolata con quella reale e allinea i conti.
        </p>
      </div>

      <BalanceBlock
        label="LIQUIDITÀ CALCOLATA"
        cents={preview?.liquidita_calcolata_cents ?? 0}
      />

      <Card className="flex flex-col gap-3">
        <div className="flex flex-col gap-1">
          <label htmlFor="reale" className="type-eyebrow">
            Liquidità reale (€)
          </label>
          <Input
            id="reale"
            inputMode="decimal"
            placeholder="Quanto hai davvero, es. 1.234,56"
            value={reale}
            onChange={(e) => setReale(e.target.value)}
            data-testid="reale-input"
          />
        </div>

        {realeValid && preview ? (
          <div className="flex flex-col gap-2">
            <p className="type-body text-ink">
              Scostamento:{" "}
              <span className="font-medium text-honesty tabular-nums">
                {drift < 0 ? "−" : "+"}
                {formatEurFromCents(Math.abs(drift))}
              </span>
              {preview.drift_percent !== null
                ? ` (${preview.drift_percent > 0 ? "+" : ""}${preview.drift_percent}%)`
                : ""}{" "}
              rispetto al calcolato
            </p>
            {drift !== 0 ? (
              <HonestyBanner>
                {drift < 0
                  ? "Hai meno del calcolato: chiudendo creo una Spesa «non identificato»."
                  : "Hai più del calcolato: chiudendo creo un'Entrata «non identificato»."}
              </HonestyBanner>
            ) : (
              <p className="type-caption text-ink-soft">
                Nessuno scostamento: i conti sono allineati.
              </p>
            )}
            <div className="flex flex-wrap gap-2">
              <LoadingButton
                loading={mutation.isPending}
                disabled={isFetching}
                onClick={() => mutation.mutate("chiusa")}
                data-testid="chiudi"
              >
                Chiudi lo scostamento
              </LoadingButton>
              <Button
                variant="ghost"
                disabled={mutation.isPending}
                onClick={() => mutation.mutate("acknowledged_open")}
              >
                Lascia aperto
              </Button>
            </div>
          </div>
        ) : null}
      </Card>

      <section className="flex flex-col gap-3">
        <h2 className="type-eyebrow">Storico riconciliazioni</h2>
        {storico === undefined ? (
          <Skeleton className="h-20 w-full" />
        ) : storico.length === 0 ? (
          <Card className="py-8 text-center">
            <p className="type-body text-ink-soft">
              Nessuna riconciliazione ancora.
            </p>
          </Card>
        ) : (
          <ul className="flex flex-col gap-2">
            {storico.map((r) => (
              <li key={r.id}>
                <Card className="flex items-center justify-between gap-3 p-4">
                  <div className="flex flex-col">
                    <span className="type-body text-ink">
                      {formatDateIt(r.data_riconciliazione)}
                    </span>
                    <span className="type-caption text-ink-soft">
                      {ESITO_LABELS[r.esito] ?? r.esito} · reale{" "}
                      {formatEurFromCents(r.liquidita_reale_cents)} · calcolata{" "}
                      {formatEurFromCents(r.liquidita_calcolata_cents)}
                    </span>
                  </div>
                  <span className="type-body tabular-nums text-honesty">
                    {r.drift_cents < 0 ? "−" : "+"}
                    {formatEurFromCents(Math.abs(r.drift_cents))}
                    {r.drift_percent !== null ? ` (${r.drift_percent}%)` : ""}
                  </span>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
