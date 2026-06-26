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
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
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
import useAuth, { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { ApiError, AuthService, type UtenteLogin } from "@/lib/api"

const formSchema = z.object({
  username: z.string().min(1, { message: "Inserisci username o email" }),
  password: z.string().min(1, { message: "Inserisci la password" }),
}) satisfies z.ZodType<UtenteLogin>

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/login")({
  component: Login,
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
        title: "Accedi - mynance",
      },
    ],
  }),
})

function Login() {
  const { loginMutation } = useAuth()
  const { showSuccessToast } = useCustomToast()
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  // A 403 means the account exists but its email isn't verified yet — offer to
  // resend the verification link instead of just toasting the error.
  const notVerified =
    loginMutation.error instanceof ApiError &&
    loginMutation.error.status === 403

  const resendMutation = useMutation({
    mutationFn: (identifier: string) =>
      AuthService.resendVerification({ requestBody: { identifier } }),
    onSuccess: () =>
      showSuccessToast(
        "Email di verifica inviata. Controlla la posta (anche lo spam).",
      ),
  })

  const onSubmit = (data: FormData) => {
    if (loginMutation.isPending) return
    loginMutation.mutate(data)
  }

  return (
    <AuthLayout>
      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-6"
        >
          <div className="flex flex-col items-center gap-2 text-center">
            <h1 className="text-2xl font-bold">Accedi al tuo account</h1>
          </div>

          <div className="grid gap-4">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username o email</FormLabel>
                  <FormControl>
                    <Input
                      data-testid="username-input"
                      placeholder="username o tu@esempio.it"
                      type="text"
                      autoComplete="username"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center">
                    <FormLabel>Password</FormLabel>
                    <RouterLink
                      to="/forgot-password"
                      className="ml-auto text-sm underline-offset-4 hover:underline"
                    >
                      Password dimenticata?
                    </RouterLink>
                  </div>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="Password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <LoadingButton type="submit" loading={loginMutation.isPending}>
              Accedi
            </LoadingButton>

            {notVerified && (
              <Alert>
                <AlertTitle>Email non verificata</AlertTitle>
                <AlertDescription className="flex flex-col items-start gap-2">
                  <span>
                    Conferma il link che ti abbiamo inviato per email prima di
                    accedere.
                  </span>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={resendMutation.isPending}
                    onClick={() =>
                      resendMutation.mutate(form.getValues("username"))
                    }
                  >
                    Reinvia email di verifica
                  </Button>
                </AlertDescription>
              </Alert>
            )}
          </div>

          <div className="text-center text-sm">
            Non hai ancora un account?{" "}
            <RouterLink to="/signup" className="underline underline-offset-4">
              Registrati
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}
