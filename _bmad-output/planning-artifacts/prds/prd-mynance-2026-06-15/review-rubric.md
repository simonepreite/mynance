# PRD Quality Review — mynance

## Overall verdict

This is a strong, unusually disciplined PRD: it has a real thesis ("accumulate before you spend" + honest manual drift correction instead of bank aggregation), a tightly maintained Italian-domain Glossary, derived-value formulas written inline, and FRs that mostly carry testable consequences. It is decision-ready and well-shaped for a single-builder/early-SaaS product. The risk is concentrated in **done-ness clarity**: a handful of derived-value formulas are reproducible in spirit but not yet unambiguous enough for a calculation engine to be built without inventing rules (month-counting and rounding, the Quota/Saldo coupling, the depreciation time base), and there is **one broken cross-reference plus a genuinely missing FR** for the in-app indicator surface that the product leans on. None of these block downstream work, but they should be fixed in the finalize pass because the calc engine is explicitly named as "the heart of the product."

Gate: **PASS-WITH-FIXES**.

## 1. Decision-readiness — strong

The PRD states decisions as decisions and records what was given up. §8 Resolved Decisions is a real decision log (10 items, each tied to an FR and to `.decision-log.md`), and §5 Non-Goals names the founding trade-off honestly ("No open banking... ever — this is the founding decision, not a missing feature") rather than smoothing it. The manual-entry vs. aggregation trade-off is argued, not dodged (§1, §4.5). §9 Deferred Items names owners (architecture) and explicitly asserts none blocks downstream — a real, falsifiable claim, not a hedge. There are no rhetorical "open questions," because everything raised at drafting was resolved at finalize, which is appropriate for a green-light pass.

### Findings
- **low** No residual open tensions surfaced (§8, §9) — Everything is resolved, which is correct for finalize, but the PRD never flags the one place the model is genuinely fragile under the user's own "honesty" value: re-baselining Liquidità iniziale (FR-12) silently rewrites all historical derived figures and any past Drift interpretation. *Fix:* add one line in FR-12 or §8 noting the trade-off accepted (history is recomputed, not preserved as audited snapshots) so it is a stated decision, not an inferred one.

## 2. Substance over theater — strong

Very little furniture. The two personas (Marco, Elena) each drive distinct requirements — Elena justifies open self-service registration and password recovery (FR-1/FR-3, UJ-3); Marco drives Secchielli, reconciliation, and Patrimonio (UJ-1/2/4). The Vision is product-specific and could not be swapped into another PRD ("of everything I have, how much is already committed... how much am I investing?"). The differentiation is real and Discovery-driven (Secchielli + derived allocation + drift-chasing), and the PRD even refuses an easy moat claim (§5: "not claiming a defensible technical moat"). NFRs (§10) are product-specific (determinism of the calc engine, negative-Saldo must never be clamped) rather than boilerplate.

### Findings
- _None._ Counter-metrics (SM-C1 entry burden, SM-C2 reminder frequency) are the opposite of theater — they actively guard against vanity engagement.

## 3. Strategic coherence — strong

The PRD has a clear thesis and the features serve it as an arc, not a backlog: factual ledger (Movimenti) → forward allocation (Secchielli) → the payoff view (Liquidità allocated/free + buffer) → the honesty mechanism (Drift) → the wider picture (Patrimonio). Success Metrics validate the thesis (trust/sustained-use and "allocation answer always available"), not raw activity — and DAU/MAU is explicitly avoided. MVP scope kind is coherent (problem-solving tool for one operator, with a platform/API spine deliberately added because native apps are a stated future). Counter-metrics are present.

### Findings
- **low** SM-5 traceability is loose (§7) — SM-5 "at least one other Utente adopts" cites "Validates FR-1–FR-4," but FR-4 is data isolation and FR-2 is session; adoption-by-another-user is really evidence for FR-1 (self-service registration) plus the product value as a whole. *Fix:* narrow SM-5's trace to FR-1 (and optionally FR-3 recovery, since a self-service stranger is the one who needs it), or reword to "validates the self-service onboarding path."

## 4. Done-ness clarity — thin (the gating dimension)

Most FRs carry at least one testable consequence, and the derived-value formulas are written inline — which is well above average. But "the calculation engine is the heart of the product" (§10) sets a high bar, and several formulas are reproducible *in spirit* but still need a rule an engineer would otherwise invent. Be unforgiving here per the rubric.

### Findings
- **high** Missing FR for the in-app indicator/notification surface, and a broken cross-reference (§4.4 FR-15 line 226; §4.5 FR-16) — FR-15 says "The warning is an in-app indicator **(see FR-19)**," but FR-19 is "Investimenti (PAC) at contributed capital." No FR actually defines the in-app indicator/warning surface (buffer breach, open Drift, negative Saldo) that FR-15, FR-16, and the honesty principle (§12) all depend on. *Fix:* add an FR (e.g. "FR-23: In-app indicators & warnings") defining how warnings/reminders are surfaced and dismissed, and repoint FR-15's reference to it; at minimum correct "see FR-19" to the reminder FR-16.
- **high** `mesi_alla_Prossima_scadenza` is underspecified for the Quota formula (§4.3 FR-9/FR-11) — Quota = `max(0,(Importo previsto − Saldo)/mesi_alla_Prossima_scadenza)` divides by a months count "derived from Prossima scadenza and today," but the PRD never says whether it is rounded up, down, or fractional, nor what happens when it is ≤ 0 (due date today/past) — a division-by-zero / negative-divisor hazard the engine must handle. *Fix:* define it explicitly, e.g. `mesi = max(1, ceil((Prossima scadenza − today)/30.44))`, and state the past-due behavior (clamp to 1 month / demand full shortfall now).
- **high** Quota/Saldo coupling is circular without a stated evaluation order (§4.3 FR-9 + FR-10) — Quota depends on Saldo (FR-9), and Saldo is credited from Quota each elapsed period and is "derived-on-read from (start date, Quota history, linked Spese)" (FR-10). With Quota recomputed when inputs change, "Quota history" and "current Quota from current Saldo" can chase each other; the deterministic resolution order is not specified. *Fix:* state the order of evaluation — e.g. Saldo at read time = Σ(credited Quota per elapsed period using the Quota in force during that period) − Σ linked Spese, and current recommended Quota is computed once from that Saldo for the remaining months — with a worked example in the calc-engine test spec (§10 already asks for worked examples).
- **medium** Depreciation time base `anni_trascorsi` is undefined (§4.6 FR-21) — Current value = `max(0, prezzo × (1 − Svalutazione × anni_trascorsi))`. Whether `anni_trascorsi` is integer full years, fractional (days/365.25), and whether it is measured from purchase date to today or to year-end, materially changes Patrimonio. *Fix:* specify fractional years from purchase date to today (`(today − purchase date)/365.25`), or state the chosen convention.
- **medium** "trailing window" month boundaries for Spesa media mensile are ambiguous (§4.4 FR-15) — "mean of monthly Spese over a trailing window (default 6 months)" does not define whether months are calendar months or rolling 30-day windows, nor whether the current partial month counts. This directly sizes the Cuscinetto and therefore the buffer warning. *Fix:* define the window as the last 6 *complete* calendar months (or state rolling 182-day mean), and confirm the partial current month is excluded.
- **low** "session... across a session" and weekly reminder lack a precise tick definition (FR-2, FR-16) — both are computed from `today − last event`, which is good and scheduler-free, but "30 days of inactivity" should name what resets the clock (any authenticated request? only writes?). *Fix:* one clause defining the activity event that resets idle timeout.

## 5. Scope honesty — strong

Omissions are explicit and load-bearing. §5 Non-Goals does real work (no aggregation, no account concept, no expense-splitting, no live market value, no advanced auth, no email/push, not paid). §6.2 separates permanent non-goals from deferrals cleanly ("Bank aggregation — permanent non-goal, not a deferral" vs. "Advanced auth — deferred"). §9 indexes deferred items with owners. The honesty principle (§12) is itself a scope commitment to *not* hide uncomfortable truths. Open-items density is low and appropriate for a green-light finalize pass. Note: this PRD does not use inline `[ASSUMPTION]` / `[NOTE FOR PM]` tags — acceptable here because items were resolved into §8/§9 rather than left inline, so there is nothing to roundtrip-index.

### Findings
- **low** EUR-only and Italian-context are decided but their downstream impact on formatting/validation isn't scoped (§8.10, §10) — fine as a constraint, but currency rounding (cents) is unstated and interacts with every formula above. *Fix:* add "amounts stored and computed to 2 decimal places (cents); rounding half-up" to §10 so the calc engine and tests agree.

## 6. Downstream usability — strong

This PRD is built to be source-extracted. The Glossary (§3) is explicit, mandates verbatim term use, and is honored consistently across FRs/UJs/SMs. FR IDs are contiguous and unique (FR-1…FR-22), UJ IDs and SM IDs are clean, and most sections stand alone via Glossary terms rather than "see above." UJs all have named protagonists (Marco/Elena) carrying context inline. The §11 API-as-product-surface section and the §10 determinism NFR give architecture a clear contract. The one defect is the FR-15→FR-19 broken reference noted under Done-ness.

### Findings
- **medium** One unresolved cross-reference (§4.4 FR-15 → FR-19) — repeats the done-ness finding; flagged here only because broken refs are the canonical downstream-extraction failure. *Fix:* as above (repoint to the in-app-indicator FR / FR-16).
- **low** FR-13 vs FR-22 both define Liquidità's role but Patrimonio reuses the symbol Liquidità (current, not initial) (§4.4/§4.6) — consistent, but an extractor pulling §4.6 alone should be told Patrimonio uses *computed* Liquidità (FR-13), not Liquidità iniziale. *Fix:* one parenthetical in FR-22: "Liquidità (computed, FR-13)."

## 7. Shape fit — strong

The shape matches the product. It is a single-operator personal-finance tool that is *also* a multi-user SaaS on a frontend-agnostic API, and the PRD treats it as exactly that hybrid: capability-spec rigor on the calc engine and FRs, plus genuinely load-bearing UJs because there is meaningful UX and a second (non-technical) persona. UJ density is justified, not over-formalized; SMs are usage/trust-based, which fits "personal-but-SaaS-quality." Chain-top expectations (feeds UX → architecture → epics) are met, which is why the done-ness gaps above matter more than they would for a standalone PRD.

### Findings
- _None._

## Downstream-readiness focus (as requested)

- **Every FR testable?** Mostly yes — each FR has a "Consequences (testable)" block. The exceptions are not untestable claims but *under-specified* formulas (FR-9 month count, FR-9/FR-10 evaluation order, FR-21 time base, FR-15 window boundaries) that cannot be turned into a single deterministic test without an added rule. The missing in-app-indicator FR (FR-15→FR-19) is the one true gap.
- **Derived-value formulas unambiguous and reproducible?**
  - **Liquidità** (FR-13): `Liquidità iniziale + ΣEntrate − ΣSpese − ΣCapitale versato` — reproducible (pending cents/rounding rule).
  - **Liquidità allocata** (FR-14): `Σ max(0, Saldo del Secchiello)` — reproducible.
  - **Risparmio libero** (FR-14): `Liquidità − Liquidità allocata` — reproducible.
  - **Quota** (FR-9): `max(0,(Importo previsto − Saldo)/mesi_alla_Prossima_scadenza)` — **ambiguous**: month-count rounding and past-due/zero-divisor undefined; couples with Saldo without stated evaluation order.
  - **Saldo / carryover** (FR-10): derived-on-read from (start date, Quota history, linked Spese) — **needs explicit evaluation order** to be deterministic (the binding architecture constraint is set, the math contract is not).
  - **Cuscinetto** (FR-15): `N × Spesa media mensile`, N=6 default — formula clear; **Spesa media mensile window boundaries ambiguous**.
  - **Depreciation** (FR-21): `max(0, prezzo × (1 − Svalutazione × anni_trascorsi))` — straight-line and floored is clear; **`anni_trascorsi` time base undefined**.
  - **Patrimonio** (FR-22): `Liquidità + Capitale versato totale + ΣValore beni immobili + ΣValore beni mobili` — reproducible (clarify Liquidità = computed).
- **Success Metrics traceable to FRs?** Yes for SM-1 (FR-5/6, FR-16–18), SM-2 (FR-16–18), SM-3 (FR-14/15), SM-4 (FR-9/10/15). **SM-5 trace is loose** (cites FR-1–FR-4; really FR-1).
- **Counter-metrics present?** Yes — SM-C1 (entry burden) and SM-C2 (reminder frequency), each tied to the primary SM it counterbalances. Strong.

## Mechanical notes

- **Broken cross-reference:** FR-15 (line 226) "see FR-19" points to Investimenti, not the intended in-app indicator/reminder FR. Repoint to FR-16 and/or a new indicator FR.
- **ID continuity:** FR-1…FR-22 contiguous and unique; UJ-1…UJ-4, SM-1…SM-5 + SM-C1/C2, API-1…API-3 all clean. No gaps or duplicates.
- **Glossary drift:** none material — Italian domain terms are used verbatim and consistently; `"non identificato"` appears consistently as a special Spesa/Movimento type and as a system Categoria (FR-18) without synonym drift.
- **Assumptions Index roundtrip:** N/A — the PRD uses §8 Resolved Decisions / §9 Deferred Items instead of inline `[ASSUMPTION]` tags; nothing to roundtrip.
- **UJ protagonist naming:** every UJ names Marco or Elena with inline context. Good.
- **Required sections:** all present for this stakes/type (Vision, Target User/JTBD, Glossary, Features+FRs, Non-Goals, MVP Scope, Success Metrics + counter-metrics, NFRs, API surface, Constraints).
