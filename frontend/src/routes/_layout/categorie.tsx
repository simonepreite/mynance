import { zodResolver } from "@hookform/resolvers/zod"
import {
  useMutation,
  useQuery,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Pencil, Plus, Tags, Trash2 } from "lucide-react"
import { Fragment, Suspense, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Skeleton } from "@/components/ui/skeleton"
import useCustomToast from "@/hooks/useCustomToast"
import {
  type CategoriaCreate,
  type CategoriaPublic,
  type CategoriaTipo,
  CategorieService,
} from "@/lib/api"
import { cn } from "@/lib/utils"
import { handleError } from "@/utils"

function categorieQueryOptions() {
  return {
    queryKey: ["categorie"],
    queryFn: () => CategorieService.listCategorie(),
  }
}

export const Route = createFileRoute("/_layout/categorie")({
  component: Categorie,
  head: () => ({
    meta: [
      {
        title: "Categorie - mynance",
      },
    ],
  }),
})

const TIPO_LABELS: Record<CategoriaTipo, string> = {
  spesa: "Spese",
  entrata: "Entrate",
}

function Categorie() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Categorie</h1>
          <p className="text-muted-foreground">
            Organizza i tuoi movimenti per categoria di spesa e di entrata
          </p>
        </div>
        <CreateCategoria />
      </div>
      <Suspense fallback={<CategorieSkeleton />}>
        <CategorieLists />
      </Suspense>
    </div>
  )
}

function CategorieLists() {
  const { data } = useSuspenseQuery(categorieQueryOptions())

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <CategoriaGroup tipo="spesa" categorie={data.spesa} />
      <CategoriaGroup tipo="entrata" categorie={data.entrata} />
    </div>
  )
}

function CategoriaGroup({
  tipo,
  categorie,
}: {
  tipo: CategoriaTipo
  categorie: CategoriaPublic[]
}) {
  const parents = categorie.filter((c) => c.parent_id == null)
  const childrenOf = (id: string) => categorie.filter((c) => c.parent_id === id)

  return (
    <section className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        {TIPO_LABELS[tipo]}
      </h2>
      {categorie.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-md border border-dashed py-10 text-center">
          <div className="rounded-full bg-muted p-3 mb-3">
            <Tags className="h-6 w-6 text-muted-foreground" />
          </div>
          <p className="text-sm text-muted-foreground">
            Nessuna categoria di {TIPO_LABELS[tipo].toLowerCase()}
          </p>
        </div>
      ) : (
        <ul className="flex flex-col gap-2">
          {parents.map((parent) => (
            <Fragment key={parent.id}>
              <CategoriaRow categoria={parent} />
              {childrenOf(parent.id).map((child) => (
                <CategoriaRow
                  key={child.id}
                  categoria={child}
                  className="ml-6"
                />
              ))}
            </Fragment>
          ))}
        </ul>
      )}
    </section>
  )
}

function CategoriaRow({
  categoria,
  className,
}: {
  categoria: CategoriaPublic
  className?: string
}) {
  return (
    <li
      className={cn(
        "flex items-center justify-between gap-2 rounded-md border px-4 py-3",
        className,
      )}
    >
      <span className="truncate">{categoria.nome}</span>
      <div className="flex items-center gap-1">
        <RenameCategoria categoria={categoria} />
        <DeleteCategoria categoria={categoria} />
      </div>
    </li>
  )
}

const NO_PARENT = "__none__"

const createSchema = z.object({
  nome: z.string().min(1, { message: "Inserisci un nome" }).max(60),
  tipo: z.enum(["spesa", "entrata"]),
}) satisfies z.ZodType<CategoriaCreate>

type CreateFormData = z.infer<typeof createSchema>

function CreateCategoria() {
  const [isOpen, setIsOpen] = useState(false)
  const [parentId, setParentId] = useState<string>("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: categorieData } = useQuery(categorieQueryOptions())

  const form = useForm<CreateFormData>({
    resolver: zodResolver(createSchema),
    mode: "onBlur",
    defaultValues: { nome: "", tipo: "spesa" },
  })

  const selectedTipo = form.watch("tipo")

  const topLevelParents = (categorieData?.[selectedTipo] ?? []).filter(
    (c) => c.parent_id == null && !c.is_system,
  )

  const mutation = useMutation({
    mutationFn: (data: CategoriaCreate) =>
      CategorieService.createCategoria({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Categoria creata")
      form.reset({ nome: "", tipo: "spesa" })
      setParentId("")
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["categorie"] })
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button data-testid="add-categoria">
          <Plus className="mr-2" />
          Nuova categoria
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Nuova categoria</DialogTitle>
          <DialogDescription>
            Scegli un nome e il tipo della categoria.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((data) =>
              mutation.mutate({
                ...data,
                parent_id: parentId && parentId !== NO_PARENT ? parentId : null,
              }),
            )}
          >
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="nome"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Nome <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input placeholder="Es. Spesa, Stipendio" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="tipo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tipo</FormLabel>
                    <Select
                      onValueChange={(val) => {
                        field.onChange(val)
                        setParentId("")
                      }}
                      value={field.value}
                    >
                      <FormControl>
                        <SelectTrigger data-testid="categoria-tipo">
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="spesa">Spesa</SelectItem>
                        <SelectItem value="entrata">Entrata</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              {topLevelParents.length > 0 && (
                <div className="flex flex-col gap-2">
                  <label
                    className="text-sm font-medium leading-none"
                    htmlFor="parent-select"
                  >
                    Sottocategoria di…
                  </label>
                  <Select value={parentId} onValueChange={setParentId}>
                    <SelectTrigger id="parent-select">
                      <SelectValue placeholder="Nessuna (categoria principale)" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={NO_PARENT}>
                        Nessuna (categoria principale)
                      </SelectItem>
                      {topLevelParents.map((p) => (
                        <SelectItem key={p.id} value={p.id}>
                          {p.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>
                  Annulla
                </Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>
                Crea
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

const renameSchema = z.object({
  nome: z.string().min(1, { message: "Inserisci un nome" }).max(60),
})

type RenameFormData = z.infer<typeof renameSchema>

function RenameCategoria({ categoria }: { categoria: CategoriaPublic }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<RenameFormData>({
    resolver: zodResolver(renameSchema),
    mode: "onBlur",
    defaultValues: { nome: categoria.nome },
  })

  const mutation = useMutation({
    mutationFn: (data: RenameFormData) =>
      CategorieService.updateCategoria({
        categoriaId: categoria.id,
        requestBody: { nome: data.nome },
      }),
    onSuccess: () => {
      showSuccessToast("Categoria rinominata")
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["categorie"] })
    },
  })

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open)
        if (open) form.reset({ nome: categoria.nome })
      }}
    >
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Rinomina ${categoria.nome}`}
        >
          <Pencil className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Rinomina categoria</DialogTitle>
          <DialogDescription>
            Aggiorna il nome della categoria.
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit((data) => mutation.mutate(data))}>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="nome"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>
                  Annulla
                </Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>
                Salva
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

function DeleteCategoria({ categoria }: { categoria: CategoriaPublic }) {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () =>
      CategorieService.deleteCategoria({ categoriaId: categoria.id }),
    onSuccess: () => {
      showSuccessToast("Categoria eliminata")
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["categorie"] })
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={`Elimina ${categoria.nome}`}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Elimina categoria</DialogTitle>
          <DialogDescription>
            Vuoi eliminare "{categoria.nome}"? L'operazione non può essere
            annullata.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              Annulla
            </Button>
          </DialogClose>
          <LoadingButton
            variant="destructive"
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            Elimina
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function CategorieSkeleton() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      {[0, 1].map((col) => (
        <div key={col} className="flex flex-col gap-2">
          <Skeleton className="h-4 w-20" />
          {[0, 1, 2].map((row) => (
            <Skeleton key={row} className="h-12 w-full" />
          ))}
        </div>
      ))}
    </div>
  )
}
