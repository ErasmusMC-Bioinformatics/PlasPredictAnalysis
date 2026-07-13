import subprocess
import glob
import os


txt_file = snakemake.input.dirlist
flag_file = snakemake.output.flag
completed_accessions_file = os.path.join(os.path.dirname(flag_file), "completed_accessions_panaroo.txt")
completed_accessions = set()

# Load completed accessions to avoid re-processing
try:
    with open(completed_accessions_file, "r") as completed_file:
        for line in completed_file:
            completed_accessions.add(line.strip())
except FileNotFoundError:
    pass

with open(txt_file, "r") as file:
    directories = [line.strip() for line in file.readlines() if line.strip()]

for directory_path in directories:
    directory = os.path.basename(directory_path.rstrip("/"))
    if directory in completed_accessions:
        print(f"✅ Skipping already processed: {directory}")
        continue

    try:
        print(f"🔄 Processing directory: {directory}")

        gff_files = glob.glob(os.path.join(directory_path, "*.gff"))
        if not gff_files:
            print(f"⚠️  No .gff files found in {directory_path}, skipping...")
            continue

        output_dir = f"panaroo_results/results_{directory}"
        os.makedirs(output_dir, exist_ok=True)

        command = ["panaroo", "-i"] + gff_files + [
            "-o", output_dir,
            "--clean-mode", "moderate",
            "--remove-invalid-genes",
            "-c", "0.85",
            "--refind-mode", "off",
            "--aligner", "clustal"
        ]

        subprocess.run(command, check=True)
        print(f"✅ Successfully processed: {directory}")

        with open(completed_accessions_file, "a") as completed_file:
            completed_file.write(f"{directory}\n")

    except subprocess.CalledProcessError:
        print(f"❌ Panaroo command failed for: {directory}")
    except Exception as e:
        print(f"❌ Unexpected error for {directory}: {e}")

# Create Snakemake output flag
with open(flag_file, "w") as f:
    f.write("Panaroo run completed.\n")
