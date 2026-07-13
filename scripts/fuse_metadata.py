import os

genbank_list = snakemake.input.list
output_file = snakemake.output.outfile

def extract_value(line, start_idx=1):
    return "_".join(line.split()[start_idx:]).replace(":", "_").replace("(", "_").replace(")", "_").replace(",", "_")

with open(genbank_list, "r") as f:
    filenames = [line.strip() for line in f if line.strip()]

with open(output_file, "w") as out_f:
    out_f.write("accession|host|organism|locatie|size\n")
    for filename in filenames:
        filepath = os.path.join("plasmid_genbank/" + filename)
        if not os.path.isfile(filepath):
            print(f"⚠️ Skipping missing file: {filepath}")
            continue

        with open(filepath, "r") as genbank_file:
            lines = genbank_file.readlines()

        accession = host = organism = locatie = size = "NA"

        for line in lines:
            if line.startswith("VERSION") and accession == "NA":
                accession = line.strip().split()[1]
            elif "ORGANISM" in line and organism == "NA":
                organism = extract_value(line, 1)
            elif "LOCUS" in line and size == "NA":
                size = line.strip().split()[2]
            elif "geo_loc_name" in line and locatie == "NA":
                locatie = extract_value(line)
            elif "/host=" in line and host == "NA":
                host = extract_value(line)

        out_f.write(f"{accession}|{host}|{organism}|{locatie}|{size}\n")
