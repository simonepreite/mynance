---
title: "Product Brief: mynance"
status: ready
created: 2026-06-12
updated: 2026-06-15
---

# Product Brief: mynance

## Executive Summary

**mynance** è uno strumento di finanza personale che risponde a una domanda a cui le app esistenti non sanno davvero rispondere: *"di tutto quello che ho, quanto è già destinato a qualcosa, quanto è risparmio libero e quanto sto investendo?"* — la **consapevolezza dell'allocazione del patrimonio**.

Non è l'ennesimo tracker di spese né un'app di budget tradizionale. È costruito attorno a un modello mentale preciso: accumulare *prima* di spendere, attraverso "secchielli" di ammortamento che accantonano in anticipo per le spese ricorrenti note, e tenere sempre chiaro quale parte della propria liquidità è già impegnata. I dati si inseriscono manualmente — una scelta deliberata, non un limite — e mynance compensa l'assenza di collegamento bancario con un meccanismo proattivo di rilevamento del *drift*, che ti riporta alla realtà quando i conti smettono di tornare.

Nasce dall'esigenza concreta del suo autore — uno strumento che faccia le cose a modo suo, gratuito perché costruito in proprio — ma è progettato fin dall'inizio come SaaS multi-utente.

## Il Problema

Chi vuole gestire con serietà le proprie finanze personali oggi sceglie tra due categorie di strumenti, entrambe insoddisfacenti per un certo tipo di utente:

- **App con aggregazione bancaria** (collegano i conti automaticamente). Sembrano comode, ma per chi possiede più conti e sposta denaro tra di essi per operare, ogni trasferimento interno viene contato come entrata + uscita. I volumi si gonfiano (entrate apparenti da 11k a fronte di 2k reali) e si finisce per *perdere* il controllo invece di guadagnarlo. Comportano costi, complessità e connessioni che si rompono.
- **App di budget a pagamento** (es. YNAB) che incarnano la giusta filosofia dei fondi di accantonamento, ma costano, sono in inglese, non si adattano al contesto italiano e impongono il *loro* modello.

Sotto entrambe c'è un problema più sottile: **nessuna gestisce bene l'accantonamento predittivo per spese ricorrenti note** (l'assicurazione, il bollo, le tasse) con quota auto-calcolata, memoria del residuo anno su anno e onestà sui casi in cui la previsione si rivela troppo ottimistica. E nessuna risponde alla domanda dell'allocazione: *quanto dei miei risparmi è davvero libero?*

C'è infine il tallone d'Achille di ogni strumento manuale: **smetti di aggiornarlo per due settimane e inizia a mentirti**. Anche l'utente più diligente perde qualche spesa ogni mese.

## La Soluzione

mynance organizza la vita finanziaria personale attorno a tre pilastri — più una vista d'insieme del patrimonio — legati da un'unica idea: sapere sempre come è allocato ogni euro.

**1. Movimenti manuali e categorizzati.** L'utente registra a mano spese (categorizzate liberamente, opzionalmente collegate a un secchiello) ed entrate (tipicamente mensili). Nessun concetto di "conto": si annotano solo i flussi reali, mai i giri interni — il problema dei volumi gonfiati sparisce alla radice.

**2. Secchielli di ammortamento predittivo.** Per ogni spesa ricorrente nota, mynance accantona una quota mensile *fittizia* (allocazione virtuale, il denaro non si sposta davvero): prende l'ultimo importo pagato, lo divide per i mesi al prossimo pagamento e ti dice quanto mettere via. Il secchiello ha **memoria**: il residuo dell'anno precedente abbassa la quota di quest'anno. E ha **onestà**: se la previsione si è rivelata troppo ottimistica e il secchiello va in negativo, te lo dice invece di nasconderlo.

**3. Liquidità viva con rilevamento del drift.** La liquidità è *derivata*: imposti il valore iniziale una volta, poi `liquidità = iniziale + entrate − spese − investito`. mynance mostra in ogni momento quanta liquidità è **già allocata** (nei secchielli) e quanta è **risparmio libero**, avvisando se il risparmio non allocato scende sotto un cuscinetto di sicurezza pari ad almeno **6 mensilità di spese** (calcolato dalle spese registrate). Per tenere il sistema onesto senza collegamento bancario, mynance **insegue il drift**: una notifica periodica (es. settimanale) invita a confermare la liquidità reale, mostra subito le divergenze col calcolato e permette di chiudere il buco — anche con una voce di spesa **"non identificato"** quando non si risale all'uscita.

**4. Patrimonio.** Oltre alla liquidità, l'utente censisce: **investimenti** (PAC con versamenti ricorrenti, tracciati a *capitale versato* — interessa quanto si è investito, non il valore di mercato del portafoglio); **beni immobili** (al prezzo pagato); **beni mobili** (auto, moto…) con svalutazione a percentuali semplici e default indicativi suggeriti. Il patrimonio totale è la somma di liquidità, capitale investito e valore dei beni.

L'accesso è multi-utente con autenticazione semplice (username + password).

## Cosa la Rende Diversa

Onestà prima di tutto: mynance **non** punta a battere YNAB o Monarch sul numero di feature, e non rivendica un vantaggio tecnologico difendibile. I suoi punti di forza sono reali e circoscritti:

- **Accantonamento predittivo fatto come si deve** — la feature nata dal modello mentale dell'autore, raramente ben supportata altrove.
- **Rilevamento del drift** — l'alternativa *onesta e manuale* all'open banking, non un suo surrogato scadente.
- **La vista dell'allocazione** — il filo che trasforma funzioni separate in un prodotto coerente.
- **Gratuito, su misura, nel contesto italiano** — costruito in proprio da chi ha le competenze tecniche e non vuole pagare per questo tipo di strumento.

## Per Chi È

- **Utente primario — l'autore (e chi gli somiglia).** Persone metodiche che vogliono accumulare *prima* di spendere, gestiscono più conti reali, faticano con le app di aggregazione e cercano controllo e chiarezza più che automatismo. Tecnicamente a proprio agio, disposte a un po' di inserimento manuale in cambio di un modello che rispecchia il loro modo di ragionare.
- **Utente secondario — chiunque condivida l'approccio.** mynance è abbastanza generico da servire chi gestisce le proprie finanze con la stessa filosofia di accantonamento e consapevolezza dell'allocazione, anche senza un profilo tecnico. *[ASSUNZIONE: l'apertura ad altri è un obiettivo reale ma successivo; la V1 ottimizza per l'utente primario.]*

## Criteri di Successo

*[ASSUNZIONE — da validare con te: trattandosi prima di tutto di uno strumento personale, i criteri sono di uso reale più che di mercato.]*

- **Lo uso davvero e con continuità.** Il successo n.1: dopo mesi, mynance è ancora aggiornato e mi fido dei suoi numeri.
- **Smetto di perdere spese.** Il drift settimanale tiene la divergenza tra calcolato e reale entro una soglia bassa e accettabile.
- **So sempre quanto è libero.** In qualunque momento distinguo liquidità allocata, risparmio libero e stato del cuscinetto di sicurezza senza fare calcoli a mano.
- **I secchielli reggono.** Le spese ricorrenti note arrivano già coperte; i casi di sforamento sono visibili in anticipo, non a posteriori.
- **(Obiettivo secondario)** Almeno un utente oltre all'autore lo adotta e lo trova utile.

## Ambito (Scope)

*[ASSUNZIONE — proposta di confine V1 da confermare.]*

**Nella V1:**
- Account multi-utente, auth username + password.
- Spese ed entrate manuali, categorizzazione libera.
- Secchielli di ammortamento: quota auto-calcolata, carryover, tracciamento del negativo.
- Liquidità derivata con vista allocato / risparmio libero e cuscinetto ≥ 6 mensilità.
- Drift detection con notifica periodica, riconciliazione e voce "non identificato".
- Patrimonio: liquidità + investimenti (PAC a capitale versato) + beni immobili (prezzo pagato) + beni mobili (svalutazione a % con default).
- **Backend API come nucleo del prodotto:** API definita, documentata e indipendente dal frontend, che espone la stessa logica/dati a qualunque client. **La V1 consegna il frontend web**; le app native seguono su un filone di sviluppo separato (stesso progetto, per condividere il contesto). Il BE nasce frontend-agnostico fin da subito, così che web, app e perfino un eventuale frontend di terzi consumino lo stesso contratto.

**Esplicitamente fuori (almeno per ora):**
- Divisione spese / funzioni sociali (tipo Splitwise).
- Aggregazione bancaria / open banking.
- Valore di mercato reale del portafoglio investimenti (quotazioni live).
- Stima automatica del valore di mercato degli immobili via API esterne (comune, tipo, locali, mq) — *nice-to-have* futuro, eventualmente come semplice nota.
- Autenticazione avanzata (2FA, social login).

## Vision

*[ASSUNZIONE — direzione a 2-3 anni da validare.]*

mynance diventa lo strumento di riferimento per chi gestisce le proprie finanze con l'approccio "accumula prima, spendi dopo": un prodotto coerente su web e mobile nativo, costruito su un'API solida. Le evoluzioni naturali — stima del valore di mercato degli immobili tramite servizi pubblici gratuiti, import dei movimenti per ridurre l'inserimento manuale, suggerimenti più intelligenti sull'allocazione e sul cuscinetto di sicurezza — si innestano tutte sullo stesso nucleo, senza tradire la scelta fondante: l'utente resta padrone dei propri numeri, e l'app lo aiuta a non mentirsi.
