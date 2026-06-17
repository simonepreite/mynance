# Wireframe (v1) — ＋ Aggiungi spesa "al volo" (mobile, hero flow)

Goal: minimum taps. Optimal path = type amount → tap category chip → Salva. Date defaults to today; Secchiello auto-set from the category (FR-5/FR-7). Realizes the entry-burden counter-metric.

```
┌──────────────────────────────┐
│  [ Spesa ] Entrata        ✕  │  default Spesa; toggle to Entrata
│                              │
│           45,00 €            │  amount = focus, numeric keypad up on open
│                              │
│  Categoria                   │
│  [⛽ Trasporti] [🛒 Alimentari]│ recent/most-used chips → 1 tap
│  [🍔 Ristoranti] [＋ altre…] │  "altre" → searchable full list
│                              │
│  📅 Oggi    📝 Nota    🎟 —   │  date=today · note optional · Secchiello
│                              │
│  ┌──────────────────────────┐│
│  │          Salva           ││  one tap → toast "Spesa aggiunta" → home
│  └──────────────────────────┘│
│   1  2  3                    │
│   4  5  6     (tastierino)    │
│   7  8  9                    │
│   ,  0  ⌫                    │
└──────────────────────────────┘
```

- Picking a category linked to a Secchiello updates the 🎟 chip to show it (e.g. "🎟 Assic. auto"); tap to override or clear (FR-5 default + per-Spesa override).
- After Salva: subtle toast confirmation, return to home with the new Spesa reflected.

## Open
- Surface: bottom sheet (rises from ＋, fast, one-handed) vs full-screen modal.
- Does ＋ create both Spesa and Entrata (toggle), or Spesa only (Entrate via Regole ricorrenti / Altro)?

Status: DRAFT — pending user confirmation.
