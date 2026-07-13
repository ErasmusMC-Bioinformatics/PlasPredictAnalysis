import math

def split_file_by_lines(input_path, output_paths):
    # 1. Lees alle regels in het geheugen
    with open(input_path, 'r') as f:
        lines = f.readlines()

    total_lines = len(lines)
    # 2. Bereken hoeveel regels er per bestand moeten (naar boven afgerond)
    chunk_size = math.ceil(total_lines / len(output_paths))

    # 3. Schrijf de regels naar de verschillende output bestanden
    for i, out_path in enumerate(output_paths):
        start = i * chunk_size
        end = start + chunk_size
        chunk = lines[start:end]
        
        with open(out_path, 'w') as f_out:
            f_out.writelines(chunk)
            
        print(f"Deel {i+1} opgeslagen: {out_path} ({len(chunk)} regels)")

# Snakemake aanroep
# We maken handmatig een lijst van de losse outputs p1 t/m p4
output_list = [
    snakemake.output.p1, 
    snakemake.output.p2, 
    snakemake.output.p3, 
    snakemake.output.p4
]

split_file_by_lines(snakemake.input.accessions, output_list)
