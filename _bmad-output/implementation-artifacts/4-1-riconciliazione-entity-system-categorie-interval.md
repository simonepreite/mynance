---
baseline_commit: badb988
---

# Story 4.1: Riconciliazione entity, "non identificato" system Categorie, reminder-interval (FR-16)

Status: done

## Summary
- **riconciliazioni** table (UUID PK, utente_id indexed, liquidita_reale/calcolata/drift cents BIGINT, data_riconciliazione, esito enum chiusa|acknowledged_open, soft-delete) + index ix_riconciliazioni_utente_id_data_riconciliazione. Migration b6c7d8e9f0a1.
- System "non identificato" Categorie (one Spesa + one Entrata, **is_system**) provisioned on registration; appear in the typed lists; rename/delete blocked (422).
- Per-Utente **intervallo_riconciliazione_giorni** (default 7); GET/PUT /riconciliazione/intervallo (ge=1 → 422 otherwise).
- Per-Utente isolation on all reads/writes.

## Files
**Added:** backend/app/api/routes/riconciliazione.py, backend/app/alembic/versions/b6c7d8e9f0a1_*.py, backend/tests/api/test_riconciliazione.py
**Modified:** backend/app/models.py, backend/app/crud_categoria.py (provision_system_categorie/get_system_categoria), backend/app/api/routes/auth.py, backend/app/api/routes/categorie.py (is_system guard), backend/app/api/main.py
