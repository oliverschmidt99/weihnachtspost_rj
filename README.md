# Weihnachtspost-Verwaltung (weihnachtspost_rj)

Dieses Projekt ist eine Web-Anwendung zur Verwaltung von Mitarbeiter- und Kundendaten im Kontext des jährlichen Weihnachtspost-Versands. Sie wurde mit Python und dem Flask-Framework entwickelt und nutzt eine SQLite-Datenbank zur Datenspeicherung.

---

## Funktionsweise & Features

Die Anwendung bietet eine zentrale Oberfläche, um den Überblick über die Weihnachtspost zu behalten:

- **Mitarbeiterverwaltung:** Du kannst Mitarbeiter anlegen, bearbeiten und löschen. Jedem Mitarbeiter kann eine Farbe zur besseren visuellen Erkennung zugewiesen werden.
- **Kundenverwaltung:** Kunden können manuell angelegt, aus Outlook `.msg`-Dateien importiert und bearbeitet werden. Jeder Kunde ist einem Mitarbeiter zugeordnet.
- **Status-System:** Jeder Kunde hat einen Status (Neu 🆕, In Ordnung ✅, Unklar ❓, Fehler ❌, Doppelt 🔃), um den Bearbeitungsfortschritt zu verfolgen.
- **Weihnachtspost pro Jahr:** Für jeden Kunden kann jährlich festgelegt werden, welche Art von Post er erhalten soll (Postkarte, Kalender, E-Mail, Speziell).
- **Filterbare Übersicht:** Eine mächtige Übersichtsseite ermöglicht das Filtern der Kunden nach Mitarbeiter, Status oder Postart. Die angezeigten Spalten können individuell ein- und ausgeblendet werden.
- **Robuster Import:** Der Import von `.msg`-Dateien (Outlook-Kontakte/Notizen) extrahiert automatisch Kontaktdaten und legt neue Kunden an oder aktualisiert bestehende.

---

## Installation

Die Anwendung ist plattformunabhängig und läuft auf Windows und Linux.

### Voraussetzungen

- **Python 3.8** oder neuer muss installiert sein. Du kannst das im Terminal mit `python --version` oder `python3 --version` prüfen.

### Schritte für Windows

1.  **Projekt herunterladen/klonen:** Lade die Projektdateien in einen Ordner deiner Wahl (z.B. `C:\Projekte\weihnachtspost_rj`).

2.  **Terminal öffnen:** Öffne die Eingabeaufforderung (`cmd`) oder PowerShell. Navigiere in dein Projektverzeichnis:

    ```bash
    cd C:\Projekte\weihnachtspost_rj
    ```

3.  **Virtuelle Umgebung erstellen:** Dies isoliert die benötigten Pakete vom Rest deines Systems.

    ```bash
    python -m venv venv
    ```

4.  **Virtuelle Umgebung aktivieren:** Dies muss in jedem neuen Terminalfenster erneut gemacht werden.

    ```bash
    .\venv\Scripts\activate
    ```

    Deine Kommandozeile sollte nun `(venv)` am Anfang anzeigen.

5.  **Abhängigkeiten installieren:**

    ```bash
    pip install -r requirements.txt
    ```

6.  **Anwendung starten:**

    ```bash
    python app.py
    ```

7.  Öffne deinen Webbrowser und gehe zu **`http://127.0.0.1:5000`**.

### Schritte für Linux

1.  **Projekt herunterladen/klonen:** Lade die Projektdateien in einen Ordner deiner Wahl (z.B. `~/projekte/weihnachtspost_rj`).

2.  **Terminal öffnen:** Navigiere in dein Projektverzeichnis:

    ```bash
    cd ~/projekte/weihnachtspost_rj
    ```

3.  **Virtuelle Umgebung erstellen:**

    ```bash
    python3 -m venv venv
    ```

4.  **Virtuelle Umgebung aktivieren:**

    ```bash
    source venv/bin/activate
    ```

    Deine Kommandozeile sollte nun `(venv)` am Anfang anzeigen.

5.  **Abhängigkeiten installieren:**

    ```bash
    pip install -r requirements.txt
    ```

6.  **Anwendung starten:**

    ```bash
    python3 app.py
    ```

7.  Öffne deinen Webbrowser und gehe zu **`http://127.0.0.1:5000`**.

### Im Netzwerk verfügbar machen

Um die Anwendung für andere im selben Netzwerk zugänglich zu machen, starte sie mit dem zusätzlichen `host`-Parameter:

```bash
python app.py --host=0.0.0.0
```

Das Terminal zeigt dir dann die IP-Adresse an, unter der die Anwendung erreichbar ist (z.B. http://192.168.1.10:5000).

## Offene Punkte & Roadmap

### Folgende Features sind für zukünftige Versionen geplant:

- ✅ Duplikat-Prüfung: Es muss zuverlässig geprüft werden, ob ein Kunde beim Import bereits existiert. (Teilweise umgesetzt über E-Mail, könnte durch Namens-Abgleich erweitert werden).

- ✅ Umgang mit leeren Feldern: Die Anwendung sollte keine Fehler auslösen, wenn importierte Felder leer sind. (Umgesetzt).

- ✅ Sicheres Löschen von Mitarbeitern: Das Löschen eines Mitarbeiters darf nicht die zugehörigen Kunden löschen. (Umgesetzt: Die Zuordnung wird aufgehoben).

- ⏳ Backup-System: Nach wichtigen Aktionen (Löschen, Hinzufügen) sollte automatisch ein Backup der Datenbank (weihnachtspost.db) erstellt werden.

- ⏳ Sicherheit (HTTPS): Die Webseite sollte über HTTPS verschlüsselt sein, besonders im Netzwerkbetrieb.

- ⏳ Benutzerauthentifizierung: Die Anwendung sollte mit einem Passwort geschützt werden.

- ⏳ Postlisten pro Jahr: Für jedes neue Jahr sollten automatisch die Post-Auswahlen des Vorjahres für alle Kunden übernommen und als neue Liste angelegt werden können.

- ⏳ Zusätzliche Import-Formate:

  - Import aus Excel-Listen (.xlsx).

  - Import aus Text-Listen (.csv, .txt).

- ⏳ Export-Funktionen:

  - Export der gefilterten Übersicht als CSV-Datei.

  - Export als PDF-Dokument.

  - Generierung einer reinen E-Mail-Liste (für Newsletter-Tools).

  - Erstellung einer Druckvorlage für Etiketten (z.B. Ultraprip Art. No. 3424).

---

### `requirements.txt`

```text
# Diese Datei listet alle Python-Pakete auf, die für das Projekt benötigt werden.
# Mit dem Befehl `pip install -r requirements.txt` werden sie alle auf einmal installiert.
Flask
Flask-SQLAlchemy
extract-msg
Werkzeug
```
