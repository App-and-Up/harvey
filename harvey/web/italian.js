// Presentation-only translations. API keys, signal codes and stored data stay unchanged.
const IT_SIGNALS = {
  SERP_RANK: ['Posizione nei risultati di ricerca', 'Posizione dell’azienda per la ricerca principale «servizio città». Le posizioni 11–30 indicano una presenza visibile ma ancora fuori dalla prima pagina; nelle prime 10 la visibilità è già alta, oltre la 30 è più bassa.', '~0,0006 USD per ricerca (API SERP a pagamento, elaborazione in coda)'],
  FOUND_IN_SERP: ['Trovata tramite ricerca', 'L’azienda è comparsa in una ricerca relativa al mercato di riferimento: indica come Harvey l’ha individuata.', 'incluso nella ricerca precedente'],
  NO_WEBSITE: ['Sito web assente', 'L’azienda ha una scheda e un numero di telefono ma nessun sito. È un criterio ricercabile direttamente, utile a chi vende siti web.', 'incluso nella ricerca delle schede aziendali'],
  UNCLAIMED_LISTING: ['Scheda Google non rivendicata', 'Nessuno ha rivendicato il Profilo dell’attività su Google. Può indicare scarsa gestione della presenza locale ed essere utile a chi propone marketing locale.', 'incluso nella ricerca delle schede aziendali'],
  REVIEW_RATING: ['Valutazione delle recensioni', 'Media delle stelle ricevute. Una valutazione bassa può indicare problemi di reputazione; una alta con poche recensioni può indicare qualità poco visibile.', 'incluso nella ricerca delle schede aziendali'],
  REVIEW_COUNT: ['Numero di recensioni', 'Numero di recensioni ricevute: un’indicazione approssimativa delle dimensioni e dell’attenzione alla presenza online.', 'incluso nella ricerca delle schede aziendali'],
  INCUMBENT_AGENCY: ['Agenzia web o marketing presente', 'Un’agenzia è citata nei crediti del sito, per esempio «Sito realizzato da X». Il dato viene registrato solo con una dicitura esplicita, per evitare attribuzioni errate.', 'gratuito (HTML della pagina iniziale)'],
  RUNNING_GOOGLE_ADS: ['Tag Google Ads presente', 'Il sito contiene un tag Google Ads: un indizio di investimento nell’acquisizione clienti.', 'gratuito (HTML della pagina iniziale)'],
  RUNNING_META_ADS: ['Pixel Meta/Facebook presente', 'Il sito contiene un Meta Pixel: un indizio di utilizzo della pubblicità sui social.', 'gratuito (HTML della pagina iniziale)'],
  TECH_STACK: ['Piattaforma e strumenti del sito', 'Tecnologie e strumenti presenti sul sito, come WordPress, Shopify, HubSpot, chat e sistemi di prenotazione.', 'gratuito (HTML della pagina iniziale)'],
  NO_SCHEMA_MARKUP: ['Dati strutturati assenti', 'Non è stato rilevato markup JSON-LD: una possibile lacuna SEO verificabile.', 'gratuito (HTML della pagina iniziale)'],
  NO_ONLINE_BOOKING: ['Prenotazioni online assenti', 'Non è stato rilevato uno strumento di prenotazione o gestione appuntamenti. Può indicare che per prenotare sia necessario telefonare.', 'gratuito (HTML della pagina iniziale)'],
  SITE_PAGE_COUNT: ['Dimensioni del sito', 'Numero di pagine ricavato da sitemap.xml. Un sito ridotto può indicare investimenti limitati; uno ampio ma non aggiornato può suggerire scarsa manutenzione.', 'gratuito (sitemap.xml)'],
  BLOG_STALE: ['Contenuti non aggiornati', 'Non risultano nuovi contenuti da molto tempo: possibile attività editoriale avviata e poi abbandonata.', 'gratuito (sitemap.xml)'],
  BLOCKS_AI_CRAWLERS: ['Crawler AI bloccati', 'Il file robots.txt blocca i crawler AI: può limitare l’accesso ai contenuti da parte di questi sistemi.', 'gratuito (robots.txt)'],
  HIRING_ROLE: ['Ricerca di personale per un ruolo pertinente', 'Un annuncio nella pagina Lavora con noi segnala un ruolo potenzialmente collegato al bisogno del prodotto.', 'gratuito (pagina Lavora con noi)'],
  CONTACT_FOUND: ['Referente identificato', 'Una persona con nome e ruolo è stata trovata nella pagina del team o di presentazione dell’azienda.', 'gratuito (pagina del team)'],
  DECISION_MAKER_TITLE: ['Ruolo decisionale', 'Il ruolo corrisponde a un possibile decisore: titolare, presidente, responsabile o direttore marketing.', 'gratuito (pagina del team)'],
  REGISTRY_VERIFIED: ['Confermato in un registro pubblico', 'La persona è stata verificata in un registro pubblico autorevole, come un albo professionale. Aiuta anche a scartare errori di estrazione. La raccolta da registri pubblici è ancora in sviluppo.', 'gratuito (API del registro pubblico)'],
  LIKELY_OWNER: ['Probabile titolare', 'Gli indicatori del registro suggeriscono che la persona sia titolare dell’attività. La raccolta da registri pubblici è ancora in sviluppo.', 'gratuito (API del registro pubblico)'],
  EMAIL_PATTERN: ['Formato email aziendale', 'Formato degli indirizzi del dominio, per esempio nome.cognome@ oppure inizialenomecognome@. Un indirizzo noto può permettere di ricavare il formato.', 'gratuito oppure circa 1 credito di ricerca'],
  EMAIL_STATUS: ['Recapitabilità dell’email', 'Indica se l’indirizzo è verificato, rischioso perché il dominio accetta ogni indirizzo, non verificato oppure non valido.', '1 credito di verifica (sono disponibili quote gratuite)'],
  CONTACT_FORM_URL: ['Modulo di contatto disponibile', 'Il sito contiene un modulo di contatto: un recapito alternativo quando non è disponibile un indirizzo email verificato.', 'gratuito (HTML del sito)'],
};

const IT_CATEGORIES = {
  discovery: ['Ricerca — quali aziende esistono', 'Come Harvey individua le aziende e ne valuta la visibilità. Questa fase può utilizzare fonti a pagamento.'],
  profile: ['Analisi — cosa fanno le aziende', 'Lettura delle pagine pubblicate dall’azienda. Nessun costo per chiamate al modello: i fatti raccolti rendono i messaggi più specifici.'],
  people: ['Referenti — chi decide', 'Le persone identificate e gli elementi che ne indicano il ruolo decisionale.'],
  verification: ['Recapiti — come contattarle', 'Verifica della recapitabilità degli indirizzi e dei recapiti alternativi.'],
};

const IT_PROVIDERS = {
  osm: {
    blurb: 'Dati cartografici pubblici gratuiti. Nessuna registrazione, chiave o carta: puoi provare la raccolta senza acquistare crediti.',
    cost_note: 'gratuito', free_tier: 'senza costo, nel rispetto dei limiti della comunità',
    caveat: 'La copertura delle attività prive di sede aperta al pubblico è limitata: OpenStreetMap descrive soprattutto luoghi fisici. Utile per una prova o un confronto, ma non è un elenco completo.',
  },
  dataforseo_listings: {
    label: 'DataForSEO — schede aziendali',
    blurb: 'Cerca attività di un tipo in un raggio geografico, con telefono, dominio, valutazione e stato della scheda. Adatto alla ricerca di attività locali.',
    cost_note: '0,372 USD per 1.000 aziende (0,012 USD/ricerca + 0,00036 USD/azienda)',
    free_tier: '1 USD di credito iniziale; deposito minimo di 50 USD per l’uso reale',
    caveat: 'Non fornisce indirizzi email: Harvey li cerca in una fase successiva.',
  },
  dataforseo_serp: {
    label: 'DataForSEO — posizione su Google',
    blurb: 'Cerca «servizio città» e registra la posizione di ogni azienda. Trova nuove aziende e raccoglie dati su quelle già note.',
    cost_note: '0,0006 USD ogni 10 risultati — 30 risultati costano 0,0018 USD per ricerca',
    free_tier: '1 USD di credito iniziale; ambiente di prova gratuito; deposito minimo di 50 USD',
    caveat: 'La profondità aumenta il costo: 100 risultati costano dieci volte 10 risultati. Una profondità di 20–30 limita la spesa e riduce i risultati costituiti da elenchi e portali.',
  },
  serper: {
    blurb: 'Ricerca Google veloce con posizioni dei risultati. Per iniziare: 2.500 ricerche gratuite, senza carta di credito, con una sola chiave API.',
    cost_note: 'circa 0,30–1,00 USD per 1.000 ricerche, secondo il pacchetto',
    free_tier: '2.500 ricerche gratuite, senza carta di credito',
    caveat: 'Pacchetti prepagati da 50 USD; i crediti scadono dopo 6 mesi.',
  },
};

const IT_SETUP = {
  venv: ['Ambiente virtuale Python', 'Esegui: python3 -m venv .venv && source .venv/bin/activate && pip install -e .'],
  env_file: ['File delle credenziali (.env)', 'Apri Impostazioni per inserire le credenziali dei servizi.'],
  email_provider: ['Servizio email configurato', 'Per Gmail: salva ID client e segreto nelle Impostazioni, poi esegui harvey gmail auth nel terminale. Per SMTP/IMAP: configura server e credenziali.'],
  verifier: ['Servizio di verifica email', 'Aggiungi una chiave Reoon, ZeroBounce o Hunter nelle Impostazioni. Senza verifica, gli indirizzi ipotizzati non vengono usati per gli invii.'],
  config: ['Configurazione di Harvey', 'Prepara il prodotto con harvey train https://tuosito.it oppure compila la configurazione locale.'],
  product_trained: ['Conoscenza del prodotto disponibile', 'Esegui harvey train https://tuosito.it oppure prepara manualmente skills/product_knowledge.md. La presenza del file non certifica l’esecuzione del training.'],
  linkedin: ['Credenziali LinkedIn', 'Facoltative. Puoi cercare contatti sul web senza automatizzare LinkedIn.'],
  cloudflare: ['Analisi approfondita con Cloudflare', 'Facoltativa: permette di leggere siti che richiedono JavaScript durante il training.'],
};

const IT_TERMS = {
  codex: 'Codex', claude: 'Claude', main: 'Ciclo automatico', trainer: 'Preparazione prodotto',
  scout: 'Ricerca contatti', writer: 'Scrittura', sender: 'Invio', handler: 'Gestione risposte', analyst: 'Analisi', harvey: 'Harvey', system: 'Sistema', brain: 'Modello',
  discover: 'Ricerca aziende', discovery: 'Ricerca aziende', profile: 'Analisi siti', prospect: 'Ricerca contatti', analyze: 'Analisi', idle: 'In attesa',
  send_campaign: 'Invio campagna', send_campaigns: 'Invio campagne', write_campaign: 'Scrittura campagna', write_campaigns: 'Scrittura campagne', handle_replies: 'Gestione risposte', read_replies: 'Lettura risposte', send_outbox: 'Invio coda',
  stage_campaign: 'Preparazione invii', email_sent: 'Email inviata', opt_out: 'Interruzione dei contatti', escalation: 'Richiesta di intervento umano', bounce: 'Email non recapitata', reply_queued: 'Risposta in coda',
  classify_intent: 'Classificazione risposta', generate_response: 'Preparazione risposta', personal_email: 'Email personalizzata', write_sequence: 'Scrittura sequenza', known_company_backfill: 'Contatti delle aziende già note', job_board: 'Portale di lavoro',
  score_contacts: 'Valutazione contatti', initial_outreach: 'Primo contatto', engaged: 'Conversazione avviata', qualifying: 'Qualifica', presenting: 'Presentazione', negotiating: 'Trattativa', closing: 'Conclusione',
  sequence: 'Sequenza', campaign: 'Campagna', reply: 'Risposta', follow_up: 'Sollecito', followup: 'Sollecito', outreach: 'Primo contatto',
  website: 'Sito web', web_search: 'Ricerca web', company_website: 'Sito aziendale', team_page: 'Pagina del team', known_companies: 'Aziende già note', hiring_boards: 'Annunci di lavoro', hiring: 'Ricerca personale', linkedin_search: 'Ricerca LinkedIn', hunter_domain_search: 'Ricerca dominio Hunter',
  listings: 'Schede aziendali', serp: 'Risultati di ricerca',
};

function uiTerm(value) {
  return IT_TERMS[value] || value || '';
}

function uiText(value) {
  if (value === null || value === undefined) return '';
  let text = String(value);
  const messages = {
    'compliance.postal_address is not set in harvey.yaml': 'Indirizzo postale mancante: configura compliance.postal_address in harvey.yaml.',
    'compliance.opt_out_line is not set in harvey.yaml': 'Frase per interrompere i contatti mancante: configura compliance.opt_out_line in harvey.yaml.',
    'postal address footer missing': 'Indirizzo postale mancante nel messaggio.',
    'opt-out footer missing': 'Frase per interrompere i contatti mancante nel messaggio.',

    'ChatGPT returned an incomplete or invalid text response.': 'ChatGPT ha restituito una risposta di testo incompleta o non valida.',
    'ChatGPT text endpoint redirect refused.': 'Il reindirizzamento del servizio di testo ChatGPT è stato rifiutato.',
    'ChatGPT text service is temporarily unavailable.': 'Il servizio di testo ChatGPT non è disponibile al momento.',
    'ChatGPT refused the text request.': 'ChatGPT ha rifiutato la richiesta di testo.',
    'ChatGPT returned a different model; no substitution is allowed.': 'ChatGPT ha restituito un modello diverso da quello scelto. La risposta è stata rifiutata.',
    'Codex text call timed out.': 'La chiamata di testo a Codex ha superato il tempo massimo.',
    'Codex text connection failed.': 'La connessione al servizio di testo Codex non è riuscita.',
    'Your Codex login has expired.': 'Il login Codex è scaduto.',
    'paused manually': 'sospeso manualmente',
    'paused from dashboard': 'sospeso dal pannello',
    'stopped from dashboard': 'interrotto dal pannello',
    'a run is already going': 'Un’operazione è già in corso.',
    'Harvey is already running.': 'Harvey è già in esecuzione.',
    'Harvey is not running.': 'Harvey non è in esecuzione.',
    'API key is required.': 'La chiave API è obbligatoria.',
    'no signal codes given': 'Non è stato specificato alcun segnale.',
    'budget cap': 'limite di spesa',
    'spend cap': 'limite di spesa',
    'no confirmed discovery signals': 'nessun segnale di ricerca confermato',
    'No confirmed discovery signals': 'Nessun segnale di ricerca confermato',
    'failed': 'non riuscita',
    'not configured': 'non configurato',
    'over budget': 'stima oltre il limite di spesa',
    'no confirmed signals': 'nessun segnale confermato',
    'paused': 'in pausa',
    'budget reached': 'limite di spesa raggiunto',
    'No API key provided.': 'Non è stata inserita una chiave API.',
    'Connected to Instantly.': 'Connessione a Instantly riuscita.',
    'Invalid request body.': 'La richiesta non è valida.',
    'Could not write .env file.': 'Impossibile salvare il file .env.',
    'Comment is required.': 'Inserisci una nota.',
    'Could not save feedback.': 'Impossibile salvare la nota.',
    'unknown action': 'Azione sconosciuta.',
    'recipient does not match the prospect record': 'Il destinatario non corrisponde al contatto registrato.',
    'empty subject': 'Oggetto vuoto.',
    'empty body': 'Testo del messaggio vuoto.',
    'HTML markup in body (plain text only)': 'Il messaggio contiene HTML: è consentito solo testo semplice.',
  };
  if (messages[text]) return messages[text];
  text = text.replace(/paused manually/g, 'sospeso manualmente')
    .replace(/paused from dashboard/g, 'sospeso dal pannello')
    .replace(/Nothing will go out until you resume it\./g, 'Nessun messaggio partirà finché gli invii non saranno riattivati.')
    .replace(/Email provider configured \(([^)]+)\)/g, 'Servizio email configurato ($1)')
    .replace(/Email verification key/g, 'Servizio di verifica email')
    .replace(/Python virtual environment/g, 'Ambiente virtuale Python')
    .replace(/Environment file \(.env\)/g, 'File delle credenziali (.env)')
    .replace(/Harvey configured \(([^)]+)\)/g, 'Configurazione di Harvey ($1)')
    .replace(/Product knowledge trained/g, 'Conoscenza del prodotto disponibile');
  text = text.replace(/^Codex model '([^']+)' always exposes tools that Harvey cannot disable \(code mode \(([^)]+)\)\), so Harvey won't send it prompts\. Set brain.model in harvey.yaml\.$/,
    'Il modello Codex «$1» espone strumenti integrati che Harvey non può disabilitare (modalità $2). L’integrazione attuale non può usarlo e non invierà istruzioni al modello.');
  text = text.replace(/^Failed to start Harvey: /, 'Impossibile avviare Harvey: ')
    .replace(/^Failed to stop Harvey: /, 'Impossibile arrestare Harvey: ')
    .replace(/^unknown provider /, 'Servizio sconosciuto: ')
    .replace(/^invalid status: /, 'Stato non valido: ')
    .replace(/^Invalid action: /, 'Azione non valida: ')
    .replace(/^API returned (\d+)\. Check your key\.$/, 'Il servizio ha restituito il codice $1. Controlla la chiave API.')
    .replace(/^Connection failed: /, 'Connessione non riuscita: ')
    .replace(/^invalid recipient address '(.*)'$/, 'Indirizzo del destinatario non valido: $1')
    .replace(/^email_status '(.*)' is not deliverable$/, 'Lo stato email «$1» non consente l’invio.')
    .replace(/^subject too long /, 'Oggetto troppo lungo ')
    .replace(/^body too long \((\d+) words > (\d+)\)/, 'Messaggio troppo lungo ($1 parole > $2)')
    .replace(/^unrendered merge tags: /, 'Variabili non sostituite: ')
    .replace(/^banned phrases: /, 'Frasi non consentite: ')
    .replace(/^too many links /, 'Troppi collegamenti ');
  return text;
}

function italianPayload(path, data) {
  if (!data || typeof data !== 'object') return data;
  if (data.message) data.message = uiText(data.message);
  if (data.error) data.error = uiText(data.error);
  if (path === '/api/setup-status' && data.checks) {
    data.checks = data.checks.map(c => {
      const it = IT_SETUP[c.id];
      return it ? {...c, label: it[0], help: it[1]} : c;
    });
  } else if (path === '/api/signals' && data.groups) {
    data.groups = data.groups.map(g => ({
      ...g,
      label: IT_CATEGORIES[g.key]?.[0] || g.label,
      blurb: IT_CATEGORIES[g.key]?.[1] || g.blurb,
      signals: g.signals.map(s => {
        const it = IT_SIGNALS[s.code];
        return it ? {...s, label: it[0], description: it[1], cost_note: it[2]} : s;
      }),
    }));
  } else if (path === '/api/discover/providers' && data.providers) {
    data.providers = data.providers.map(p => ({...p, ...IT_PROVIDERS[p.key]}));
  } else if (path === '/api/today' && data.items) {
    const n = title => Number((title.match(/^\d+/) || [0])[0]);
    const content = {
      paused: ['Invii sospesi', 'Nessun messaggio partirà finché gli invii non saranno riattivati.', 'Controlla gli invii'],
      setup: ['Completa la configurazione di Harvey', 'Apri le impostazioni per completare i collegamenti ai servizi mancanti.', 'Apri impostazioni'],
      'signals-none': ['Nessun segnale confermato', 'Tutti i segnali sono esclusi: la ricerca non ha dati da raccogliere.', 'Controlla i segnali'],
      discover: ['Nessuna azienda presente', 'I segnali sono confermati, ma non è stata ancora eseguita una raccolta. Puoi provare la fonte gratuita senza registrazione.', 'Trova aziende'],
    };
    data.items = data.items.map(item => {
      let copy = content[item.key];
      const count = n(item.title);
      if (item.key === 'signals') copy = [count + (count === 1 ? ' segnale da confermare' : ' segnali da confermare'), 'Harvey raccoglie solo i segnali che approvi. Scegli quelli utili per il tuo cliente ideale.', 'Controlla i segnali'];
      if (item.key === 'profile') copy = [count + (count === 1 ? ' azienda da analizzare' : ' aziende da analizzare'), 'La lettura dei siti raccoglie fatti utili per personalizzare i messaggi, senza chiamate al modello.', 'Analizza i siti'];
      if (item.key === 'outbox') copy = [count + (count === 1 ? ' email da approvare' : ' email da approvare'), 'Nessun messaggio viene inviato senza approvazione. Controllali uno alla volta.', 'Apri i messaggi'];
      if (item.key === 'replies') copy = [count + (count === 1 ? ' conversazione aperta' : ' conversazioni aperte'), 'Sono arrivate risposte. Controlla come le sta gestendo Harvey.', 'Leggi conversazioni'];
      return copy ? {...item, title: copy[0], detail: ['paused', 'setup'].includes(item.key) ? uiText(item.detail) : copy[1], action: copy[2]} : item;
    });
  }
  return data;
}
