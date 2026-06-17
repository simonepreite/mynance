# Wireframe (v2) — Home "Mese" (mobile)

Supersedes v1. Per decision-log #13/#14/#15: period-selectable; Spese grouped by Categoria, sorted desc by total, drill into category for detail; no other choices for now.

```
┌──────────────────────────────┐
│ [Giorno][Sett.][ Mese ][Anno]│  selettore periodo (Mese attivo)
│      ‹   Giugno 2026   ›   👤 │  naviga nel periodo
├──────────────────────────────┤
│ ⚠ È ora di riconciliare    → │  banner contestuale (solo se attivo)
├──────────────────────────────┤
│   BILANCIO · GIUGNO          │
│        Netto   + 480 €       │  netto = numero protagonista (verde/rosso)
│   Entrate 2.100 │ Spese 1.620│
├──────────────────────────────┤
│  Spese per categoria         │  ordine: maggiore → minore
│   🎟 Assicurazioni  620 €▕▔▔▔│  (legata a Secchiello)
│   🛒 Alimentari     540 €▕▔▔ │
│   ⛽ Trasporti      280 €▕▔  │
│   🍔 Ristoranti     180 €▕▔  │
│   …                          │
│        ▸ tap categoria        │
│          → dettaglio spese    │
├──────────────────────────────┤
│  🏠     📊     ＋     💧    ⋯ │  Mese·Statistiche·Aggiungi·Liquidità·Altro
└──────────────────────────────┘
```

Category totals sum to month Spese (620+540+280+180 = 1.620). Bars are proportional to each category's share.

### Drill-down: dettaglio categoria (tap su "Alimentari")
```
┌──────────────────────────────┐
│  ‹  Alimentari · Giugno      │
│     540 €  ·  9 spese         │
├──────────────────────────────┤
│  03 giu  Supermercato  63,20 €│
│  07 giu  Panificio      8,40 €│
│  …                           │
└──────────────────────────────┘
```

## Open
- #16: Home vs Statistiche boundary — does Statistiche become trends/charts across periods (snapshot here, trends there)?

Status: DRAFT — pending user confirmation.
