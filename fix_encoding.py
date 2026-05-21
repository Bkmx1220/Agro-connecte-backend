# fix_encoding.py

# On teste plusieurs encodages possibles
encodings = ["utf-16", "latin-1", "cp1252"]

for enc in encodings:
    try:
        with open("data.json", "r", encoding=enc) as f:
            content = f.read()
        print(f"✔️ Fichier lu avec succès en {enc}")

        with open("data_utf8.json", "w", encoding="utf-8") as f:
            f.write(content)

        print("✅ Conversion en UTF-8 réussie")
        break

    except Exception as e:
        print(f"❌ Échec avec {enc}")