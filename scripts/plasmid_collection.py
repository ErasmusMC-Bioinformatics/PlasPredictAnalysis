import os
import time
from Bio import Entrez

def read_and_fetch_accession(batch_size=5000, total_downloads=735920):
    """
    This function reads the file where all the important accession codes are listed.
    By calling the fetch_data() function, data can be fetched from the NCBI Nucleotide database.
    The function handles downloading in batches to avoid server overload.
    """
    email = "s1113311@student.hsleiden.nl"
    completed_accessions = set()
    output_directory = "plasmid_fasta/"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    # Load completed accession codes to avoid re-downloading
    try:
        with open("completed_accessions_fasta.txt", "r") as completed_file:
            for line in completed_file:
                completed_accessions.add(line.strip())
    except FileNotFoundError:
        pass  # File doesn't exist yet, no completed accessions

    # Read the file of accession codes
    with open(snakemake.input.sublist, "r") as accession_file:
        count = 0
        # Loop through the file
        for accession_code in accession_file:
            accession_code = accession_code.strip().split()[0]
           
            # Skip if already completed
            if accession_code in completed_accessions:
                continue

            # Make the file names
#            filename_gb = os.path.join(output_directory, accession_code + ".txt")
            filename_fa = os.path.join(output_directory, accession_code + ".fasta")
           
            # Fetch Fasta data
            fetch_data(accession_code, filename_fa, email, "fasta")
           
            # Mark accession as completed
            with open("completed_accessions_fasta.txt", "a") as completed_file:
                completed_file.write(f"{accession_code}\n")
           
            count += 1
            # Break the loop once we reach the batch size
            if count % batch_size == 0:
                print(f"Reached {count} downloads in this batch, pausing to avoid server issues.")
                # Pause before the next batch
                time.sleep(60)  # Wait 60 seconds before continuing to avoid overloading the server
           
            # Stop when the total number of downloads is reached
            if count == total_downloads:
                print(f"Reached total of {total_downloads} downloads. Stopping.")
                break

            # Add a delay between requests to avoid overloading the server
            time.sleep(1)

def fetch_data(accession_code, filename, email, rettype):
    """
    Fetches either a Genbank or Fasta file based on the parameters given.

    :param accession_code: The accession code of the sequence to retrieve.
    :param filename: The name of the file where the data of interest will be written to.
    :param email: NCBI prefers an email address when connecting to and collecting from the database.
    :param rettype: The type of file that will be fetched. This is either Fasta or Genbank.
    """
    try:
        # Fetch the file using the accession code
        with Entrez.efetch(db="nucleotide", id=accession_code, rettype=rettype, retmode="text", email=email) as handle:
            # Parse the file and save it
            with open(filename, "w") as out_handle:
                out_handle.write(handle.read())
#    print(f"File saved for this part")
    except Exception as e:
        print(f"An error occurred: {e}")
#    print("Saved the files!")
# Main function to run the script properly
if __name__ == "__main__":
    read_and_fetch_accession(batch_size=5000, total_downloads=739520)
    with open(snakemake.output.outfile, "w") as confirmation:
        confirmation.write("A part of the Fasta files have been downloaded")
    print("FASTA files saved!")

