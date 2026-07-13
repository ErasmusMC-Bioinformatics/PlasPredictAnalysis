import os
import subprocess
import shutil
from Bio import SeqIO
import pandas as pd
from datetime import datetime
completed_accessions = set()
# Output directory for RGI results
FASTA_DIR = "plasmid_fasta/"
OUTPUT_DIR = "rgi/outputs/"

# Create the output, plasmid table, and extracted plasmid directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Loop through all FASTA files in the input list provided by Snakemake
with open(snakemake.input.sublist, "r") as fastas:
    for line in fastas.readlines()[1:]:
        file_name = line.strip()

        # Skip empty lines (if any)
        if not file_name:
            continue

        input_file = os.path.join(FASTA_DIR, file_name + ".fasta")
       # print(input_file)
        output = (file_name + ".output2")
        output_subdir = os.path.join(OUTPUT_DIR, file_name + ".output")
        #os.makedirs(output_subdir, exist_ok=True)

        # Print the file being processed
#        print(f"\nProcessing {file_name}...\n")

        # Run RGI
        command = [
            "rgi", "main",
            "-i", input_file,
            "-o", output_subdir,
            "-t", "contig",
            "-d", "plasmid"
        ]
#        with open("/mnt/DATAPOOL/mmibstudent2/Plasmid_project/rgi/error.log", "a") as err_log:
        subprocess.run(command)

print("RGI analysis complete")

with open(snakemake.output.outfile, "w") as confirmation:
    confirmation.write("RGI analysis completed!")

    # Load completed accession codes to avoid re-downloading
    #try:
   #     with open("completed_accessions.txt", "r") as completed_file:
  #          for line in completed_file:
 #               completed_accessions.add(line.strip())
#    except FileNotFoundError:
#with open("completed_accessions.txt", "a") as completed_file:
 #               completed_file.write(f"{accession_code}\n")
