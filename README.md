# Kunden-Benachrichtigungs-App (kundenkommunikation)

Dieses Projekt ist eine Web-Anwendung zur Verwaltung von Mitarbeiter- und Kundendaten im Kontext von Post-, E-Mail- und sonstigen Benachrichtigungen.
Sie wurde mit **Python** und dem **Flask-Framework** entwickelt und nutzt eine **SQLite-Datenbank** zur Datenspeicherung.

---

## Funktionsweise & Features

Die Anwendung bietet eine zentrale Oberfläche, um den Überblick über die Kundenkommunikation zu behalten:

- **Mitarbeiterverwaltung:** Anlegen, Bearbeiten und Löschen von Mitarbeitern. Jedem Mitarbeiter kann eine Farbe zur visuellen Erkennung zugewiesen werden.
- **Kundenverwaltung:** Kunden können manuell angelegt, aus Outlook `.msg`-Dateien importiert und bearbeitet werden. Jeder Kunde ist einem Mitarbeiter zugeordnet.
- **Status-System:** Kundenstatus zur Verfolgung des Bearbeitungsfortschritts:
  - Neu 🆕
  - In Ordnung ✅
  - Unklar ❓
  - Fehler ❌
  - Doppelt 🔃
- **Benachrichtigungen pro Jahr:** Pro Kunde kann jährlich festgelegt werden, welche Art von Kommunikation erfolgt (Brief, Kalender, E-Mail, Speziell).
- **Filterbare Übersicht:** Kunden können nach Mitarbeiter, Status oder Benachrichtigungsart gefiltert werden. Spalten sind individuell ein-/ausblendbar.
- **Robuster Import:** Automatische Extraktion von Kontaktdaten aus `.msg`-Dateien (Outlook-Kontakte/Notizen) und Anlage/Aktualisierung von Kunden.

---

## Installation

Die Anwendung ist plattformunabhängig und läuft auf **Windows** und **Linux**.

### Voraussetzungen

- **Python 3.8+** muss installiert sein.
  Prüfen mit:

  ```bash
  python --version
  # oder
  python3 --version
  ```

### Schritte für Windows

1. **Projekt herunterladen/klonen**
   z.B. nach `C:\Projekte\kundenkommunikation`

2. **Terminal öffnen & ins Projekt wechseln**

   ```bash
   cd C:\Projekte\kundenkommunikation
   ```

3. **Virtuelle Umgebung erstellen**

   ```bash
   python -m venv venv
   ```

4. **Virtuelle Umgebung aktivieren**

   ```bash
   .\venv\Scripts\activate
   ```

   → `(venv)` sollte in der Kommandozeile erscheinen.

5. **Abhängigkeiten installieren**

   ```bash
   pip install -r requirements.txt
   ```

6. **Anwendung starten**

   ```bash
   python app.py
   ```

7. **Webbrowser öffnen:**
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### Schritte für Linux

1. **Projekt herunterladen/klonen**
   z.B. nach `~/projekte/kundenkommunikation`

2. **Terminal öffnen & ins Projekt wechseln**

   ```bash
   cd ~/projekte/kundenkommunikation
   ```

3. **Virtuelle Umgebung erstellen**

   ```bash
   python3 -m venv venv
   ```

4. **Virtuelle Umgebung aktivieren**

   ```bash
   source venv/bin/activate
   ```

   → `(venv)` sollte in der Kommandozeile erscheinen.

5. **Abhängigkeiten installieren**

   ```bash
   pip install -r requirements.txt
   ```

6. **Anwendung starten**

   ```bash
   python3 app.py
   ```

7. **Webbrowser öffnen:**
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### Im Netzwerk verfügbar machen

Starte mit zusätzlichem Host-Parameter:

```bash
python app.py --host=0.0.0.0
```

→ Das Terminal zeigt die IP-Adresse an, z.B. `http://192.168.1.10:5000`.

---

## Offene Punkte & Roadmap

- ✅ **Duplikat-Prüfung:** Teilweise umgesetzt (über E-Mail), soll durch Namensabgleich erweitert werden.
- ✅ **Umgang mit leeren Feldern:** Fehlerfreie Verarbeitung leerer Import-Felder (umgesetzt).
- ✅ **Sicheres Löschen von Mitarbeitern:** Kunden bleiben erhalten, Zuordnung wird aufgehoben.
- ⏳ **Backup-System:** Automatisches Backup der DB (`kundenverwaltung.db`) nach wichtigen Aktionen.
- ⏳ **Sicherheit (HTTPS):** Verschlüsselung für Netzwerkbetrieb.
- ⏳ **Benutzerauthentifizierung:** Passwortschutz für die Anwendung.
- ⏳ **Benachrichtigungslisten pro Jahr:** Automatische Übernahme der Kommunikations-Auswahlen vom Vorjahr.
- ⏳ **Zusätzliche Import-Formate:**

  - Excel-Listen (`.xlsx`)
  - Text-Listen (`.csv`, `.txt`)

- ⏳ **Export-Funktionen:**

  - Gefilterte Übersicht als CSV
  - Export als PDF
  - Generierung einer reinen E-Mail-Liste
  - Druckvorlage für Etiketten (z.B. Ultraprip Art. No. 3424)

---

## requirements.txt

Diese Datei listet alle benötigten Python-Pakete auf.
Installation mit:

```bash
pip install -r requirements.txt
```

**Inhalt:**

```plaintext
Flask
Flask-SQLAlchemy
extract-msg
Werkzeug
```
