# Brief → PRD Reconciliation Review

**Reviewed:** 2026-06-15
**Inputs:** `brief.md`, `addendum.md`, `.decision-log.md` (brief folder) vs `prd.md` (this folder).
**Scope:** Verify the PRD preserves the *intent* of the brief — qualitative ideas (philosophy, tone, emotional jobs), concrete commitments/constraints/metrics, scope boundaries, and addendum depth the PRD should at least reference. Intentional brief→addendum routing of technical "how" is NOT flagged. No new scope proposed.

**Overall:** Strong, faithful translation. The core philosophy (accumulate-before-you-spend, anti-aggregation conviction, honesty principle, drift-chasing as a positive stance, the allocation thesis) is preserved and in several places stated more sharply than the brief. Gaps are concentrated in: the forward-looking Vision/roadmap, two non-functional commitments the brief explicitly parked for downstream (GDPR rationale + privacy minimums, indicative depreciation rates), and a couple of secondary framings (the "portfolio / serious technical project" stake; manual-entry-as-a-feature stated as a value rather than only a constraint).

---

## Gaps (one line each)

1. **[High] Forward-looking Vision / roadmap dropped.** Brief §Vision (line 91) + decision log (line 13, "eventuale import"). The brief's 2–3-year direction — property market estimate via free public services, **import of movements to reduce manual entry**, **smarter allocation / safety-buffer suggestions** — is absent; the PRD §1 "Vision" is a product description, not a forward direction, and §6.2 only carries the property-valuation deferral. *Fix:* add a short "Future Direction (post-V1)" note (or extend §9 Deferred Items) naming movement-import and smarter allocation/buffer suggestions as non-V1 evolutions that ride the same core, per brief Vision.

2. **[Medium] GDPR posture + parked privacy minimums not referenced.** Addendum lines 53–54. The brief records the user's explicit stance (GDPR low-risk because entered numbers may be fictitious) AND the facilitator's parked, non-blocking minimums for the architecture phase: **privacy policy** and **account deletion** (plus robust password hashing). PRD §10/§12 cover hashing and "minimize what's stored," but the fictitious-data rationale and the privacy-policy / account-deletion minimums are missing. *Fix:* in §9 (Deferred Items) or §12, reference the addendum's parked privacy minimums (privacy policy, account-deletion) and the GDPR rationale so architecture inherits them.

3. **[Medium] Indicative depreciation rates not carried or referenced.** Addendum line 87 (auto ≈ −15/20% annual, first year steeper; moto ≈ −8/12% annual). FR-21 says "a default rate is suggested by asset type" but drops the concrete indicative numbers and does not point to the addendum for them. *Fix:* in FR-21 (or §9), reference the addendum's indicative per-type rates as the source for UX defaults, so downstream UX doesn't reinvent them.

4. **[Low] "Portfolio / serious technical project" stake omitted.** Decision log line 9 ("Vale anche come progetto tecnico serio/portfolio"). The PRD captures "free, built by author, no monetization" but not that the build itself is also a serious technical/portfolio effort — a real stake that motivates the API-first rigor. *Fix:* one clause in §0 or §7 noting the secondary stake of a serious technical / portfolio project (explains the API-as-product emphasis).

5. **[Low] Manual-entry-as-a-feature stated as constraint, not as a value.** Brief lines 14, 33 ("una scelta deliberata, non un limite"). The PRD frames manual entry well (deliberate, §1; §2.2 Non-Users) but mostly as a trade-off the user accepts, rather than echoing the brief's positive framing that manual entry is *itself* a feature that eliminates inflated volumes at the root. The honesty/control intent survives; the "feature, not limitation" tone is slightly flattened. *Fix:* one phrase in §1 or §4.2 stating manual entry is a deliberate feature (root-cause fix for inflated volumes), not merely a tolerated cost.

6. **[Low] Counter-metric for "entry burden" is well-captured — confirm, not a gap.** Noted as a *positive*: SM-C1/SM-C2 strongly preserve the brief's anti-friction intent and even sharpen it; no action.

---

## Notes (verified present — no action needed)

- **Accumulate-before-you-spend, anti-aggregation conviction, honesty principle, drift-chasing-as-positive-stance, allocation-as-the-thread:** all preserved (PRD §1, §2.1, §4.3, §4.5, §5, §12). The "honesty principle" is elevated to an explicit product value in §12 — stronger than the brief.
- **Open question "is an accumulated Secchiello part of Patrimonio?"** (addendum line 23): resolved correctly — *Liquidità allocata* is part of *Liquidità*/*Patrimonio* (Glossary, FR-14, FR-22).
- **Open question "what happens when a Secchiello goes negative?"** (addendum line 22): substantively resolved — negative *Saldo* surfaced (FR-10), *Quota* rises to recover shortfall (FR-9). The "suggest drawing from another bucket" sub-option is a "how" and its omission is acceptable (not flagged).
- **No-account-concept, no internal transfers, "non identificato", 6-month buffer from registered Spese, derived liquidity option A, PAC at contributed capital, beni mobili/immobili split, API-as-product / web-first / native-on-separate-track:** all faithfully carried.
- Technical "how" routed to addendum (stack, transport, schema, the native-language no-cross-platform constraint) is intentional and correctly excluded — not flagged.
