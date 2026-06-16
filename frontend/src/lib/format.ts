// Display-only money/date formatting (Story 1.1, AC7).
// NEVER compute or store money here. Money is integer cents in the API; this
// module only renders it for the UI. Derived money is always computed server-side.

const eurDigits = new Intl.NumberFormat("it-IT", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
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

/** Format an ISO date (`YYYY-MM-DD`) in Italian locale, e.g. `"16/06/2026"`. */
export function formatDateIt(iso: string): string {
  return new Intl.DateTimeFormat("it-IT").format(new Date(iso))
}
