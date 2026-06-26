import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
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
import { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { AuthService, type ForgotPasswordRequest } from "@/lib/api"
import { handleError } from "@/utils"

const formSchema = z.object({
  email: z.string().email({ message: "Inserisci un'email valida" }),
}) satisfies z.ZodType<ForgotPasswordRequest>

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/forgot-password")({
  component: ForgotPassword,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({ to: "/" })
    }
  },
  head: () => ({
    meta: [{ title: "Password dimenticata - mynance" }],
  }),
})

function ForgotPassword() {
  const { showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    defaultValues: { email: "" },
  })

  const mutation = useMutation({
    mutationFn: (data: ForgotPasswordRequest) =>
      AuthService.forgotPassword({ requestBody: data }),
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    if (mutation.isPending) return
    mutation.mutate(data)
  }

  if (mutation.isSuccess) {
    return (
      <AuthLayout>
        <div className="flex flex-col gap-6 text-center">
          <h1 className="text-2xl font-bold">Controlla la posta</h1>
          <p className="text-muted-foreground text-sm">
            Se l'email è associata a un account, ti abbiamo inviato un link per
            reimpostare la password. Controlla anche la cartella spam.
          </p>
          <RouterLink
            to="/login"
            className="text-sm underline underline-offset-4"
          >
            Torna all'accesso
          </RouterLink>
        </div>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Password dimenticata</h1>
            <p className="text-muted-foreground text-sm">
              Inserisci la tua email: ti invieremo un link per reimpostare la
              password.
            </p>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="email-input"
                      placeholder="tu@esempio.it"
                      type="email"
                      autoComplete="email"
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
              Invia il link
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            Hai un codice di recupero?{" "}
            <RouterLink
              to="/recover-password"
              className="underline underline-offset-4"
            >
              Usa il codice
            </RouterLink>
          </div>

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
