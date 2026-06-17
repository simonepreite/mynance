import { createFileRoute } from "@tanstack/react-router"
import { BarChart3 } from "lucide-react"

import { ComingSoon } from "@/components/Common/ComingSoon"

export const Route = createFileRoute("/_layout/statistiche")({
  component: Statistiche,
  head: () => ({
    meta: [{ title: "Statistiche - mynance" }],
  }),
})

function Statistiche() {
  return (
    <ComingSoon title="Statistiche" icon={<BarChart3 className="h-7 w-7" />}>
      Qui troverai i grafici di andamento e la ripartizione delle spese.
      Arriverà a breve.
    </ComingSoon>
  )
}
