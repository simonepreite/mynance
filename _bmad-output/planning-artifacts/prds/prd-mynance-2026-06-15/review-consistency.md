# Adversarial Internal-Consistency Review — PRD mynance (2026-06-15)

Reviewer scope: internal consistency only (contradictions, ambiguities, broken cross-references, untestable statements). Source file reviewed: `prd.md` in this directory. No other files consulted.

Verdict: The PRD is largely coherent and the recently changed areas (typed categories, derived-on-read crediting, linear depreciation) are mostly self-consistent, but there is **one Critical broken cross-reference**, **two High double-counting / formula gaps**, and several Medium ambiguities that make a few "testable" consequences not actually testable as written.

---

## Critical

### C-1. Broken cross-reference: FR-15 points to the wrong FR
- **Location:** FR-15, line 226 — "The warning is an in-app indicator (see FR-19), not a blocking action."
- **Problem:** FR-19 is "Investimenti (PAC) at contributed capital" — it has nothing to do with in-app indicators or notifications. There is no FR that defines the in-app indicator/notification surface; the nearest relevant requirement is the in-app reminder in FR-16. The pointer is simply wrong and will mislead a downstream reader/implementer.
- **Fix:** Change "(see FR-19)" to "(see FR-16)" — or, if a dedicated notifications/indicator FR is intended, add it and point there; do not point at the PAC requirement.

---

## High

### H-1. Patrimonio double-counts contributed capital against Liquidità (sign/double-count)
- **Location:** Glossary `Patrimonio` (line 90) + FR-13 (line 211) + FR-22 (line 280) + FR-19 (line 264).
- **Problem:** `Liquidità = Liquidità iniziale + Σ Entrate − Σ Spese − Σ Capitale versato` already **subtracts** capital paid into PACs (a Versamento PAC reduces Liquidità, FR-19 / line 264). `Patrimonio = Liquidità + Capitale versato totale + …` then **adds** that same capital back. Net effect on Patrimonio is zero — which is arguably correct (cash converted to investment is conserved in net worth). BUT FR-22's own anti-double-count note (line 281) only discusses Beni immobili/mobili purchases vs Spese; it never states this Liquidità−Capitale / +Capitale offset is intentional. A reader cannot tell whether the double appearance of Capitale versato is a deliberate conservation identity or an accidental double-count, so the formula is not safely reproducible.
- **Fix:** Add one line to FR-22 (or the `Patrimonio` glossary entry): "Capitale versato is subtracted from Liquidità and re-added here on purpose — net worth conserves cash that became investment; it is not double-counted."

### H-2. Patrimonio component term names don't match their glossary definitions (undefined-term / reproducibility)
- **Location:** Glossary `Patrimonio` (line 90) vs FR-22 formula (line 280).
- **Problem:** The glossary writes `Patrimonio = Liquidità + Capitale versato totale + Valore immobili + Valore beni mobili`; FR-22 writes `… + Σ Valore beni immobili + Σ Valore beni mobili`. The two are meant to be identical but use different tokens ("Valore immobili" vs "Σ Valore beni immobili"), and neither "Valore immobili" nor "Valore beni mobili" is a defined glossary term — only `Bene immobile`/`Bene mobile` are defined, with the depreciated value formula living in FR-21. The summation (Σ) is present in one place and absent in the other. A test author cannot bind "Valore immobili" to a precise stored quantity from the glossary alone.
- **Fix:** Make the two formulas character-identical and define the per-asset value terms: e.g. glossary uses `Σ Valore beni immobili (= price paid)` and `Σ Valore beni mobili (= FR-21 depreciated value)`.

---

## Medium

### M-1. Linear depreciation underspecified at the edges (anni=0, anni fractional, Svalutazione×anni>1)
- **Location:** FR-21 (line 274), Glossary `Svalutazione` (line 96), §8 decision 3 (line 337).
- **Problem:** `Current value = max(0, prezzo × (1 − Svalutazione × anni_trascorsi))`.
  - `Svalutazione×anni > 1` is handled by the `max(0, …)` floor — good, no negative values. OK.
  - `anni = 0` (asset registered today): value = prezzo × (1 − 0) = prezzo. Correct, but only because `anni_trascorsi` is implicitly the elapsed time since purchase date; the PRD never states whether `anni_trascorsi` is integer years, fractional years, or floored to whole years. With integer-floored years a 9-month-old asset shows zero depreciation; with fractional years it depreciates continuously. These give materially different numbers and the "testable" consequence cannot be tested without that decision.
  - No statement of what date drives `anni_trascorsi` (purchase date is captured in FR-21 — good — but "as of today" vs "as of a valuation date" is unstated).
- **Fix:** Add to FR-21: "`anni_trascorsi` = (today − purchase date) in fractional years" (or "in whole elapsed years", pick one) — and state the reference date is today.

### M-2. "Free categorization" wording now contradicts the typed-category model
- **Location:** FR-7 heading "Free categorization (typed) …" (line 152); §4.2 Description "*Spese* are freely categorized" (line 135); §6.1 "free categorization" (line 299); UJ-3 path is fine.
- **Problem:** Categorie are now strictly typed and backend-enforced (FR-7 line 156, Glossary line 74). "Free categorization" is accurate only in the sense "user can create arbitrary labels", but read plainly it implies any Categoria can be applied to any Movimento — which the typed model explicitly forbids. §4.2's "Spese are freely categorized" is the most misleading instance because typing constrains which Categorie are even selectable. This is an internal tension, not a hard contradiction, but it will read as one.
- **Fix:** Replace "free categorization / freely categorized" with "user-defined, type-scoped categorization" (or "free-form labels within their type") in FR-7 heading, §4.2, and §6.1.

### M-3. FR-5 default/override is testable but the "no Secchiello" override vs "Categoria has no link" cases are conflated
- **Location:** FR-5 (lines 140, 142) + FR-7 (line 158).
- **Problem:** FR-5 says the link "can be overridden — to a different Secchiello or to none". The default logic is clear and testable when the Categoria has a linked Secchiello. But when the Categoria has **no** linked Secchiello, the spec is silent on the initial state of the Spesa's Secchiello field (presumably "none", which the user may then set manually). It is also unstated whether an explicit per-Spesa override to "none" is persisted distinctly from "defaulted to none" — relevant because FR-7 line 158 says changing the Categoria's link later affects only future Spese, implying the per-Spesa value is frozen at creation. The frozen-at-creation rule should be stated for the unlinked case too.
- **Fix:** Add a consequence to FR-5: "If the chosen Categoria has no linked Secchiello, the Spesa's Secchiello link defaults to none; in all cases the link value is fixed at record time and later Categoria-link changes do not retroactively alter it (FR-7)."

### M-4. Quota formula vs FR-9 consequences: `Saldo ≥ Importo previsto ⇒ Quota 0` not derivable from the formula at all elapsed states
- **Location:** FR-9 (lines 178–180), Glossary `Quota` (line 77).
- **Problem:** `Quota = max(0, (Importo previsto − Saldo) / mesi)`. The bullet "If Saldo ≥ Importo previsto, Quota is 0" follows directly (numerator ≤ 0 → max(0,…)=0) — consistent. But the bullet "If Saldo is negative, Quota rises to recover the shortfall over the remaining months" is consistent only while `mesi > 0`. There is no defined behavior for `mesi_alla_Prossima_scadenza = 0` (due today) or `< 0` (overdue): division by zero / negative denominator yields undefined or a negative Quota that the outer max clamps to 0, which would silently stop funding an overdue, under-funded bucket — contradicting the "honesty / surface under-funding" principle (FR-10 line 188, §12 line 378).
- **Fix:** Add to FR-9: "When `mesi ≤ 0` (due or overdue), Quota is not divided; the full outstanding `max(0, Importo previsto − Saldo)` is surfaced as immediately-needed, and a negative Saldo continues to be shown as under-funding."

### M-5. Drift "acknowledge without fix" — timer reset wording is consistent with FR-17 but the gap-persistence vs recompute interaction is undertested
- **Location:** FR-18 last bullet (line 252) + FR-17 (line 245) + FR-16 (line 239).
- **Problem:** Internally these are consistent: FR-17 sets last-Riconciliazione = today on confirming reality; FR-18 acknowledge-without-fix "confirms reality and resets the last Riconciliazione date, while the gap stays visible". FR-16 computes the reminder from `today − last Riconciliazione`. No contradiction. **However**, "the gap stays visible as an indicator until it is closed" is not testable as written: after acknowledging, computed Liquidità is unchanged and real Liquidità was only entered transiently — the spec never says the acknowledged real figure (and thus the displayed gap) is **persisted**. If it isn't stored, there is nothing to keep displaying, and subsequent Entrate/Spese would change computed Liquidità while the "gap" has no fixed reference. This makes the acknowledged-gap indicator under-defined.
- **Fix:** Add to FR-18: "Acknowledging persists the entered real Liquidità and its timestamp; the displayed open gap = (persisted real − current computed Liquidità) and updates live until a closing Movimento is recorded." (Decide explicitly whether the gap re-tracks computed changes or is frozen.)

### M-6. System Categoria "non identificato" per-type is consistent, but its interaction with Spesa media is only half-specified
- **Location:** FR-18 (line 251) + FR-15 (line 225) + Glossary `Spesa`/`Categoria`.
- **Problem:** "non identificato" now exists as a system Categoria in **each** type (Spesa and Entrata) — consistent with the typed model (good). FR-15 line 225 states "non identificato" **Spese** are included in Spesa media mensile. It is silent on whether "non identificato" **Entrate** (the FR-18 inflow case) are excluded from anything they could distort — they aren't part of Spesa media (Entrate never are), so this is fine, but a reader checking symmetry will wonder. Minor.
- **Fix:** Optional: add a half-sentence to FR-18 noting "non identificato" Entrate are ordinary Entrate for all derived figures (they raise Liquidità; they do not affect Spesa media).

---

## Low

### L-1. Secchiello crediting "derived-on-read" language is clean — no leftover scheduler contradiction found
- **Location:** FR-10 (line 185), FR-11 Notes (line 195), §8 decision 2 (line 336), §11, FR-16 (line 239), FR-8 (line 166).
- **Observation:** Searched all crediting/reminder/generation language. FR-10 explicitly says "derived-on-read … free of a background scheduler"; FR-16 says the reminder "does not require a background scheduler"; FR-11 Notes and §8.2 repeat the binding constraint; §11 (API-3) says derived values are computed server-side. These are mutually consistent — no leftover "scheduled job" / "each month credits" contradiction remains. One soft tension: UJ-1 (line 47) says mynance "starts crediting it virtually each month" — narratively fine, but a literal reader could read "each month" as periodic writes. Trivial.
- **Fix (optional):** In UJ-1 change "starts crediting it virtually each month" to "accrues the Quota virtually month by month (derived, not a transfer)".

### L-2. §8 decision list is missing item 10's FR tag; decision 10 (Currency) has no FR, which is fine but asymmetric
- **Location:** §8 lines 335–344.
- **Problem:** Decisions 1–9 each cite an FR; decision 10 "Currency — EUR only" cites none (it lives in §10/§5, not an FR). Not an error, just inconsistent presentation.
- **Fix (optional):** Tag decision 10 as "(§10 / §5)".

### L-3. UJ-2 uses "−€87" then FR-17 defines Drift sign as `reale − calcolata` — verify the narrative sign
- **Location:** UJ-2 (line 53) vs FR-17 (line 244).
- **Problem:** UJ-2 shows divergence "(e.g. −€87)" and then closes it with a "non identificato" **Spesa** of €87. If real < computed by €87, then `Drift = reale − calcolata = −87` (matches the narrative) and the fix is indeed a Spesa (lowering computed Liquidità to meet reality). Internally consistent — flagged only to confirm the sign convention is the one intended; it is.
- **Fix:** None required; sign is consistent.

---

## Cross-reference / numbering audit (summary)

- FR numbering 1–22 is sequential, no duplicates, no orphans (verified).
- §-pointers: §5, §8, §9, §10, §11, §12, §2.3 all resolve to existing sections.
- **Broken FR pointer:** FR-15 → "FR-19" should be FR-16 (see C-1). This is the only broken cross-reference found.
- Glossary terms used in FRs are all defined, **except** the Patrimonio component value terms "Valore immobili"/"Valore beni mobili" which are referenced as if defined but only the underlying `Bene immobile`/`Bene mobile` and the FR-21 value formula exist (see H-2).
- SM cross-refs (SM-1..C2 → FRs) all resolve.

## Formula consistency (summary table)

| Formula | Location | Status |
|---|---|---|
| Liquidità = iniziale + ΣEntrate − ΣSpese − ΣCapitale versato | Gloss l82 / FR-13 l211 | Consistent across both |
| Quota = max(0,(Importo previsto−Saldo)/mesi) | FR-9 l178 | Consistent; edge case mesi≤0 undefined (M-4) |
| Liquidità allocata = Σ max(0, Saldo) | Gloss l84 / FR-14 l216 | Consistent; negative Saldo correctly excluded from allocation while still shown per-bucket (FR-10) |
| Risparmio libero = Liquidità − allocata | Gloss l85 / FR-14 l217 | Consistent |
| Cuscinetto = N × Spesa media, N=6 | Gloss l86 / FR-15 l223 | Consistent |
| Depreciation = max(0, prezzo×(1−Svalut×anni)) | FR-21 l274 / §8.3 l337 | Floor handles >1; anni granularity/ref-date undefined (M-1) |
| Patrimonio = Liquidità + Capitale versato + immobili + mobili | Gloss l90 / FR-22 l280 | Token mismatch (H-2) + undocumented Capitale offset (H-1) |
