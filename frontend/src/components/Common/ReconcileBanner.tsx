import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import { HonestyBanner } from "@/components/morbido"
import { RiconciliazioneService } from "@/lib/api"
import { formatEurFromCents } from "@/lib/format"

// Honesty surfaces (UX-DR8): a warm-amber "due" banner when it's time to
// reconcile, or a quiet standing indicator for an acknowledged-open Drift.
// Never alarm-red, never modal; taps into the Riconciliazione flow.
export function ReconcileBanner() {
  const navigate = useNavigate()
  const { data } = useQuery({
    queryKey: ["promemoria"],
    queryFn: () => RiconciliazioneService.promemoria(),
  })

  if (!data) return null

  let message: string | null = null
  if (data.due) {
    message =
      data.data_ultima_riconciliazione === null
        ? "È ora di riconciliare — non l'hai ancora fatto."
        : `È ora di riconciliare — ultima volta: ${data.giorni_dall_ultima} gg fa.`
  } else if (data.drift_aperto_cents != null && data.drift_aperto_cents !== 0) {
    const d = data.drift_aperto_cents
    message = `Scostamento aperto: ${d < 0 ? "−" : "+"}${formatEurFromCents(Math.abs(d))}.`
  }

  if (!message) return null

  return (
    <button
      type="button"
      onClick={() => navigate({ to: "/riconciliazione" })}
      className="w-full text-left outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-panel"
    >
      <HonestyBanner>{message}</HonestyBanner>
    </button>
  )
}
