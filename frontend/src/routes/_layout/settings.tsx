import { createFileRoute } from "@tanstack/react-router"

import { Appearance } from "@/components/Common/Appearance"
import useAuth from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: "Impostazioni - mynance",
      },
    ],
  }),
})

function UserSettings() {
  const { user: currentUser } = useAuth()

  if (!currentUser) {
    return null
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Impostazioni</h1>
        <p className="text-muted-foreground">
          Gestisci le preferenze del tuo account
        </p>
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="text-sm font-medium">Account</h2>
        <p className="text-sm text-muted-foreground">
          Username:{" "}
          <span className="font-medium text-foreground">
            {currentUser.username}
          </span>
        </p>
      </div>

      <div className="flex items-center justify-between gap-4">
        <div className="flex flex-col">
          <h2 className="text-sm font-medium">Aspetto</h2>
          <p className="text-sm text-muted-foreground">
            Scegli il tema chiaro, scuro o di sistema.
          </p>
        </div>
        <Appearance />
      </div>
    </div>
  )
}
