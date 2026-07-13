with open(snakemake.input.amr_total) as amr, open(snakemake.output.outfile, "w") as table:
    table.write(f"accession|amr_gene|amr_gene_family|drug_class|resistance_mechanism\n")
    count = 1
    for info in amr.readlines()[1::]:
        info = info.strip().split("\t")
        gene_family, drug_class, resistance_mechanism = info[16], info[14], info[15]
        accession = info[1].rsplit("_", 1)[0]
        #print(info)
        amr_gene = info[8]
        table.write(f"{accession}|{amr_gene}|{gene_family}|{drug_class}|{resistance_mechanism}\n")
