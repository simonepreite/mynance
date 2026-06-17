import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
  useNavigate,
} from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { AuthLayout } from "@/components/Common/AuthLayout"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { AuthService, type UtenteRecover } from "@/lib/api"
import { handleError } from "@/utils"

const formSchema = z.object({
  username: z.string().min(1, { message: "Inserisci il tuo username" }),
  recovery_code: z
    .string()
    .min(1, { message: "Inserisci il codice di recupero" }),
  new_password: z
    .string()
    .min(8, { message: "La password deve avere almeno 8 caratteri" }),
}) satisfies z.ZodType<UtenteRecover>

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/recover-password")({
  component: RecoverPassword,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: "Recupera l'accesso - mynance",
      },
    ],
  }),
})

function RecoverPassword() {
  const navigate = useNavigate()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: {
      username: "",
      recovery_code: "",
      new_password: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UtenteRecover) =>
      AuthService.recover({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password aggiornata. Ora puoi accedere.")
      navigate({ to: "/login" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    if (mutation.isPending) return
    mutation.mutate(data)
  }

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Recupera l'accesso</h1>
            <p className="text-muted-foreground text-sm">
              Usa il codice di recupero ricevuto alla registrazione per
              impostare una nuova password.
            </p>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="username-input"
                      placeholder="il-tuo-username"
                      type="text"
                      autoComplete="username"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="recovery_code"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Codice di recupero</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="recovery-code-input"
                      placeholder="Il codice salvato alla registrazione"
                      type="text"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="new_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nuova password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="new-password-input"
                      placeholder="Almeno 8 caratteri"
                      autoComplete="new-password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <LoadingButton
              type="submit"
              className="w-full"
              loading={mutation.isPending}
            >
              Aggiorna password
            </LoadingButton>
          </div>

          <p className="text-center text-xs text-muted-foreground">
            Senza il codice di recupero non è possibile recuperare l'account:
            non esiste un altro modo per riottenere l'accesso.
          </p>

          <div className="text-center text-sm">
            Ti sei ricordato la password?{" "}
            <RouterLink to="/login" className="underline underline-offset-4">
              Accedi
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}
