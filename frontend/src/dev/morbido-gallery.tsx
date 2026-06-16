import { StrictMode } from "react"
import ReactDOM from "react-dom/client"
import {
  BalanceBlock,
  BottomNav,
  Button,
  Card,
  Chip,
  HonestyBanner,
  Input,
  ListRow,
} from "@/components/morbido"
import { ThemeProvider, useTheme } from "@/components/theme-provider"
import "@/index.css"

const NAV_ITEMS = [
  { id: "home", label: "Home" },
  { id: "liquidita", label: "Liquidità" },
  { id: "statistiche", label: "Statistiche" },
]

// Dev-only component gallery. Not part of the app router — served as a separate
// Vite multi-page entry (morbido-gallery.html) purely so the Playwright theme
// project can exercise the shared library and the accessibility floor.
function Gallery() {
  const { resolvedTheme, setTheme } = useTheme()

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col gap-4 bg-background p-5">
      {/* focus-probe is intentionally the first focusable element so the e2e
          can Tab to a known target and assert the focus ring. */}
      <Button data-testid="focus-probe">Focus me</Button>

      <div className="flex items-center gap-2">
        <Button
          variant="secondary"
          data-testid="set-light"
          onClick={() => setTheme("light")}
        >
          Light
        </Button>
        <Button
          variant="secondary"
          data-testid="set-dark"
          onClick={() => setTheme("dark")}
        >
          Dark
        </Button>
        <span
          data-testid="current-theme"
          className="type-caption text-ink-soft"
        >
          {resolvedTheme}
        </span>
      </div>

      <Card data-testid="card">
        <p className="type-h2 text-ink">Card</p>
        <p className="type-body text-ink-soft">A floating Morbido surface.</p>
      </Card>

      <BalanceBlock
        data-testid="balance-block"
        label="Bilancio · Giugno"
        cents={123456}
      />
      <BalanceBlock
        data-testid="balance-block-negative"
        label="Bilancio · Maggio"
        cents={-45678}
      />

      <HonestyBanner>
        Una liquidità non riconciliata da 12 giorni.
      </HonestyBanner>

      <Card>
        <div data-testid="list-row">
          <ListRow label="Spesa" value="€ 12,00" onSelect={() => undefined} />
        </div>
      </Card>

      <div className="flex gap-2">
        <Chip data-testid="chip" selected>
          Selezionato
        </Chip>
        <Chip>Non selezionato</Chip>
      </div>

      <Input data-testid="input" placeholder="Importo" aria-label="Importo" />

      <div data-testid="bottom-nav" className="mt-auto">
        <BottomNav items={NAV_ITEMS} activeId="home" />
      </div>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider defaultTheme="system" storageKey="mynance-theme">
      <Gallery />
    </ThemeProvider>
  </StrictMode>,
)
