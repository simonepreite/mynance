---
stepsCompleted: [1, 2, 3, 4, 5, 6]
status: 'complete'
inputDocuments:
  - prds/prd-mynance-2026-06-15/prd.md
  - ux-designs/ux-mynance-2026-06-15/DESIGN.md
  - ux-designs/ux-mynance-2026-06-15/EXPERIENCE.md
  - architecture.md
  - epics.md
---

# Implementation Readiness Assessment Report

**Date:** 2026-06-16
**Project:** mynance

## Document Inventory

| Type | Document(s) | Format | Status |
|------|-------------|--------|--------|
| PRD | `prds/prd-mynance-2026-06-15/prd.md` | whole | final |
| UX Design | `ux-designs/ux-mynance-2026-06-15/DESIGN.md` + `EXPERIENCE.md` | two peer specs | final |
| Architecture | `architecture.md` | whole | complete |
| Epics & Stories | `epics.md` (6 epics, 36 stories) | whole | complete |

No duplicate (whole + sharded) conflicts. No required documents missing. (`reconcile-prd.md` is a UX review artifact, excluded from assessment inputs.)

## PRD Analysis

### Functional Requirements (22 FR + 3 API)
- FR-1: Self-service registration (username + password; empty isolated dataset; unique usernames; salted-hash passwords).
- FR-2: Authentication & session (login; 30-day idle, configurable; logout; non-revealing invalid-credential errors).
- FR-3: Password recovery via one-time recovery code (shown once, salted-hash, regeneratable; no email).
- FR-4: Data isolation (read/write only own data; cross-Utente → not-found/forbidden).
- FR-5: Record a Spesa (amount, date, Spesa-type Categoria, note, optional Secchiello link default-from-Categoria + override; affects Liquidità).
- FR-6: Record an Entrata (increases Liquidità).
- FR-7: Typed Categorie (Spesa/Entrata distinct spaces) + optional Categoria→Secchiello link; starter set per type; delete-in-use reassigns.
- FR-8: Regole ricorrenti auto-generate Entrate / Versamenti PAC up to today; editable/skippable.
- FR-9: Auto-computed Quota `max(0,(Importo previsto−Saldo)/mesi)`, `mesi=max(1,ceil(days/30.44))`.
- FR-10: Funding/payment/carryover lifecycle (derived-on-read chronological; negative Saldo surfaced, never clamped).
- FR-11: Any Periodicità (monthly/quarterly/semiannual/annual/custom).
- FR-12: Set Liquidità iniziale once (later change = logged re-baseline).
- FR-13: Derived Liquidità `iniziale + ΣEntrate − ΣSpese − ΣCapitale versato`.
- FR-14: Allocation breakdown (allocata `Σmax(0,Saldo)`, Risparmio libero).
- FR-15: Cuscinetto warning `N×Spesa media` (N=6; last N complete months incl. "non identificato").
- FR-16: In-app reconciliation reminder from `today−last Riconciliazione` (no scheduler).
- FR-17: Reconcile real liquidity → Drift (€ and %); sets last-reconciliation date.
- FR-18: Close gap via "non identificato" Movimento, or acknowledge-and-leave-open.
- FR-19: Investimenti (PAC) at Capitale versato (Versamento reduces Liquidità; no market value).
- FR-20: Beni immobili at price paid (static).
- FR-21: Beni mobili linear depreciation `max(0, prezzo×(1−Svalut×anni))`; suggested rates.
- FR-22: Net-worth total `Liquidità + Capitale versato + Σ immobili + Σ mobili`; no auto-deduct.
- API-1: Contract independence (logic not only in frontend). · API-2: OpenAPI documented + `/api/v1` versioned. · API-3: derived values server-side, never recomputed per client.

### Non-Functional Requirements (8)
- NFR-1: Calculation correctness & determinism (reproducible; worked-example tests; negative Saldo never clamped).
- NFR-2: Security & per-Utente data isolation (authZ on every access; salted-hash secrets).
- NFR-3: Single currency EUR / Italian context; money in integer cents.
- NFR-4: Data durability & integrity (no Movimento lost; consistent recompute).
- NFR-5: Performance (sub-second derived views over a year+).
- NFR-6: Privacy (minimal data, no third-party sharing/exfiltrating analytics).
- NFR-7: Cost (near-zero operating budget; free to users).
- NFR-8: Honesty principle (uncomfortable truths surfaced plainly, warm amber, never hidden).

### Additional Requirements
- Frontend-agnostic documented API as product surface; V1 web frontend, native later on same core.
- Non-goals (explicit): no bank aggregation, no account concept, no expense-splitting, no live market value, no 2FA/social login, no email/push infra, not paid.

### PRD Completeness Assessment
PRD is `final`, internally consistent, with every FR carrying testable "Consequences" (≈ acceptance criteria). Formulas are unambiguous (money in cents, derived-on-read, linear depreciation floored at 0). All open questions/assumptions were resolved at finalize (§8 Resolved Decisions); only architecture-owned items deferred (§9). No requirement gaps detected at the PRD level.

## Epic Coverage Validation

### Coverage Matrix
| FR | Requirement | Epic / Story | Status |
|----|-------------|--------------|--------|
| FR-1 | Self-service registration | Epic 1 · Story 1.3 | ✓ Covered |
| FR-2 | Authentication & session | Epic 1 · Story 1.4 | ✓ Covered |
| FR-3 | Recovery code | Epic 1 · Story 1.3 | ✓ Covered |
| FR-4 | Data isolation | Epic 1 · Story 1.5 | ✓ Covered |
| FR-5 | Record a Spesa | Epic 2 · Story 2.5 (link in Epic 3 · 3.1) | ✓ Covered |
| FR-6 | Record an Entrata | Epic 2 · Story 2.6 | ✓ Covered |
| FR-7 | Typed Categorie + Secchiello link | Epic 2 · Story 2.1 (link in Epic 3 · 3.1) | ✓ Covered |
| FR-8 | Regole ricorrenti | Epic 6 · Stories 6.1–6.5 | ✓ Covered |
| FR-9 | Auto-computed Quota | Epic 3 · Story 3.2 (+ 3.1) | ✓ Covered |
| FR-10 | Funding/payment/carryover | Epic 3 · Story 3.3 | ✓ Covered |
| FR-11 | Any Periodicità | Epic 3 · Stories 3.1/3.2 | ✓ Covered |
| FR-12 | Set Liquidità iniziale | Epic 2 · Story 2.2 | ✓ Covered |
| FR-13 | Derived Liquidità | Epic 2 · Stories 2.3/2.4 | ✓ Covered |
| FR-14 | Allocation breakdown | Epic 3 · Story 3.5 | ✓ Covered |
| FR-15 | Cuscinetto warning | Epic 3 · Story 3.6 | ✓ Covered |
| FR-16 | Reconciliation reminder | Epic 4 · Stories 4.1/4.2 | ✓ Covered |
| FR-17 | Reconcile / Drift | Epic 4 · Story 4.3 | ✓ Covered |
| FR-18 | "non identificato" / acknowledge | Epic 4 · Stories 4.4/4.5 | ✓ Covered |
| FR-19 | Investimenti (PAC) | Epic 5 · Story 5.1 (recurring in Epic 6 · 6.3) | ✓ Covered |
| FR-20 | Beni immobili | Epic 5 · Story 5.2 | ✓ Covered |
| FR-21 | Beni mobili depreciation | Epic 5 · Story 5.3 | ✓ Covered |
| FR-22 | Net-worth total | Epic 5 · Story 5.4 | ✓ Covered |
| API-1/2/3 | API-as-product (contract, OpenAPI/versioning, server-side logic) | Epic 1 · Story 1.1 (founded) + upheld across all epics | ✓ Covered |

### Missing Requirements
None. Every PRD FR and API requirement maps to at least one story. No story implements a requirement absent from the PRD (no scope creep).

### Coverage Statistics
- Total PRD FRs: 22 (+ 3 API requirements)
- FRs covered in epics: 22 (+ 3 API)
- **Coverage: 100%**

## UX Alignment Assessment

### UX Document Status
**Found** — two peer specs, both `final`: `DESIGN.md` (Morbido visual identity, light/dark tokens) and `EXPERIENCE.md` (IA, flows, states, accessibility floor).

### UX ↔ PRD Alignment
- Every UX surface maps to a PRD FR (EXPERIENCE.md IA table + coverage self-check); the Key Flows mirror the PRD's UJ-1…UJ-4 with the same protagonists (Marco, Elena) verbatim.
- The PRD's honesty principle (NFR-8) and entry-burden counter-metric (SM-C1) are carried into UX as the warm-amber honesty states and the "al volo" quick-capture.
- UX-introduced decisions (mobile-first adaptive surfaces, period-aware Home, charts-only Statistiche) extend — not contradict — the PRD (web-first V1, manual entry, allocation awareness). No UX requirement conflicts with the PRD.

### UX ↔ Architecture Alignment
- Architecture's Frontend section explicitly adopts the Morbido design tokens as CSS custom properties (light/dark, system default + override) and the installable PWA (vite-plugin-pwa) — directly supporting DESIGN.md and UX-DR1/2/12/13.
- Derived values computed server-side (API-3) and consumed via the generated TS client → the UX rule "client never recomputes money" is architecturally enforced.
- UX state patterns (loading, empty, honesty, offline/stale) are supported: architecture's online-first capture + optimistic UI matches the UX offline/stale handling (true offline queue deferred by both — consistent).
- Accessibility floor (text-safe `-ink` token variants, focus ring, ≥44px targets) is reflected in both DESIGN.md tokens and the architecture/component conventions.

### Alignment Issues
None. UX, PRD, and Architecture are mutually consistent.

### Warnings
None. UX documentation exists and is complete for a user-facing product; architecture accounts for all UX needs.

## Epic Quality Review

### Best-Practices Compliance (create-epics-and-stories standards)
- **User value:** all 6 epics are user-outcome epics — no technical-milestone epics. ✓
- **Epic independence:** E1 standalone; E2 needs only E1; E3 needs E1+E2; E4 needs E1+E2; E5 needs E1+E2; E6 needs E1+E2+E5. No epic requires a *later* epic (the original 5.2→Epic 6 backward dependency was removed during story creation). ✓
- **Within-epic ordering:** each story builds only on earlier stories; the one cross-epic forward dependency (Categoria→Secchiello link in 2.1/2.5) was relocated to Epic 3 (Story 3.1), where Secchielli exist. ✓
- **Story sizing:** each story is single-dev-session sized, with Given/When/Then ACs covering happy path + error/edge cases (negative Saldo surfaced, cross-Utente 404/403, integer cents, optimistic rollback). ✓
- **Table-creation timing:** per-story — `utenti` (1.3), `movimenti` (2.5), `secchielli` (3.1), `riconciliazioni` (4.1), `investimenti`/`versamenti_pac` (5.1), `beni_immobili` (5.2), `beni_mobili` (5.3), `regole_ricorrenti` (6.1). No upfront table dump. ✓
- **Starter template:** Architecture's starter is Epic 1 · Story 1.1 (clone `full-stack-fastapi-template` + deps + Neon + Morbido restyle). ✓
- **Greenfield setup:** init + CI/CD + Docker dev env all in Epic 1. ✓
- **Traceability:** every story references the FR(s) it fulfills. ✓

### Findings
- 🔴 Critical: **none.**
- 🟠 Major: **none.**
- 🟡 Minor (both **fixed** in this pass):
  - Story 3.3 referenced the Categoria→Secchiello link "from Epic 2"; after relocation the link is introduced in Story 3.1 — reference corrected.
  - Stories 2.1 and 4.1 both claimed to provision the system "non identificato" Categorie; 2.1 reworded to defer to Epic 4 (Story 4.1) as the single authoritative provisioning point.

### Compliance Checklist (all epics)
- [x] Epic delivers user value
- [x] Epic functions independently (builds only on earlier epics)
- [x] Stories appropriately sized
- [x] No forward dependencies
- [x] Database tables created when needed
- [x] Clear Given/When/Then acceptance criteria
- [x] Traceability to FRs maintained

## Summary and Recommendations

### Overall Readiness Status
**READY FOR IMPLEMENTATION** — high confidence.

### Assessment Summary
- **FR coverage:** 100% (22 FR + 3 API requirements, each traced to ≥1 story; no scope creep).
- **PRD:** `final`, internally consistent, testable consequences; no requirement gaps.
- **UX ↔ PRD ↔ Architecture:** fully aligned; architecture accounts for all UX needs; no warnings.
- **Epic quality:** all 6 epics user-value-focused, independent, correctly ordered, properly sized, tables-per-story, starter as Story 1.1, full FR traceability.

### Critical Issues Requiring Immediate Action
**None.** The four issues surfaced across the planning chain were all resolved before this report closed:
1. (epic creation) Backward dependency 5.2 → Epic 6 — **removed** (recurring PAC consolidated into Epic 6 · 6.3).
2. (coverage/quality) Forward dependency 2.1/2.5 → Epic 3 (Categoria→Secchiello link) — **relocated** to Epic 3 · Story 3.1.
3. (quality) Stale "from Epic 2" reference in Story 3.3 — **corrected** to Story 3.1.
4. (quality) Duplicate "non identificato" provisioning in 2.1/4.1 — **deduplicated** to Epic 4 · Story 4.1.

### Carry-forward (non-blocking, for awareness during build)
- Derived-on-read performance is a watch item at scale (architecture mitigation: `user_id`+date indexes + per-request memoization; checkpoint snapshots deferred).
- Deferred by design: true offline capture queue, native apps, full GDPR / account-deletion tooling, backup restore drill.

### Recommended Next Steps
1. **`bmad-sprint-planning`** — produce the sprint plan / story sequence from `epics.md`.
2. **`bmad-create-story` → `bmad-dev-story`** — implement story-by-story, starting **Epic 1 · Story 1.1** (init from `full-stack-fastapi-template` + Neon + Morbido restyle), then the authZ boundary and the pure `calc/` engine (with worked-example tests) before feature endpoints.
3. Optional: the test-architecture skills (`bmad-tea`) for the calc-engine test strategy (NFR-1 — the heart of the product).

### Final Note
This assessment found 4 issues across 2 categories (dependencies + minor consistency); **all were resolved during the assessment**. The planning chain (PRD → UX → Architecture → Epics) is coherent, complete, and ready for Phase 4 implementation.

**Date:** 2026-06-16 · **Assessor:** Implementation Readiness check (BMad)
