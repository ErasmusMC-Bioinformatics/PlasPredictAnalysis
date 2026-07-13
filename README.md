# Big_Data_Analysis_of_Bacterial_Plasmids

## Overview

This pipeline analyzes bacterial plasmids obtained from the public NCBI repository. The goal is to characterize plasmids, annotate them, identify antimicrobial resistance (AMR) genes, and perform a pangenome analysis. All results are stored in a PostgreSQL database.

The pipeline is implemented using Snakemake (version 7.32.4.25) to ensure reproducible and scalable analysis. Each step is executed through Python scripts that call external tools such as PlasmidFinder, RGI, Prokka, and Panaroo.

---

## Requirements

- Python 3.8.6
- Snakemake 7.32.4.25
- Biopython
- PostgreSQL 12.9
- Installed tools with the following versions:
  - PlasmidFinder 2.1.6
  - RGI 6.0.3
  - Prokka 1.14.6
  - Panaroo 1.5.1
  - Mash 2.3

---

## Data
The file sequence.seq contains the accessions of all the bacterial plasmids that were used for this project and can be downloaded from this repository.
For the most up to date version, the file can be downloaded from NCBI using the parameters as shown in figure 1.

<img width="1600" height="865" alt="image" src="https://github.com/user-attachments/assets/b1579947-2c1a-41cb-879f-17bdc70d959a" />

Figure 1. Parameters used for the retrieval of all bacterial plasmids used in this project.

---
## Pipeline Overview

<img width="1751" height="923" alt="pipeline_dag" src="https://github.com/user-attachments/assets/76dc7e1b-ff68-4930-9ed7-61030082db90" />

Figure 2. Overview of the steps performed in the Snakemake pipeline.
--

## Pipeline Steps

1. **Plasmid and Metadata Collection**
   Using `plasmid_collection.py` and `metadata_collection.py`, plasmid FASTA sequences and metadata are downloaded from NCBI in batches, based on accession numbers.

2. **Plasmid Typing**
   `plasmidfinder_snakemake.py` runs PlasmidFinder via subprocess to determine Inc types for plasmids.

3. **AMR Gene Identification**
   `rgi_snakemake.py` runs RGI to identify antimicrobial resistance genes in plasmids.

4. **Genome Annotation**
   Prokka is run through `prokka.py` to annotate plasmid sequences with bacterial gene predictions.

5. **Clustering Based on Inc Types**
   Using `cluster_plasmid_types.py`, plasmids are grouped by Inc type for downstream analysis.

6. **Pangenome Analysis**
   Panaroo is run with `panaroo_snakemake.py` on clustered plasmids to identify gene presence and diversity.

7. **Database Loading**
   The final processed data (AMR, typing, metadata) are loaded into a PostgreSQL database using `db_load.py`.

Extra step that still needs to be included in the pipeline: **Genomic Distance Estimation**
Mash sketches are created and distances calculated to infer plasmid similarity, followed by conversion to Newick format for visualization.
For just estimating distances, Mash can be used. However if there is a need to generate a tree based on the distances. Mashtree is recommended.

---

## 📃 Script Overview

#### **1. Data Collection and Processing**

These scripts are responsible for downloading raw data and running bioinformatics tools.

* **`plasmid_collection.py`**: This script downloads plasmid sequences in FASTA format from a sublist of accessions.
* **`metadata_collection.py`**: This script collects GenBank files, which contain essential metadata for the accessions.
* **`plasmidfinder_snakemake.py`**: This script runs the PlasmidFinder tool to identify plasmid replicon sequences in the collected data.
* **`rgi_snakemake.py`**: This script executes the RGI (Resistance Gene Identifier) tool, which predicts antibiotic resistance genes.
* **`prokka.py`**: This script runs Prokka, a rapid bacterial annotation tool that identifies coding sequences.

---

#### **2. Data Fusion and Formatting**

These scripts combine the outputs from the earlier steps and prepare the data for the database.

* **`fuse_plasmidfinder_tables.py`**: This script merges the results from individual PlasmidFinder runs into a single CSV file.
* **`fuse_rgi_tables.py`**: This script combines all the individual RGI output files into a single, comprehensive table.
* **`get_amr.py`**: This script processes the combined RGI table to extract the final AMR (antimicrobial resistance) table for database loading.
* **`extract_metadata.py`**: This script extracts relevant metadata, such as host and organism, from the collected GenBank files.
* **`clean_metadata` (Bash/Shell command)**: This command filters lines from the metadata file that do not have the correct number of fields, ensuring the data is clean before being loaded into the database.

---

#### **3. Advanced Analysis**

These scripts perform more complex analyses after the initial data processing.

* **`cluster_plasmid_types.py`**: This script uses the merged PlasmidFinder results to identify plasmid types and create directories for downstream clustering analysis.
* **`panaroo_snakemake.py`**: This script runs the Panaroo tool on the clustered data to perform a pan-genome analysis.

---

#### **4. Database Loading**

* **`db_load.py`**: This is the core script for the database operations. Its main function is to:
    * Connect to a PostgreSQL database.
    * Drop existing tables to prevent conflicts.
    * Create new tables for metadata, AMR, and PlasmidFinder data.
    * Read the cleaned data and insert it into the appropriate tables.
    * Verify that accession numbers exist in the `Metadata` table before inserting data into other tables.
 ---

## Usage

1. Clone this repository.
2. Ensure all dependencies and required tools are installed.
3. Place the accession list file at the specified location (e.g., `sequence.seq` or `batch2_accessions.txt`) and make sure the paths are changed into the proper paths in each of the individual scripts (up to the user's liking). Specify the right accession file in the Snakefile
4. Put the Snakefile and the scripts that the pipeline consists of in the same directory together with the accession file.
5. Run the pipeline with:

```bash
snakemake --snakefile Snakefile all -c4
snakemake --snakefile Snakefile all -c4 --rerun-incomplete --keep-going
snakemake --snakefile Snakefile part_a.txt part_b.txt part_c.txt part_d.txt -c4
snakemake --snakefile Snakefile collect_fasta_pa.txt collect_fasta_pb.txt collect_fasta_pc.txt collect_fasta_pd.txt -c4
snakemake --snakefile Snakefile collect_genbank_pa.txt collect_genbank_pb.txt collect_genbank_pc.txt collect_genbank_pd.txt -c4
snakemake --snakefile Snakefile downloads_complete.flag -c1
snakemake --snakefile Snakefile combined_results_pa.csv combined_results_pb.csv combined_results_pc.csv combined_results_pd.csv -c4
snakemake --snakefile Snakefile confirmation_rgi_pa.txt confirmation_rgi_pb.txt confirmation_rgi_pc.txt confirmation_rgi_pd.txt -c4
snakemake --snakefile Snakefile fused_plasmidfinder.csv -c1
snakemake --snakefile Snakefile rgi_list.txt -c1
snakemake --snakefile Snakefile amr_total.txt -c1
snakemake --snakefile Snakefile metadata_list.txt -c1
snakemake --snakefile Snakefile metadata.txt -c1
snakemake --snakefile Snakefile inc_mash_cluster_dirs.txt inc_panaroo_cluster_dirs.txt -c1
snakemake --snakefile Snakefile panaroo_done.flag -c1
snakemake --snakefile Snakefile db_initialized.flag -c1
snakemake --snakefile Snakefile load_complete.flag -c1
```
6. The final database load status will be indicated by the presence of the file:
`confirmation_db.txt`
---

### Overview of Snakemake Rules

The rules below are grouped by function, which will help you understand the different steps in your pipeline.

#### **1. Main Rule and Splitting**
* **`rule all`**: This is the main rule and the entry point of the workflow. It defines the final files that Snakemake needs to create. Only when these files have been successfully created is the workflow considered complete.
* **`rule split_accession_list`**: This rule splits a long list of accession numbers into four smaller lists. This is a crucial step for distributing the workload and enabling parallel processing.

---

#### **2. Data Collection**
* **`rule collect_part1` to `collect_part4`**: These four rules download the plasmid sequences in FASTA format for each of the split lists. This parallel approach significantly speeds up the process.
* **`rule collect_genbank_part1` to `collect_genbank_part4`**: These four rules are responsible for downloading the GenBank files that contain essential metadata.

---

#### **3. Bioinformatics Tools**
* **`rule plasmidfinder_part1` to `plasmidfinder_part4`**: These rules run the PlasmidFinder tool on the downloaded FASTA files to identify plasmid replicon sequences.
* **`rule rgi_part1` to `rgi_part4`**: These rules execute the RGI (Resistance Gene Identifier) tool, which predicts which genes code for antibiotic resistance.
* **`rule prokka_part1` to `prokka_part4`**: These rules run the Prokka tool for rapid bacterial annotation, which helps in identifying coding sequences in the downloaded data.

---

#### **4. Merging and Cleaning**
* **`rule merge_plasmidfinder_results`**: Merges the separate CSV outputs from the individual PlasmidFinder runs into a single, comprehensive file.
* **`rule get_rgi_files`**: Finds all RGI output files and creates a list of them.
* **`rule merge_rgi_outputs`**: Combines all the individual RGI output files into one large, overarching table.
* **`rule get_amr_table`**: Processes the merged RGI table to extract the final AMR (antimicrobial resistance) table for the database.
* **`rule get_genbank_files`**: Finds all downloaded GenBank files and creates a list of them.
* **`rule extract_metadata`**: Retrieves relevant metadata (such as host and organism) from the GenBank files.
* **`rule clean_metadata`**: This is an important step that cleans the extracted metadata. It removes incomplete or incorrectly formatted lines, ensuring the data is consistent.

---

#### **5. Advanced Analysis and Database Loading**
* **`rule cluster_types`**: Identifies plasmid types from the merged PlasmidFinder results and prepares the directory structure for further analysis.
* **`rule run_panaroo_clusters`**: Runs the Panaroo program to perform a pan-genome analysis of the data.
* **`rule load_database`**: This is the final rule in the pipeline. It loads all the processed and cleaned data (AMR, PlasmidFinder, and metadata) into the PostgreSQL database. It represents the ultimate goal of the entire workflow.
## Inputs and Outputs

Splitting the list of accessions into four:
- Input: sequence.seq or batch2_accessions.txt
- Output: xaa, xab, xac, xad

Collect the FASTA sequences part 1:
- Input: xaa
- Output: collect_fasta_p1.txt

Collect the FASTA sequences part 2:
- Input: xab
- Output: collect_fasta_p2.txt

Collect the FASTA sequences part 3 :
- Input: xac
- Output: collect_fasta_p3.txt

Collect the FASTA sequences part 4:
- Input: xad
- Output: collect_fasta_p4.txt

Collect genbank part 1:
- input: xaa
- output: collect_genbank_p2.txt

Collect genbank part 2:
- input: xab
- output: collect_genbank_p2.txt

Collect genbank part 3:
- input: xac
- output: collect_genbank_p3.txt

Collect genbank part 4:
- input: xad
- output: collect_genbank_p4.txt

Plasmidfinder part 1:
- input: xaa
- output: combined_results_part1.csv

Plasmidfinder part 2:
- input: xab
- output: combined_results_part2.csv

Plasmidfinder part 3:
- input: xac
- output: combined_results_part3.csv

Plasmidfinder part 4:
- input: xad
- output: combined_results_part4.csv

RGI part 1:
- input: xaa
- output: confirmation_rgi_p1.txt

RGI part 2:
- input: xab
- output: confirmation_rgi_p2.txt

RGI part 3:
- input: xac
- output: confirmation_rgi_p3.txt

RGI part 4:
- input: xad
- output: confirmation_rgi_p4.txt

Prokka part 1:
- input: xaa
- output: confirmation_prokka_p1.txt

Prokka part 2:
- input: xab
- output: confirmation_prokka_p2.txt

Prokka part 3:
- input: xac
- output: confirmation_prokka_p3.txt

Prokka part 4:
- input: xad
- output: confirmation_prokka_p4.txt

Merge plasmidfinder results:
- input: combined_results_part1.csv, combined_results_part3.csv, combined_results_part3.csv, combined_results_part4.csv
- output: fused_plasmidfinder.csv

Cluster Plasmid types:
- input: fused_plasmidfinder.csv
- output: inc_mash_clusters_dirs.txt, inc_panaroo_clusters_dirs.txt

Panaroo:
- input: inc_panaroo_cluster_dirs.txt
- output: panaroo_done.flag

Merge rgi outputs:
- input: Plasmid_project/rgi_outputs/*
- output: amr_total.txt

Get AMR table:
- input: amr_total.txt
- output: full_amr_table.txt

Extract metadata:
- input: Plasmid_project/plasmid_collection/plasmid_genbank/*
- output: metadata.txt

Clean metadata:
- input: metadata.txt
- output: metadata_clean.txt

Load database:
- input: fused_plasmidfinder.csv, full_amr_table.txt, metadata_clean.csv
- output: confirmation_db.txt


---

## Explanation of Input and Output files generated using the pipeline.
- sequence.seq: List of all the plasmid accessions that were used in this project
- confirmation_db.txt: indicates that the database has been loaded fully.
- fused_plasmidfinder.csv: Table containing all typed plasmids.
- panaroo_done.flag: indicates that the panaroo step has been completed
- metadata_clean.txt: The metadata after making sure it is in the right format.
- full_amr_table.txt: Table containing all AMR info.
- combined_results_part1.csv: First part of the typed plasmids.
- combined_results_part2.csv: Second part of the typed plasmids.
- combined_results_part3.csv: Third part of the typed plasmids.
- combined_results_part4.csv: Fourth part of the typed plasmids.
- confirmation_p1_rgi.txt: Indicates the first part of the RGI analysis is finished.
- confirmation_rgi_p2.txt: Indicates the second part of the RGI analysis is finished.
- confirmation_rgi_p3.txt: Indicates the third part of the RGI analysis is finished.
- confirmation_rgi_p4.txt: Indicates the fourth part of the RGI analysis is finished.
- confirmation_prokka_p1.txt: Indicates the first part of the Prokka analysis is finished.
- confirmation_prokka_p2.txt: Indicates the second part of the Prokka analysis is finished.
- confirmation_prokka_p3.txt: Indicates the third part of the Prokka analysis is finished.
- confirmation_prokka_p4.txt: Indicates the fourth part of the Prokka analysis is finished.
- xaa: First part of sequence.seq
- xab: Second part of sequence.seq
- xac: Third part of sequence.seq
- xad: Fourth part of sequence.seq
- collect_fasta_p1.txt: List keeping track of all the downloaded FASTA to prevent redownloading first part.
- collect_fasta_p2.txt: List keeping track of all the downloaded FASTA to prevent redownloading the second part.
- collect_fasta_p3.txt: List keeping track of all the downloaded FASTA to prevent redownloading the third part.
- collect_fasta_p4.txt: List keeping track of all the downloaded FASTA to prevent redownloading the fourth part.
- collect_genbank_p1.txt: List keeping track of all the downloaded genbank files to prevent redownloading of the first part.
- collect_genbank_p2.txt: List keeping track of all the downloaded genbank files to prevent redownloading of the second part.
- collect_genbank_p3.txt: List keeping track of all the downloaded genbank files to prevent redownloading of the third part.
- collect_genbank_p4.txt: List keeping track of all the downloaded genbank files to prevent redownloading of the fourth part.
- inc_mash_cluster_dirs.txt: File containing the paths of all the plasmid types for the mash data.
- inc_panaroo_cluster_dirs.txt: File containing the paths of all the plasmid types for the panaroo data.
- amr_total.txt: The extracted data from the RGI data.
- metadata.txt: The extracted metadata from all the genbank files.

---

## Future/Potential updates

1. The split_accessions rule does not properly split the accession list into four segments. A Python script that splits properly can be created in the future.
2. The extract_metadata rule, especially extract_metadata.py needs some reviewing with regards to extracting the useful information the right way because somewhere along the line it goes wrong with creating the table. If this problem can be fixed, the clean_metadata rule can be discarded.
3. The Mash distances step needs to be added.

---

## Contact

For questions or issues, please contact the author.

---
