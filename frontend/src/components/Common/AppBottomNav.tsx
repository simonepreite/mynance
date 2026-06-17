import { useNavigate, useRouterState } from "@tanstack/react-router"
import { BarChart3, Home, Landmark, Plus, Wallet } from "lucide-react"
import { useState } from "react"
import { BottomNav, type BottomNavItem } from "@/components/morbido"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

// The five primary slots (UX-DR2). The central "Aggiungi" is the quick-add FAB,
// whose bottom-sheet lands in Story 2.7 — here it is a calm stub. Liquidità,
// Statistiche and Patrimonio route to placeholder screens until their epics.
const ICON = "h-5 w-5"
const items: (BottomNavItem & { path?: string })[] = [
  { id: "home", label: "Home", icon: <Home className={ICON} />, path: "/" },
  {
    id: "liquidita",
    label: "Liquidità",
    icon: <Wallet className={ICON} />,
    path: "/liquidita",
  },
  { id: "add", label: "Aggiungi", icon: <Plus className={ICON} /> },
  {
    id: "statistiche",
    label: "Statistiche",
    icon: <BarChart3 className={ICON} />,
    path: "/statistiche",
  },
  {
    id: "patrimonio",
    label: "Patrimonio",
    icon: <Landmark className={ICON} />,
    path: "/patrimonio",
  },
]

const PATH_TO_ID: Record<string, string> = {
  "/": "home",
  "/liquidita": "liquidita",
  "/statistiche": "statistiche",
  "/patrimonio": "patrimonio",
}

export function AppBottomNav() {
  const navigate = useNavigate()
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const [addOpen, setAddOpen] = useState(false)

  const activeId = PATH_TO_ID[pathname] ?? ""

  const onSelect = (id: string) => {
    if (id === "add") {
      setAddOpen(true)
      return
    }
    const target = items.find((i) => i.id === id)?.path
    if (target) navigate({ to: target })
  }

  return (
    <>
      <BottomNav items={items} activeId={activeId} onSelect={onSelect} />
      <Dialog open={addOpen} onOpenChange={setAddOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Aggiungi un movimento</DialogTitle>
            <DialogDescription>
              Presto potrai registrare spese ed entrate da qui, in pochi tocchi.
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </>
  )
}
