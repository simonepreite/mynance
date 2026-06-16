# Deferred Work

## Deferred from: code review of story 1-1 (2026-06-16)

- **`localStorage` access unguarded in template `theme-provider.tsx`** [frontend/src/components/theme-provider.tsx:36] — accessing `localStorage` in the `useState` initializer (and `setItem` on change) is not wrapped in try/catch, so it throws and crashes the React render in private-mode / disabled-storage / SSR contexts. Pre-existing, template-vendored (introduced in template import commit 7b931eb, not in mynance's delta). Revisit when reworking the theme provider for AC5.
- **Egress lint rule absent** [frontend/biome.json] — Task 6 subtask asked for a lint rule banning hand-written `fetch`/`axios`/`XMLHttpRequest` outside `frontend/src/lib/api`. Not implemented because the template's `src/utils.ts` legitimately imports `AxiosError`. AC6's literal text (lint/type/test/build gating) is still satisfied; the egress boundary is currently enforced by convention/README + the generated client. Add the scoped rule when convenient.
