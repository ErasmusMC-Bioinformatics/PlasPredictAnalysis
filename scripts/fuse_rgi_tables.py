import os
import glob

rgi_dir = "rgi/outputs/"
list_rgi = snakemake.input.infile
output_file = snakemake.output.outfile

# Header
header = (
    "ORF_ID\tContig\tStart\tStop\tOrientation\tCut_Off\tPass_Bitscore\tBest_Hit_Bitscore\t"
    "Best_Hit_ARO\tBest_Identities\tARO\tModel_type\tSNPs_in_Best_Hit_ARO\tOther_SNPs\t"
    "Drug_ClassResistance_Mechanism\tAMR_Gene_Family\tPredicted_DNA\tPredicted_Protein\t"
    "CARD_Protein_Sequence\tPercentage_Length_of_Reference_Sequence\tID\tModel_ID\tNudged\t"
    "Note\tHit_Start\tHit_End\tAntibiotic\n"
)

with open(output_file, "w") as out_f:
    out_f.write(header)
  #  for file in list:
 #       file = file.strip().split()[0]
        
    # Vind alle *.output.txt bestanden in de map
    for filepath in sorted(glob.glob(os.path.join(rgi_dir, "*output.txt"))):
        with open(filepath, "r") as f:
            lines = f.readlines()
            if len(lines) > 1:
                out_f.writelines(lines[1:])  # Skip de header
