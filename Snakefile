# FINAL PLASMID PIPELINE - SNAKEMAKE
# Author: Humère Javed
# Email: javedhumere@gmail.com
# Version 1

# De suffixes we use for parallelization
SUFFIXES = ['a', 'b', 'c', 'd']

rule all:
    input:
        "full_amr_table.txt",
        "fused_plasmidfinder.csv",
        "metadata.txt",
        "load_complete.flag",
        "panaroo_done.flag"

# 1. Preparation

rule split_accession_list:
    input: accessions="batch2_accessions.txt"
    output:
        p1="part_a.txt",
        p2="part_b.txt",
        p3="part_c.txt",
        p4="part_d.txt"
    script: "scripts/split_list.py"

# 2. DOWNLOADS (FASTA & GENBANK) 

rule collect_fasta:
    input: sublist="part_{suffix}.txt"
    output: outfile="collect_fasta_p{suffix}.txt"
    script: "scripts/plasmid_collection.py"

rule collect_genbank:
    input: sublist="part_{suffix}.txt"
    output: outfile="collect_genbank_p{suffix}.txt"
    script: "scripts/metadata_collection.py"

rule wait_for_downloads:
    input:
        fasta=expand("collect_fasta_p{suffix}.txt", suffix=SUFFIXES),
        genbank=expand("collect_genbank_p{suffix}.txt", suffix=SUFFIXES)
    output:
        touch("downloads_complete.flag")

#  3. ANALYSis LAYER 1 (PLASMIDFINDER & RGI) 

rule plasmidfinder:
    input:
        sublist="part_{suffix}.txt",
        ready="downloads_complete.flag"
    output: outfile="combined_results_p{suffix}.csv"
    script: "scripts/plasmidfinder_snakemake.py"

rule rgi:
    input:
        sublist="part_{suffix}.txt",
        ready="downloads_complete.flag"
    output: outfile="confirmation_rgi_p{suffix}.txt"
    script: "scripts/rgi_snakemake.py"

#  4. ANALYSIS LAYER 2 (PROKKA) 
# Start pas als de snelle analyses voor dat specifieke deel klaar zijn

rule prokka:
    input:
        sublist="part_{suffix}.txt",
        pf_ready="combined_results_p{suffix}.csv",
        rgi_ready="confirmation_rgi_p{suffix}.txt"
    output: outfile="confirmation_prokka_p{suffix}.txt"
    script: "scripts/prokka.py"

#  5. AGGREGATION (AMR & PLASMIDFINDER) 

rule merge_plasmidfinder:
    input: 
        csvs=expand("combined_results_p{suffix}.csv", suffix=SUFFIXES),
        prokka_done=expand("confirmation_prokka_p{suffix}.txt", suffix=SUFFIXES)
    output: outfile="fused_plasmidfinder.csv"
    script: "scripts/fuse_plasmidfinder_tables.py"

rule get_rgi_files:
    input:
        prokka_ready=expand("confirmation_prokka_p{suffix}.txt", suffix=SUFFIXES)
    output:
        outfile="rgi_list.txt"
    shell:
        "mkdir -p rgi/outputs && ls rgi/outputs/ | egrep 'output.txt' > {output.outfile} || touch {output.outfile}"

rule merge_rgi:
    input: infile="rgi_list.txt"
    output: outfile="amr_total.txt"
    script: "scripts/fuse_rgi_tables.py"

rule get_amr_table:
    input: amr_total="amr_total.txt"
    output: outfile="full_amr_table.txt"
    script: "scripts/get_amr.py"

#  6. METADATA & CLUSTERING

rule get_genbank_files:
    input: ready="downloads_complete.flag"
    output: outfile="metadata_list.txt"
    shell:
        "ls plasmid_genbank/ > {output.outfile}"

rule extract_metadata:
    input: sublist="metadata_list.txt"
    output: outfile="metadata.txt"
    shell:
        "bash scripts/extract_metadata.sh {input.sublist} {output.outfile}"

rule cluster_types:
    input: infile="fused_plasmidfinder.csv"
    output:
        mash_dirs="inc_mash_cluster_dirs.txt",
        panaroo_dirs="inc_panaroo_cluster_dirs.txt"
    script: "scripts/cluster_plasmid_types.py"

rule run_panaroo:
    input:
        dirlist="inc_panaroo_cluster_dirs.txt",
        prokka_done=expand("confirmation_prokka_p{suffix}.txt", suffix=SUFFIXES)
    output: flag="panaroo_done.flag"
    script: "scripts/panaroo_snakemake.py"

# 7. DATABASE SETUP & LOAD 

rule setup_db:
    output: flag="db_initialized.flag"
    params:
        db_dir=expand("~/my_db"),
        port="5434",
        db_name="plasmid_project_batch"
    shell:
        """
        mkdir -p logs
        if [ ! -d "{params.db_dir}" ]; then
            initdb -D {params.db_dir}
        fi
        if ! pg_isready -p {params.port} > /dev/null 2>&1; then
            pg_ctl -D {params.db_dir} -l logs/postgres.log -o "-p {params.port}" start
            sleep 5
        fi
        createdb -p {params.port} {params.db_name} 2>/dev/null || echo "DB bestaat al"
        touch {output.flag}
        """

rule load_database:
    input:
        amr="full_amr_table.txt",
        pf="fused_plasmidfinder.csv",
        md="metadata.txt",
        db_ready="db_initialized.flag"
    output: outfile="load_complete.flag"
    script: "scripts/db_load.py"
