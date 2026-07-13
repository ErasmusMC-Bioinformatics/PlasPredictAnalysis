
import shutil
import os
import csv


# Use Snakemake paths
input_csv = snakemake.input.infile
mash_cluster_list = snakemake.output.mash_dirs
panaroo_cluster_list = snakemake.output.panaroo_dirs

# Open the input file
with open(input_csv, "r") as infile:
    inc_dict = {}  # Dictionary to store Inc types and accessions
    reader = csv.reader(infile)
    next(reader)  # Skip header

    for line in reader:
        inc = line[1].replace("(", "_").replace(")", "_").replace(" ", "_").replace("/", "_")
        accession = line[4].strip('"').split(" ")[0]

        if inc not in inc_dict:
            inc_dict[inc] = []
        inc_dict[inc].append(accession)

# Open output files for writing cluster directory paths
with open(mash_cluster_list, "w") as mashfile, open(panaroo_cluster_list, "w") as panaroofile:
    for inc_type, accessions in inc_dict.items():
        cluster_dir_mash = f"mash/{inc_type}_cluster/"
        cluster_dir_panaroo = f"panaroo/{inc_type}_cluster/"

        mashfile.write(f"{cluster_dir_mash}\n")
        panaroofile.write(f"{cluster_dir_panaroo}\n")

        os.makedirs(cluster_dir_mash, exist_ok=True)
        os.makedirs(cluster_dir_panaroo, exist_ok=True)

        for accession in accessions:
            source = f"plasmid_fasta/{accession}.fasta"
            destination_mash = os.path.join(cluster_dir_mash, f"{accession}.fasta")

            source2 = f"prokka/{accession}.output/{accession}.outfile.gff"
            destination_panaroo = os.path.join(cluster_dir_panaroo, f"{accession}.outfile.gff")

            try:
                shutil.copyfile(source, destination_mash)
                print(f"Successfully copied to mash: {accession}")
            except FileNotFoundError:
                print(f"File not found (mash): {source}, skipping...")
            except Exception as e:
                print(f"Error copying mash file {accession}: {e}")

            try:
                shutil.copyfile(source2, destination_panaroo)
                print(f"Successfully copied to panaroo: {accession}.outfile.gff")
            except Exception as e:
                print(f"Error copying panaroo file {accession}: {e}")
