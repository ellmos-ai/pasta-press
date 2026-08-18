# PastaPress Roadmap

## Geplante Features

- [ ] **Smart Code/Tag Filtering:** Problematische Stellen (z. B. Quellcode, LaTeX-Commands, HTML-Tags) automatisch herausfiltern, sodass diese erst gar nicht an das LLM übermittelt werden. Ein-/ausschaltbar über eine neue Config-Einstellung ('on/off').

  *Empirische Begründung (E2E-Test 2026-08-18, echtes Forschungs-LaTeX durch
  Übersetzung + Paraphrase mit qwen3.6:35b-mlx):* Das Tool selbst arbeitet
  verlustfrei, aber das LLM beschädigt LaTeX **innerhalb** von Chunks. Konkret
  beobachtet und vom Filter zu verhindern:
  1. Markdown-Codefences (```latex) um LaTeX-Blöcke — akkumulieren über
     Pressdurchgänge (0 → 2 → 4 Fence-Marker).
  2. Chunk-übergreifende Umgebungen: Leerzeile zwischen `\item`s = Chunk-Grenze;
     das Modell schließt offene Umgebungen eigenmächtig (7 `\begin` vs. 9 `\end`
     nach einem Durchgang → "lonely \item", kompiliert nicht).
  3. Verlust von Mathe-Delimitern (`$\tanh$` → `\tanh` im Textmodus).
  4. Tokenizer-Artefakte (CJK-Klammer `】` statt `}` in einer `\subsection`).
  5. Sprachdrift in LaTeX-Kommentaren (bereits übersetzter `%`-Block wurde beim
     zweiten Durchgang teils zurück ins Englische gedreht).

  Minimallösung: geschützte Blöcke (`\begin{...}...\end{...}`, `$...$`, `%`-Zeilen,
  Präambel-Kommandos) als Platzhalter am LLM vorbeischleusen und danach
  reinsetzen; Chunk-Grenzen nie innerhalb offener Umgebungen legen.

- [ ] **Warnung vor Mehrfach-Pressung:** Ein bereits gepresster Text sollte nicht
  erneut gepresst werden (Stille-Post-Effekt: Fehler propagieren UND akkumulieren,
  s. o.). Erkennbar z. B. über eine Marker-Zeile/Metadatei oder den Output-Suffix.
