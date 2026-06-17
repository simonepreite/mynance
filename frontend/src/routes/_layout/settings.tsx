import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Appearance } from "@/components/Common/Appearance"
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
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { LiquiditaService } from "@/lib/api"
import { formatEurFromCents } from "@/lib/format"
import { parseEurToCents } from "@/lib/money"
import { handleError } from "@/utils"

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [{ title: "Impostazioni - mynance" }],
  }),
})

function UserSettings() {
  const { user: currentUser } = useAuth()

  if (!currentUser) {
    return null
  }

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Impostazioni</h1>
        <p className="text-muted-foreground">
          Gestisci le preferenze del tuo account
        </p>
      </div>

      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-medium">Account</h2>
        <p className="text-sm text-muted-foreground">
          Username:{" "}
          <span className="font-medium text-foreground">
            {currentUser.username}
          </span>
        </p>
      </section>

      <LiquiditaInizialeSection />

      <section className="flex items-center justify-between gap-4">
        <div className="flex flex-col">
          <h2 className="text-sm font-medium">Aspetto</h2>
          <p className="text-sm text-muted-foreground">
            Scegli il tema chiaro, scuro o di sistema.
          </p>
        </div>
        <Appearance />
      </section>
    </div>
  )
}

const schema = z.object({
  amount: z
    .string()
    .min(1, { message: "Inserisci un importo" })
    .refine((v) => parseEurToCents(v) !== null, {
      message: "Importo non valido (es. 1234,56)",
    }),
})

type FormData = z.infer<typeof schema>

function LiquiditaInizialeSection() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data } = useQuery({
    queryKey: ["liquidita-iniziale"],
    queryFn: () => LiquiditaService.readLiquiditaIniziale(),
  })

  const form = useForm<FormData>({
    resolver: zodResolver(schema),
    mode: "onBlur",
    defaultValues: { amount: "" },
  })

  const mutation = useMutation({
    mutationFn: (value_cents: number) =>
      LiquiditaService.setLiquiditaIniziale({ requestBody: { value_cents } }),
    onSuccess: (res) => {
      showSuccessToast(
        res.rebaselined
          ? "Liquidità iniziale ri-basata: tutti i valori derivati si aggiornano."
          : "Liquidità iniziale impostata.",
      )
      form.reset({ amount: "" })
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["liquidita-iniziale"] })
    },
  })

  const onSubmit = (values: FormData) => {
    const cents = parseEurToCents(values.amount)
    if (cents === null || mutation.isPending) return
    mutation.mutate(cents)
  }

  const current =
    data?.is_set && data.value_cents != null
      ? formatEurFromCents(data.value_cents)
      : "Non impostata"

  return (
    <section className="flex flex-col gap-3">
      <div className="flex flex-col">
        <h2 className="text-sm font-medium">Liquidità iniziale</h2>
        <p className="text-sm text-muted-foreground">
          La base da cui partono tutti i calcoli. Attuale:{" "}
          <span className="font-medium text-foreground">{current}</span>
        </p>
      </div>

      {data?.is_set ? (
        <p className="text-xs text-muted-foreground">
          Modificarla è una ri-basatura: sposta ogni valore derivato e viene
          registrata.
        </p>
      ) : null}

      <Form {...form}>
        <form
          onSubmit={form.handleSubmit(onSubmit)}
          className="flex flex-col gap-2 sm:flex-row sm:items-start"
        >
          <FormField
            control={form.control}
            name="amount"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel className="sr-only">Importo in euro</FormLabel>
                <FormControl>
                  <Input
                    inputMode="decimal"
                    placeholder="Es. 1234,56"
                    data-testid="liquidita-iniziale-input"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <LoadingButton type="submit" loading={mutation.isPending}>
            {data?.is_set ? "Aggiorna" : "Imposta"}
          </LoadingButton>
        </form>
      </Form>
    </section>
  )
}
