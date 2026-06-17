import { createFileRoute } from "@tanstack/react-router"
import { Wallet } from "lucide-react"

import { ComingSoon } from "@/components/Common/ComingSoon"

export const Route = createFileRoute("/_layout/liquidita")({
  component: Liquidita,
  head: () => ({
    meta: [{ title: "Liquidità - mynance" }],
  }),
})

function Liquidita() {
  return (
    <ComingSoon title="Liquidità" icon={<Wallet className="h-7 w-7" />}>
      Qui vedrai la tua liquidità, l'allocazione nei secchielli e il risparmio
      libero. Arriverà a breve.
    </ComingSoon>
  )
}
