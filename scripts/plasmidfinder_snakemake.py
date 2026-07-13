import os
import subprocess
import shutil
from Bio import SeqIO
import pandas as pd
from datetime import datetime

# Path settings
FASTA_DIR = "plasmid_fasta/"
OUTPUT_DIR = "plasmidfinder/"
PLASMIDFINDER_SCRIPT = "/plasmidfinder.py"
PLASMIDFINDER_DB = "/plasmidfinder_db"
PLASMID_TABLE_DIR = "plasmidfinder/plasmid_results_all/"
EXTRACTED_PLASMIDS_DIR = "plasmidfinder/extracted_plasmids_all/"
ERROR_LOG_FILE = "plasmidfinder_errors.log"

# Zorg dat output directories bestaan
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PLASMID_TABLE_DIR, exist_ok=True)
os.makedirs(EXTRACTED_PLASMIDS_DIR, exist_ok=True)

# Lege lijst voor resultaten
results_files = []

# Open logbestand
with open(ERROR_LOG_FILE, "a") as error_log:

    # Verwerk accession lijst
    with open(snakemake.input.sublist, "r") as fastas:
        for line in fastas:
            acc = line.strip()
            if not acc:
                continue  # sla lege lijnen over

            file_name = acc + ".fasta"
            input_file = os.path.join(FASTA_DIR, file_name)
            output_subdir = os.path.join(OUTPUT_DIR, file_name + "_plasmidfinder_output")
            os.makedirs(output_subdir, exist_ok=True)
            try:
                # Check of bestand bestaat en niet leeg is
                if not os.path.isfile(input_file) or os.path.getsize(input_file) == 0:
                    msg = f"⚠️  Bestand ontbreekt of is leeg: {input_file}. Overgeslagen."
                    print(msg)
                    error_log.write(msg + "\n")
                    continue

                # Run plasmidfinder
                result = subprocess.run([
                    "python", PLASMIDFINDER_SCRIPT,
                    "-i", input_file,
		    "-p", PLASMIDFINDER_DB,
                    "-o", output_subdir,
                    "-x"
                ], check=True, capture_output=True, text=True)

            except subprocess.CalledProcessError as e:
                msg = f"❌ Fout bij {file_name}: {e.stderr}"
                print(msg)
                error_log.write(f"{file_name} - subprocess error:\n{e.stderr}\n\n")
                continue

            except Exception as e:
                msg = f"❌ Onverwachte fout bij {file_name}: {str(e)}"
                print(msg)
                error_log.write(f"{file_name} - unexpected error:\n{str(e)}\n\n")
                continue

            # Verwerk output
            results_file = os.path.join(output_subdir, "results_tab.tsv")
            if os.path.exists(results_file):
                dest_file = os.path.join(PLASMID_TABLE_DIR, f"{file_name}_results_tab.tsv")
                shutil.copy(results_file, dest_file)
                results_files.append(dest_file)
            else:
                msg = f"⚠️  Geen resultatenbestand voor {file_name}"
                print(msg)
                error_log.write(msg + "\n")

# Combineer resultaten
if results_files:
    combined_df = pd.concat([
        pd.read_csv(f, sep='\t').assign(Source_File=os.path.basename(f))
        for f in results_files
    ])
    combined_file_name = snakemake.output.outfile
    combined_file_path = combined_file_name
    combined_df.to_csv(combined_file_path, index=False)
    print(f"\n✅ Gecombineerd resultatenbestand aangemaakt: {combined_file_name}")
else:
    print("\n⚠️  Geen geldige resultaten om te combineren.")

print("\n🏁 PlasmidFinder analyse voltooid.")
