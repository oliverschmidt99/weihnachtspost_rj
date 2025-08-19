import os
import csv
from extract_msg import Message


def extract_msg_to_csv(root_folder, output_csv):
    """
    Durchsucht einen Ordner und dessen Unterordner nach .msg-Dateien,
    liest die E-Mail-Daten aus und speichert sie in einer CSV-Datei im vorgegebenen Format.
    """

    # Header für die CSV-Datei mit eindeutigen Spaltennamen
    # Die doppelten Namen wurden mit '_1', '_2' etc. umbenannt,
    # um eine korrekte CSV-Struktur zu gewährleisten.
    csv_headers = [
        "folder",
        "subject",
        "date",
        "time",
        "to",
        "from",
        "cc",
        "importance",
        "status",
        "received_from",
        "received_on",
        "subject_1",
        "from_1",
        "to_1",
        "cc_1",
        "importance_1",
        "body",
        "date_1",
        "time_1",
        "received_from_1",
        "received_on_1",
        "subject_2",
        "from_2",
        "to_2",
        "cc_2",
    ]

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()

        for folder_path, _, filenames in os.walk(root_folder):
            for filename in filenames:
                if filename.endswith(".msg"):
                    file_path = os.path.join(folder_path, filename)

                    try:
                        msg = Message(file_path)

                        # Datums- und Uhrzeitinformationen
                        date_str = ""
                        time_str = ""
                        if msg.date:
                            try:
                                # msg-extractor gibt das Datum im Format 'YYYY-MM-DD HH:MM:SS+ZZZZ' zurück
                                # Wir trennen es in Datum und Zeit auf
                                date_time_parts = msg.date.split(" ")
                                date_str = date_time_parts[0]
                                time_str = date_time_parts[1].split("+")[0]
                            except IndexError:
                                date_str = msg.date

                        # Relative Pfadangabe
                        relative_folder = os.path.relpath(folder_path, root_folder)

                        data = {
                            "folder": relative_folder,
                            "subject": msg.subject if msg.subject else "",
                            "date": date_str,
                            "time": time_str,
                            "to": msg.to if msg.to else "",
                            "from": msg.sender if msg.sender else "",
                            "cc": msg.cc if msg.cc else "",
                            # Der Body wird dem Feld 'body' zugeordnet
                            "body": msg.body.strip() if msg.body else "",
                            # Andere Felder, die in den meisten E-Mails nicht direkt vorkommen, bleiben leer
                            # Dies entspricht dem von dir gewünschten Verhalten
                        }

                        # Daten in die CSV-Datei schreiben
                        writer.writerow(data)
                        print(f"Verarbeitet: {file_path}")

                    except Exception as e:
                        print(f"Fehler beim Verarbeiten der Datei {file_path}: {e}")


if __name__ == "__main__":
    msg_folder = "C:/Users/o.schmidt/Desktop/post"  # HIER ANPASSEN
    output_file = "emails.csv"

    if os.path.exists(msg_folder):
        extract_msg_to_csv(msg_folder, output_file)
        print(f"Fertig! Die E-Mail-Daten wurden in '{output_file}' gespeichert.")
    else:
        print(f"Fehler: Der angegebene Pfad '{msg_folder}' existiert nicht.")
