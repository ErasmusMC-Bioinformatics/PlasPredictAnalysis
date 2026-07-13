import os
import subprocess

fasta_lijst = snakemake.input.sublist
fasta_pad = "plasmid_fasta/"
bevestiging_file = snakemake.output.outfile  # for example confirmation_prokka_pa.txt
error_log_file = "prokka_errors.log"

with open(error_log_file, "a") as errlog:
    with open(fasta_lijst, "r") as file:
        for regel in file:
            regel = regel.strip()
            if not regel:
                continue

            fasta_file = os.path.join(fasta_pad, f"{regel}.fasta")
            outdir = f"prokka/{regel}.output"
            prefix = f"{regel}.outfile"

            # Check for valid FASTA starting with '>'
            try:
                with open(fasta_file, "r") as f_check:
                    first_line = f_check.readline()
                    if not first_line.startswith(">"):
                        msg = f"⚠️ Onvalid FASTA-(geen '>') vor {regel}: {fasta_file}"
                        print(msg)
                        errlog.write(msg + "\n")
                        continue
            except FileNotFoundError:
                msg = f"❌ File not found: {fasta_file}"
                print(msg)
                errlog.write(msg + "\n")
                continue

            # Run prokka
            try:
                subprocess.run([
                    "prokka",
                    "--outdir", outdir,
                    "--prefix", prefix,
                    fasta_file,
                    "--kingdom", "Bacteria",
                    "--force"
                ], check=True)
            except subprocess.CalledProcessError as e:
                msg = f"❌ Prokka failed for {regel}: {e}"
                print(msg)
                errlog.write(msg + "\n")
                continue

# Make a confirmation file for Snakemake
with open(bevestiging_file, "w") as f:
    f.write("Prokka part completed.\n")

print("✅ Done with all Prokka annotations.")
