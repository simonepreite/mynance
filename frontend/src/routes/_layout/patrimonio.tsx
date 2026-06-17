import { createFileRoute } from "@tanstack/react-router"
import { Landmark } from "lucide-react"

import { ComingSoon } from "@/components/Common/ComingSoon"

export const Route = createFileRoute("/_layout/patrimonio")({
  component: Patrimonio,
  head: () => ({
    meta: [{ title: "Patrimonio - mynance" }],
  }),
})

function Patrimonio() {
  return (
    <ComingSoon title="Patrimonio" icon={<Landmark className="h-7 w-7" />}>
      Qui vedrai il tuo patrimonio netto: liquidità, investimenti e beni.
      Arriverà a breve.
    </ComingSoon>
  )
}
