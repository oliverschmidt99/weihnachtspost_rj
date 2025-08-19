import os
import csv
import re
import subprocess
import tempfile
import shutil

# Ordner mit MSG-Dateien
msg_folder = os.path.join(os.path.dirname(__file__), "msgDatein")
output_csv = "kontakte.csv"

columns = [
    "Anrede",
    "Titel",
    "Vorname",
    "Nachname",
    "Strasse",
    "Postleitzahl",
    "Ort",
    "Land",
    "Anschriftswahl Privat/Firma",
    "Firma1",
    "Firma2",
    "Abteilung",
    "Funktion",
    "Telefon/beruflich",
    "Durchwahl Büro",
    "Mobiles Telefon",
    "Faxnummer",
    "Telefon/privat",
    "Email-Name",
    "Anmerkungen",
]


def parse_message_txt(text):
    """Liest message.txt-Text und extrahiert Felder"""
    data = {col: "" for col in columns}

    if match := re.search(r"First Name:\s*(.*)", text):
        data["Vorname"] = match.group(1).strip()
    if match := re.search(r"Last Name:\s*(.*)", text):
        data["Nachname"] = match.group(1).strip()
    if match := re.search(r"Full Name:\s*(Herr|Frau)", text):
        data["Anrede"] = match.group(1).strip()
    if match := re.search(r"Job Title:\s*(.*)", text):
        data["Funktion"] = match.group(1).strip()
    if match := re.search(r"Company:\s*(.*)", text):
        data["Firma1"] = match.group(1).strip()
    if match := re.search(r"Business Address:\s*(.*)", text):
        addr = match.group(1).strip()
        if addr_match := re.match(r"(.+),\s*(\d{4,5})\s+(.+)", addr):
            data["Strasse"] = addr_match.group(1).strip()
            data["Postleitzahl"] = addr_match.group(2).strip()
            data["Ort"] = addr_match.group(3).strip()
        else:
            data["Strasse"] = addr
    if match := re.search(r"Business:\s*([+\d\s()/.-]+)", text):
        data["Telefon/beruflich"] = match.group(1).strip()
    if match := re.search(r"Home:\s*([+\d\s()/.-]+)", text):
        data["Telefon/privat"] = match.group(1).strip()
    if match := re.search(r"Mobile:\s*([+\d\s()/.-]+)", text):
        data["Mobiles Telefon"] = match.group(1).strip()
    if match := re.search(r"Fax:\s*([+\d\s()/.-]+)", text):
        data["Faxnummer"] = match.group(1).strip()
    if match := re.search(r"Email:\s*([\w\.-]+@[\w\.-]+)", text):
        data["Email-Name"] = match.group(1).strip()

    return data


def main():
    # 1. Temporären Arbeitsordner anlegen
    temp_dir = tempfile.mkdtemp(prefix="msg_extract_")
    print(f"📂 Temporärer Ordner: {temp_dir}")

    # 2. Alle MSG-Dateien extrahieren
    for filename in os.listdir(msg_folder):
        if filename.lower().endswith(".msg"):
            filepath = os.path.join(msg_folder, filename)
            print(f"🔍 Extrahiere {filename}...")
            subprocess.run(
                ["python", "-m", "extract_msg", "--out", temp_dir, filepath],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    # 3. CSV-Datei schreiben
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()

        # Alle message.txt im Temp-Ordner finden
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower() == "message.txt":
                    file_path = os.path.join(root, file)
                    with open(
                        file_path, "r", encoding="utf-8", errors="ignore"
                    ) as txtfile:
                        text = txtfile.read()
                    row = parse_message_txt(text)
                    writer.writerow(row)
                    print(f"✅ {file_path} verarbeitet")

    # 4. Temp-Ordner löschen
    shutil.rmtree(temp_dir)
    print(f"🗑️ Temporärer Ordner gelöscht.")

    print(f"\n📄 Fertig! CSV gespeichert als: {os.path.abspath(output_csv)}")


if __name__ == "__main__":
    main()
