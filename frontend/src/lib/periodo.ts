// Client-side period helpers for the period selector (UX-DR3). These compute
// the anchor to send to the server aggregation; the server owns the boundaries
// and all money math (API-3). Dates are plain `YYYY-MM-DD` strings handled in
// UTC parts so labels never shift a day.

export type Period = "day" | "week" | "month" | "year"

export const PERIODS: { value: Period; label: string }[] = [
  { value: "day", label: "Giorno" },
  { value: "week", label: "Settimana" },
  { value: "month", label: "Mese" },
  { value: "year", label: "Anno" },
]

function fmt(d: Date): string {
  const y = d.getUTCFullYear()
  const m = String(d.getUTCMonth() + 1).padStart(2, "0")
  const day = String(d.getUTCDate()).padStart(2, "0")
  return `${y}-${m}-${day}`
}

export function todayIso(): string {
  const now = new Date()
  return fmt(
    new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())),
  )
}

function parts(iso: string): [number, number, number] {
  const [y, m, d] = iso.split("-").map(Number)
  return [y, m, d]
}

export function shiftAnchor(
  period: Period,
  iso: string,
  delta: number,
): string {
  const [y, m, d] = parts(iso)
  if (period === "day") {
    return fmt(new Date(Date.UTC(y, m - 1, d + delta)))
  }
  if (period === "week") {
    return fmt(new Date(Date.UTC(y, m - 1, d + 7 * delta)))
  }
  if (period === "month") {
    return fmt(new Date(Date.UTC(y, m - 1 + delta, 1)))
  }
  return `${y + delta}-01-01` // year
}

const MONTHS = new Intl.DateTimeFormat("it-IT", {
  month: "long",
  timeZone: "UTC",
})
const DAYMONTH = new Intl.DateTimeFormat("it-IT", {
  day: "numeric",
  month: "short",
  timeZone: "UTC",
})
const FULL = new Intl.DateTimeFormat("it-IT", {
  day: "numeric",
  month: "long",
  year: "numeric",
  timeZone: "UTC",
})

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

export function periodLabel(period: Period, iso: string): string {
  const [y, m, d] = parts(iso)
  const date = new Date(Date.UTC(y, m - 1, d))
  if (period === "day") {
    return cap(FULL.format(date))
  }
  if (period === "week") {
    const monday = new Date(date)
    monday.setUTCDate(date.getUTCDate() - ((date.getUTCDay() + 6) % 7))
    const sunday = new Date(monday)
    sunday.setUTCDate(monday.getUTCDate() + 6)
    return `${DAYMONTH.format(monday)} – ${DAYMONTH.format(sunday)} ${y}`
  }
  if (period === "month") {
    return `${cap(MONTHS.format(date))} ${y}`
  }
  return String(y) // year
}
