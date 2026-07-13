import os

# Definieer het pad naar de map met de GenBank-bestanden
GENBANK_DIR = "plasmid_genbank/"

# Open de uitvoerbestanden in 'append' modus ('a') en schrijf de header
with open(snakemake.output.outfile, "w") as meta_file:
    meta_file.write("accession|host|locatie|size\n")

    # Lees inpu5
    with open(snakemake.input.infile, "r") as input_file:
        for line in input_file:
            filename = line.strip()
            filepath = os.path.join(GENBANK_DIR, filename)

            # Controleer of het bestand bestaat
            if not os.path.exists(filepath):
                print(f"Waarschuwing: Bestand niet gevonden: {filepath}")
                continue

            # Initialiseer variabelen
            accession = ""
            size = ""
            geo_loc = ""
            host = ""

            # Lees het bestand regel voor regel
            with open(filepath, "r") as gb_file:
                for gb_line in gb_file:
                    if "VERSION" in gb_line:
                        accession = gb_line.strip().split()[1]
                    elif "LOCUS" in gb_line:
                        size = gb_line.strip().split()[2]
                    elif "geo_loc_name" in gb_line:
                        # Haal de locatie op en verwijder onnodige tekens
                        geo_loc = gb_line.strip().split("=")[1].replace('"', '').split(":")[0]
                    elif "/host=" in gb_line:
                        # Haal de host op en verwijder onnodige tekens
                        host = gb_line.strip().split("=")[1].replace('"', '')

            # Schrijf de verzamelde data naar de bestanden
            if accession and host and geo_loc and size:
                meta_file.write(f"{accession}|{host}|{geo_loc}|{size}\n")
