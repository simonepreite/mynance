// Input parsing for money entry. The API stores/derives money as integer cents;
// this turns a user-typed euro amount into integer cents WITHOUT float drift
// (integer arithmetic on the whole/fraction parts). Display formatting lives in
// `format.ts`; never derive money on the client.

/**
 * Parse a user-typed euro amount into integer cents.
 * Accepts `"1234.56"` or `"1234,56"` (Italian comma), optional thousands dots
 * are not assumed. Returns `null` for anything that isn't a non-negative amount
 * with at most two decimals.
 */
export function parseEurToCents(raw: string): number | null {
  const s = raw.trim().replace(/\s/g, "").replace(",", ".")
  if (!/^\d+(\.\d{1,2})?$/.test(s)) {
    return null
  }
  const [intPart, fracPart = ""] = s.split(".")
  return Number(intPart) * 100 + Number(`${fracPart}00`.slice(0, 2))
}
