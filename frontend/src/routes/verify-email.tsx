import { useMutation } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
  useNavigate,
} from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
import { z } from "zod"
import { AuthLayout } from "@/components/Common/AuthLayout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { AuthService } from "@/lib/api"

const searchSchema = z.object({
  token: z.string().catch(""),
})

export const Route = createFileRoute("/verify-email")({
  component: VerifyEmail,
  validateSearch: searchSchema,
  beforeLoad: async ({ search }) => {
    if (!search.token) {
      throw redirect({ to: "/login" })
    }
  },
  head: () => ({
    meta: [{ title: "Verifica email - mynance" }],
  }),
})

function VerifyEmail() {
  const { token } = Route.useSearch()
  const navigate = useNavigate()
  const { showSuccessToast } = useCustomToast()
  const [identifier, setIdentifier] = useState("")

  const verifyMutation = useMutation({
    mutationFn: (t: string) =>
      AuthService.verifyEmail({ requestBody: { token: t } }),
  })

  const resendMutation = useMutation({
    mutationFn: (id: string) =>
      AuthService.resendVerification({ requestBody: { identifier: id } }),
    onSuccess: () =>
      showSuccessToast(
        "Se l'account esiste e non è verificato, ti abbiamo inviato un nuovo link.",
      ),
  })

  // Consume the token once on mount (guard against StrictMode double-invoke).
  const started = useRef(false)
  useEffect(() => {
    if (started.current) return
    started.current = true
    verifyMutation.mutate(token)
  }, [token, verifyMutation.mutate, verifyMutation])

  if (verifyMutation.isSuccess) {
    return (
      <AuthLayout>
        <div className="flex flex-col gap-6 text-center">
          <h1 className="text-2xl font-bold">Email verificata</h1>
          <p className="text-muted-foreground text-sm">
            Il tuo indirizzo è stato confermato. Ora puoi accedere.
          </p>
          <Button onClick={() => navigate({ to: "/login" })}>
            Vai all'accesso
          </Button>
        </div>
      </AuthLayout>
    )
  }

  if (verifyMutation.isError) {
    return (
      <AuthLayout>
        <div className="flex flex-col gap-6">
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Link non valido</h1>
            <p className="text-muted-foreground text-sm">
              Il link di verifica non è valido o è scaduto. Inserisci il tuo
              username o email per riceverne uno nuovo.
            </p>
          </div>
          <div className="grid gap-3">
            <Input
              data-testid="identifier-input"
              placeholder="username o tu@esempio.it"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
            />
            <LoadingButton
              type="button"
              className="w-full"
              loading={resendMutation.isPending}
              disabled={!identifier}
              onClick={() => resendMutation.mutate(identifier)}
            >
              Reinvia email di verifica
            </LoadingButton>
          </div>
          <div className="text-center text-sm">
            <RouterLink to="/login" className="underline underline-offset-4">
              Torna all'accesso
            </RouterLink>
          </div>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout>
      <div className="flex flex-col gap-4 text-center">
        <h1 className="text-2xl font-bold">Verifica in corso…</h1>
        <p className="text-muted-foreground text-sm">Un attimo solo.</p>
      </div>
    </AuthLayout>
  )
}
