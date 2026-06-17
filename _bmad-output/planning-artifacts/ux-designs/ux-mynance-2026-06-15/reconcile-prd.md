---
title: Input Reconciliation Review — UX Spines vs Sources
status: review
created: 2026-06-15
reviewer: input-reconciliation
sources:
  - prds/prd-mynance-2026-06-15/prd.md
  - briefs/brief-mynance-2026-06-12/brief.md
  - briefs/brief-mynance-2026-06-12/addendum.md
targets:
  - ux-designs/ux-mynance-2026-06-15/DESIGN.md
  - ux-designs/ux-mynance-2026-06-15/EXPERIENCE.md
---

# Input Reconciliation Review

Verdict: The spines are a strong, high-fidelity translation of the sources — the honesty principle, the warm/comfortable register, and entry-burden minimization are all explicitly carried through — but the founding **accumulate-before-you-spend** philosophy is preserved only mechanically (Secchielli) and is quietly inverted by a spend-tracking default Home, and a few FR surfaces (reporting on "non identificato", Drift sizing relative to Liquidità, re-baselining tone) are under-specified.

Legend: severity | source location | what's missing/weak/distorted in the spines | one-line fix.

## Critical

(none — no source intent is wholly dropped or contradicted.)

## High

- High | brief §"La Soluzione"/§"Vision" + PRD §1 ("accumulate before you spend", "always know how every euro is allocated") | The founding philosophy is carried *mechanically* via Secchielli/allocation, but the **default landing (Home "Mese") is a spend-tracking surface** (Bilancio + Spese-by-Categoria), which frames the product spend-first — the inverse of "accumulate before you spend"; the allocation answer (the actual thesis) is demoted to a tab the user must navigate to. | In EXPERIENCE.md state/IA, give the accumulate-first answer first-class presence on first run and surface a compact allocata/libera glance or an explicit "set aside first" entry path from Home, without moving the canonical split off the Liquidità screen.

- High | PRD §1, brief Executive Summary ("consapevolezza dell'allocazione del patrimonio" is THE differentiator; UJ-3 climax) | The single unifying idea — allocation awareness as the product's reason to exist — is never stated as a guiding experience principle in EXPERIENCE.md (Voice/Tone and Honesty get dedicated sections; allocation awareness does not). It is implemented per-screen but not elevated as the spine's organizing intent. | Add a short "Allocation awareness" framing note to EXPERIENCE.md Foundation so downstream readers treat the allocata/libera answer as the product's spine, not one of several views.

- High | PRD §7 SM-C1 + FR-8 ("auto-generation rules exist to reduce manual logging"; brief §"La Soluzione" recurring Entrate) | **Regole ricorrenti are the PRD's named mechanism to reduce entry burden**, but the spine files them only as a management surface buried in Altro → Impostazioni — their burden-reducing job (the SM-C1 counter-balance) is never surfaced to the user or framed as such. | In EXPERIENCE.md, frame Regole ricorrenti as the entry-burden reducer (e.g. nudge to set up recurring income/PAC during/after onboarding) and make them reachable beyond deep settings.

## Medium

- Medium | PRD FR-18 + §4.5 ("non identificato" Movimenti "can be reported on separately", dedicated system Categoria per type) | The spine asserts they are "reportable separately" (Honesty section) but specifies **no surface that actually reports on them** — Statistiche is explicitly "charts only, no lists", Home is single-period, and the system "non identificato" Categoria has no stated home. The FR's reporting affordance is unspecified. | Name where "non identificato" Movimenti are reviewed (e.g. as a normal `category-row` in Home's list, or a filter in the Categoria detail) so the reporting consequence of FR-18 has a UX surface.

- Medium | addendum §"Liquidità: modello DERIVATO" + PRD SM-2 (Drift "within a low % of Liquidità") | The Riconciliazione flow shows Drift as a signed magnitude (`Scostamento: −87 €`) but never shows it **relative to Liquidità** — the source frames acceptable drift as a small *percentage* of liquidity, and the user's "is this gap OK?" judgment depends on that proportion. | Add the proportional context (e.g. "≈ X% del calcolato") to the Drift display in the Riconciliazione flow.

- Medium | PRD FR-12 §8 ("changing Liquidità iniziale is a re-baselining action, logged, shifts all derived figures") | The spine notes it is "flagged as a logged re-baselining action" but gives **no confirmation/warning tone** for what is effectively a destructive re-baseline of every derived number — inconsistent with the honesty principle's "surface uncomfortable consequences plainly". | Specify a warm confirm step + microcopy for re-baselining that states it shifts all derived figures (consistent with Voice/Tone honesty rules).

- Medium | PRD §1 + brief §"Il Problema" (no "account" concept is a deliberate, philosophy-load-bearing choice; reconciliation = "check actual bank balances") | The spine never makes the **no-account model explicit to the user**, yet the reconcile flow tells the user to "check his actual bank balances" (Flow 2) — a user who has multiple accounts needs the gentle framing that mynance ignores which account money sits in (the whole anti-inflation rationale). | Add a one-line framing in the Riconciliazione flow/onboarding that the real-liquidity figure is the sum across all accounts (mynance has no account concept by design).

- Medium | brief §"Cosa la Rende Diversa" / PRD §4.5 ("the honest, manual alternative to open banking — not a poor surrogate") | Drift detection is implemented faithfully but framed neutrally ("time to reconcile"); the *pride* of the source framing — this is the honest manual alternative, not a degraded substitute for open banking — is absent, risking the reminder reading as a chore (the SM-C2 dismissal risk the PRD warns of). | Add reassuring/positive framing to the reconcile entry (e.g. that confirming reality is what keeps the numbers trustworthy), reinforcing it as a feature, not a nag.

## Low

- Low | addendum §3 ("Beni immobili tend to *appreciate* over time"; brief §"Patrimonio") | The source contrasts mobili (depreciate) vs immobili (appreciate); the spine correctly fixes immobili at static price-paid (per resolved PRD scope) but offers **no acknowledgement** of the appreciation intuition, so a user expecting their house value to move may be confused by the static figure. | Add a brief explanatory caption on Beni immobili ("price paid — no market estimate in V1") so the static value reads as deliberate, not broken.

- Low | PRD §4.3 / addendum §"Caso da tracciare" (Secchiello memory: carryover lowers next cycle's Quota — the "memory" property) | The under-funding (honesty) half of the Secchiello is well surfaced; the **positive "memory"/carryover** half (residuo lowers next Quota — a satisfying, philosophy-affirming moment) is mentioned only in Flow 1 resolution, not as a celebrated state or microcopy. | Add a calm positive-state microcopy for carryover (e.g. "Avanzo di X € — la Quota del prossimo ciclo scende") to make the accumulate-first payoff felt.

- Low | PRD §2.3 (two personas: Marco technical, Elena non-technical / brief secondary user) | The spine's flows use both protagonists, but onboarding is tuned once; the **non-technical adopter's** need for the recovery-code step to be reassuring (not alarming) and for domain terms to be gently introduced is not called out. | Note in Onboarding that domain-term first-encounters get a light gloss for the non-technical persona (terms stay verbatim, but first use is explained).

- Low | PRD §10 NFR ("financial data never silently dropped"; edits/deletes recompute) + FR-5/FR-7 (deleting Categoria in use prompts reassignment) | Edit/delete recompute is covered for Spese; the **Categoria-delete reassignment prompt** (FR-7) is named in Impostazioni but its UX (what the reassignment dialog does) is unspecified at spine level. | Specify the reassignment prompt behavior briefly (offer a target Categoria; never orphan Movimenti).
