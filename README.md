## Aufgabenstellung – Python-Umsetzung mit Flask

Das Programm dient der Verwaltung von Mitarbeitern und Kunden im Kontext der Weihnachts-Post.

Es soll in Python umgesetzt werden, mit einer Web-basierten Benutzeroberfläche (UI) über Flask, sodass es plattformunabhängig und anwenderfreundlich nutzbar ist.

Die Daten sollen zukunftssicher und zuverlässig gespeichert werden. Dazu wird eine relationale Datenbank (SQLite) empfohlen, statt CSV-Dateien:

### SQLite ermöglicht:

- Dauerhafte Speicherung von Daten
- Einfache Erweiterung bei neuen Feldern
- Sichere Abfragen und Filterungen
- Automatisierung von Drucken und Versandlisten

CSV wäre nur für den Import/Export von Daten geeignet, ist aber für große Datenmengen oder komplexe Beziehungen (Mitarbeiter ↔ Kunden ↔ Postarten) weniger geeignet.

## Funktionsumfang

### Mitarbeiterverwaltung

- Mitarbeiter anlegen, bearbeiten, löschen

**Attribute:**

- Unique_ID
- Anrede
- Vorname
- Name
- Abteilung
- Position
- Telefon

### Kundenverwaltung

- Kunden anlegen, bearbeiten, löschen
- Kunden importieren aus CSV oder MSG-Dateien

**Attribute:**

- Unique_ID
- Anrede
- Titel
- Vorname
- Nachname
- Strasse
- Postleitzahl
- Ort
- Land
- Anschriftswahl Privat/Firma
- Firma1
- Firma2
- Abteilung
- Funktion
- Telefon/beruflich
- Durchwahl Büro
- Mobiles Telefon
- Faxnummer
- Telefon/privat
- Email-Name
- Anmerkungen

**Liste aus Jahren:**

- Physische Post
- Digitale Post
- Spezielle Post

- Zuweisung von Kunden zu Mitarbeitern
- Alle Kunden eines Mitarbeiters auflisten
- Auswahl der Art der Weihnachtspost für jeden Kunden

### Weihnachtspostverwaltung

- Auswahl der zu druckenden oder zu versendenden Post pro Mitarbeiter
- Unterstützung für physische Post (Postkarte, Kalender) und digitale Post (E-Mail) sowie spezielle Gestaltung

### Benutzeroberfläche (UI)

- Flask-Webanwendung
- Intuitives Dashboard für Mitarbeiter- und Kundenübersicht
- Formulare für Anlegen, Bearbeiten und Löschen von Datensätzen
- Filter- und Suchfunktion für Kunden und Mitarbeiter
- Auswahl und Druck/Export von Postlisten