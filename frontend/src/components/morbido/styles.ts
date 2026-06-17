// Shared keyboard focus ring: a visible 2px ring using the dedicated focus
// token (never the soft accent) — Story 1.2, AC3. Plain utility classes (not
// @apply) so Tailwind picks them up from source exactly like the shadcn set.
export const focusRing =
  "outline-none focus-visible:ring-2 focus-visible:ring-focus focus-visible:ring-offset-2 focus-visible:ring-offset-background"
