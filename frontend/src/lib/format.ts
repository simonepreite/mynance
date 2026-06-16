// Display-only money/date formatting (Story 1.1, AC7).
// NEVER compute or store money here. Money is integer cents in the API; this
// module only renders it for the UI. Derived money is always computed server-side.

const eurDigits = new Intl.NumberFormat("it-IT", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
  // Force the thousands separator so output is deterministic across runtimes
  // (default "auto" omits grouping for 4-digit integers under small-ICU builds),
  // matching the documented `€ 1.234,56` example.
  useGrouping: true,
})

/**
 * Format integer cents as an Italian euro string, e.g. `123456` -> `"€ 1.234,56"`.
 * @param cents integer minor units (no floats)
 */
export function formatEurFromCents(cents: number): string {
  if (!Number.isInteger(cents)) {
    throw new Error("formatEurFromCents expects integer cents, not a float")
  }
  return `€ ${eurDigits.format(cents / 100)}`
}

/**
 * Format an ISO date (`YYYY-MM-DD`) in Italian locale, e.g. `"16/06/2026"`.
 * Returns `""` for empty/invalid input (never throws). Date-only strings are
 * formatted from their UTC parts so they don't shift a day in negative-offset
 * timezones (`new Date("2026-06-16")` is UTC midnight).
 */
export function formatDateIt(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) {
    return ""
  }
  const isDateOnly = /^\d{4}-\d{2}-\d{2}$/.test(iso)
  return new Intl.DateTimeFormat(
    "it-IT",
    isDateOnly ? { timeZone: "UTC" } : undefined,
  ).format(date)
}
