import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Receipt, X } from "lucide-react"
import { useState } from "react"

import { BalanceBlock, Card } from "@/components/morbido"
import { Button } from "@/components/ui/button"
import { LiquiditaService } from "@/lib/api"

const DISMISS_KEY = "mynance-onboarding-liquidita-dismissed"

function readDismissed() {
  try {
    return localStorage.getItem(DISMISS_KEY) === "1"
  } catch {
    return false
  }
}

export const Route = createFileRoute("/_layout/")({
  component: Home,
  head: () => ({
    meta: [
      {
        title: "Home - mynance",
      },
    ],
  }),
})

function currentMonthLabel() {
  // Display-only; the full period selector (Giorno/Settimana/Mese/Anno) arrives
  // with the Home "Mese" story (2.8). Here we just label the current month.
  const month = new Intl.DateTimeFormat("it-IT", { month: "long" }).format(
    new Date(),
  )
  return month.charAt(0).toUpperCase() + month.slice(1)
}

function Home() {
  const navigate = useNavigate()
  const [dismissed, setDismissed] = useState(readDismissed)

  const { data: liquidita } = useQuery({
    queryKey: ["liquidita"],
    queryFn: () => LiquiditaService.readLiquidita(),
  })

  const dismiss = () => {
    try {
      localStorage.setItem(DISMISS_KEY, "1")
    } catch {
      // storage may be unavailable; dismiss for this session regardless
    }
    setDismissed(true)
  }

  const showPrompt = liquidita
    ? !liquidita.iniziale_is_set && !dismissed
    : false

  return (
    <div className="flex flex-col gap-6">
      <div>
        <p className="type-eyebrow">Bilancio</p>
        <h1 className="type-h1 text-ink">{currentMonthLabel()}</h1>
      </div>

      <BalanceBlock label="LIQUIDITÀ" cents={liquidita?.value_cents ?? 0} />

      {showPrompt ? (
        <Card className="flex flex-col gap-3">
          <div className="flex items-start justify-between gap-3">
            <p className="type-body text-ink">
              Imposta la tua Liquidità iniziale per cominciare.
            </p>
            <button
              type="button"
              onClick={dismiss}
              aria-label="Nascondi il suggerimento"
              data-tap-target
              className="-m-2 inline-flex min-h-11 min-w-11 items-center justify-center rounded-lg text-ink-soft outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              <X className="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => navigate({ to: "/settings" })}>
              Imposta ora
            </Button>
            <Button variant="ghost" onClick={dismiss}>
              Più tardi
            </Button>
          </div>
        </Card>
      ) : null}

      <section className="flex flex-col gap-3">
        <h2 className="type-eyebrow">Spese</h2>
        <Card className="flex flex-col items-center gap-3 py-12 text-center">
          <span aria-hidden="true" className="text-ink-soft">
            <Receipt className="h-7 w-7" />
          </span>
          <p className="type-body text-ink-soft">
            Ancora nessuna spesa questo mese.
          </p>
        </Card>
      </section>
    </div>
  )
}
