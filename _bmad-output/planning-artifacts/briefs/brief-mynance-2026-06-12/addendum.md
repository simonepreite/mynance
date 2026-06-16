# Addendum — Brief mynance

Dettaglio contribuito dall'utente che eccede lo scopo del brief (1-2 pagine) ma è prezioso per il downstream (PRD, architettura).

## Feature differenziante: "Secchielli" / Sinking funds con forecasting e riconciliazione

Modello mentale dell'utente (Simone): accumula il patrimonio *prima* di una spesa nota e ricorrente, invece di subirla quando arriva.

**Meccanica descritta (esempio: assicurazione auto):**
1. Prende l'ultimo premio pagato e lo divide per le mensilità fino al prossimo pagamento (es. /12).
2. Ogni mese accantona una **quota fittizia** (virtuale — il denaro non viene necessariamente spostato su un conto reale) nel "secchiello" dedicato a quella spesa.
3. All'arrivo della spesa, il secchiello ha già accumulato la copertura → la spesa ha già una destinazione/fonte pianificata.
4. **Carryover:** tipicamente la spesa successiva è inferiore (es. premio assicurativo che cala) → rimane un **residuo** nel secchiello. L'anno successivo il residuo viene considerato: la nuova quota mensile si calcola sottraendo quanto già presente nel secchiello.

**Caso da tracciare esplicitamente — il forecast sbagliato (under-funding):**
- Previsione ottimistica → il secchiello a fine ciclo va **in negativo** (la spesa reale supera l'accantonato).
- L'app deve gestire e rendere visibile questo scenario, non solo il caso "felice".

**Risolto:** i secchielli sono **allocazione VIRTUALE** ("quota fittizia") su denaro reale già posseduto — un layer di organizzazione mentale, NON sotto-conti reali separati.

**Domande aperte su questa feature (da chiarire):**
- Cosa fa l'app quando un secchiello va in negativo? (Solo alert? Suggerisce di attingere da un altro secchiello? Ricalcolo automatico della quota?)
- Relazione tra "secchielli" (pilastro budget) e "patrimonio" (pilastro asset): un secchiello accumulato è parte del patrimonio?

## Vincoli tecnici (contribuiti dall'utente — per PRD/architettura, NON da progettare nel brief)

- **Backend:** API strutturata (servizio centrale unico).
- **Due frontend separati e nativi:**
  - Frontend **web**.
  - App **mobile Android/iOS in linguaggi nativi** — esplicitamente NO framework cross-platform che generano entrambe le app da un'unica codebase (no React Native, Flutter, ecc.).
- Implicazione: l'API deve essere il contratto stabile condiviso dai tre client; design API-first.

**Principio portante (enfasi utente):** il backend È il prodotto.
- API **definita e documentata**, indipendente dal frontend.
- Espone la **stessa logica e gli stessi dati** a tutti i client; la resa (rendering) può differire per piattaforma, la logica no.
- Deve poter essere usata anche da **un frontend di terzi** (chi vuole costruirsi il proprio client).
- **Sequenza di sviluppo:** web prima; app native (Android/iOS) su un **filone separato ma nello stesso progetto/repo** per condividere il contesto. La struttura del BE nasce frontend-agnostica da subito, non adattata al solo web.

## Modello dati: nessun concetto di "conto" (decisione corretta in corsa)

L'utente NON vuole che mynance gestisca più conti. Contesto: con le app di aggregazione, avendo più conti reali (es. conto domiciliazioni ≠ conto pagamenti carta) e spostando denaro tra essi, gli aggregatori contano ogni trasferimento interno come entrata + uscita → volumi gonfiati (es. entrate apparenti di 11k a fronte di 2k reali). Poiché in mynance l'inserimento è manuale, l'utente non registra i giri interni e il problema sparisce alla radice — quindi i conti non servono come entità.

**Modello corretto:**
- Nessuna entità "conto". mynance ignora da quale conto reale provenga il denaro.
- **Spesa:** inserita manualmente dall'utente, categorizzata liberamente, opzionalmente collegata a un secchiello di ammortamento.
- **Entrata:** registrata manualmente dall'utente, tipicamente mese per mese.
- Tipi di movimento previsti al momento: spesa ed entrata (nessun "trasferimento").

## Multi-tenancy & auth (decisione)

- mynance nasce **multi-tenant dalla V1**: account utente con isolamento dati.
- Autenticazione iniziale **semplice: username + password**.
- Posizione utente sul GDPR: rischio percepito basso perché l'utente inserisce numeri potenzialmente anche fittizi.
  - Nota del facilitatore (parcheggiata, non bloccante per il brief): email/credenziali restano dati personali e password di dati finanziari richiedono comunque hashing robusto e basi minime (privacy policy, cancellazione account). Da valutare in architettura, non da risolvere nel brief.

## Pilastro Patrimonio — modello dettagliato (contributo utente)

La tesi che unifica il prodotto: **consapevolezza dell'allocazione del patrimonio**. Patrimonio totale ≈ Liquidità + Capitale investito + Valore beni fisici.

### 1. Liquidità (il pool centrale)
- L'utente imposta una **quota iniziale** di liquidità.
- Man mano che crea **secchielli**, vede quale parte della liquidità è **già allocata** (e a cosa) e quale resta come **risparmio puro** (non allocato).
- **Avviso cuscinetto di sicurezza:** l'app raccomanda di tenere non allocata almeno **6 mensilità di spese**; la soglia è **calcolata automaticamente dalle spese registrate** dall'utente. Avvisa se il risparmio libero scende sotto questa soglia.
- I secchielli sono quindi porzioni *allocate* della liquidità (risolve la domanda aperta: i secchielli SONO parte del patrimonio liquido, etichettati per destinazione).

### 2. Investimenti — Azioni/ETF / PAC
- L'utente imposta l'importo del proprio **PAC** (Piano di Accumulo Capitale, versamento ricorrente).
- A una certa data il denaro viene **logicamente "spostato"** dal pool liquidità al "conto investimenti".
- **Importante:** interessa **quanto capitale è stato investito** (somma dei versamenti / costo), **NON il valore reale di mercato del portafoglio**. → niente quotazioni live necessarie.

### 3. Beni fisici
- Casa, auto, moto, ecc.
- Distinzione esplicita:
  - **Beni mobili** (auto, moto): si **ammortizzano** — perdono valore nel tempo.
  - **Beni immobili** (casa): tendenzialmente **acquisiscono** valore nel tempo.
- Implica una qualche modellazione dell'andamento del valore nel tempo (deprezzamento / rivalutazione).

### Liquidità: modello DERIVATO + riconciliazione anti-drift (deciso)
- **Liquidità derivata (opzione A confermata):** valore iniziale impostato una volta, poi `liquidità = iniziale + entrate − spese − versato investimenti`.
- **Riconciliazione manuale:** l'utente può allineare il calcolato alla realtà; le uscite non attribuibili si registrano come voce di spesa **"non identificato"**.
- **DRIFT DETECTION (feature di punta, enfasi esplicita dell'utente):** anche utenti diligenti perdono spese ogni mese. mynance deve **segnalare proattivamente il drift**: es. **notifica settimanale** che invita ad aggiornare/confermare l'importo reale della liquidità e mostra subito le **divergenze** rispetto al calcolato, offrendo di chiudere il gap (es. voce "non identificato"). È la risposta manuale e onesta al problema "l'app mente se smetti di inserire", alternativa all'open banking.

### Beni fisici — modello deciso
- **Beni immobili:** l'utente inserisce **solo il prezzo pagato** (prioritario).
  - *Nice-to-have / non prioritario:* stima del valore di mercato in base a caratteristiche dell'immobile (comune, tipo, n. locali, metri quadri), mostrata anche solo come **nota**. Possibile uso di **API di servizi gratuiti** (es. quotazioni immobiliari pubbliche IT tipo OMI/Agenzia delle Entrate — da verificare disponibilità). Candidato a versione futura.
- **Beni mobili:** **percentuali di svalutazione semplici**, con **default indicativi suggeriti in UI**, differenziati per tipo (es. auto vs moto). L'utente resta libero di impostare/sovrascrivere il valore finale.
  - Tassi indicativi suggeribili (da affinare in PRD/UX, solo orientativi): auto ~ −15/20% annuo (primo anno più ripido); moto generalmente svaluta più lentamente, ~ −8/12% annuo (modelli classici possono fare eccezione).

### Vista aggregata
- Patrimonio totale = Liquidità + Capitale investito (PAC, a costo versato) + Valore beni fisici (immobili a prezzo pagato + mobili svalutati).
