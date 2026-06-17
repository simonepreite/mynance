import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation } from "@tanstack/react-query"
import {
  createFileRoute,
  Link as RouterLink,
  redirect,
  useNavigate,
} from "@tanstack/react-router"
import { Check, Copy } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { AuthLayout } from "@/components/Common/AuthLayout"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { PasswordInput } from "@/components/ui/password-input"
import { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { AuthService, type UtenteRegister } from "@/lib/api"
import { handleError } from "@/utils"

const formSchema = z
  .object({
    username: z
      .string()
      .min(3, { message: "L'username deve avere almeno 3 caratteri" })
      .max(50, { message: "L'username è troppo lungo" }),
    password: z
      .string()
      .min(8, { message: "La password deve avere almeno 8 caratteri" }),
    confirm_password: z.string().min(1, { message: "Conferma la password" }),
  })
  .refine((data) => data.password === data.confirm_password, {
    message: "Le password non coincidono",
    path: ["confirm_password"],
  })

type FormData = z.infer<typeof formSchema>

export const Route = createFileRoute("/signup")({
  component: SignUp,
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
        title: "Registrati - mynance",
      },
    ],
  }),
})

function SignUp() {
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()
  const [recoveryCode, setRecoveryCode] = useState<string | null>(null)

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
      confirm_password: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UtenteRegister) =>
      AuthService.register({ requestBody: data }),
    onSuccess: (response) => {
      // Show the one-time recovery code; the account exists from here on.
      setRecoveryCode(response.recovery_code)
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    if (mutation.isPending) return
    const { confirm_password: _confirm_password, ...submitData } = data
    mutation.mutate(submitData)
  }

  if (recoveryCode) {
    return (
      <AuthLayout>
        <RecoveryCodePanel
          code={recoveryCode}
          onContinue={() => navigate({ to: "/login" })}
        />
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
            <h1 className="text-2xl font-bold">Crea il tuo account</h1>
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
                      placeholder="scegli-un-username"
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
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="password-input"
                      placeholder="Almeno 8 caratteri"
                      autoComplete="new-password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirm_password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Conferma password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      data-testid="confirm-password-input"
                      placeholder="Ripeti la password"
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
              Registrati
            </LoadingButton>
          </div>

          <div className="text-center text-sm">
            Hai già un account?{" "}
            <RouterLink to="/login" className="underline underline-offset-4">
              Accedi
            </RouterLink>
          </div>
        </form>
      </Form>
    </AuthLayout>
  )
}

function RecoveryCodePanel({
  code,
  onContinue,
}: {
  code: string
  onContinue: () => void
}) {
  const { showSuccessToast } = useCustomToast()
  const [saved, setSaved] = useState(false)
  const [copied, setCopied] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      showSuccessToast("Codice copiato negli appunti")
    } catch {
      // clipboard may be unavailable; the code is shown on screen regardless
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-center gap-2 text-center">
        <h1 className="text-2xl font-bold">Salva il codice di recupero</h1>
        <p className="text-muted-foreground text-sm">
          Account creato. Questo codice è l'unico modo per recuperare l'accesso
          se dimentichi la password.
        </p>
      </div>

      <Alert variant="destructive">
        <AlertTitle>Lo vedrai solo questa volta</AlertTitle>
        <AlertDescription>
          Non viene inviata alcuna email: conservalo in un posto sicuro adesso.
        </AlertDescription>
      </Alert>

      <div className="flex items-center justify-between gap-3 rounded-md border bg-muted/50 p-4">
        <code
          data-testid="recovery-code"
          className="font-mono text-lg tracking-wider break-all"
        >
          {code}
        </code>
        <Button
          type="button"
          variant="outline"
          size="icon"
          aria-label="Copia il codice di recupero"
          onClick={copy}
        >
          {copied ? <Check /> : <Copy />}
        </Button>
      </div>

      <div className="flex items-start gap-3 text-sm">
        <Checkbox
          id="recovery-saved"
          checked={saved}
          onCheckedChange={(v) => setSaved(v === true)}
          data-testid="recovery-saved"
        />
        <Label htmlFor="recovery-saved" className="font-normal leading-snug">
          Ho salvato il codice di recupero in un posto sicuro.
        </Label>
      </div>

      <Button
        type="button"
        className="w-full"
        disabled={!saved}
        onClick={onContinue}
        data-testid="recovery-continue"
      >
        Vai all'accesso
      </Button>
    </div>
  )
}

export default SignUp
