import pandas as pd
import os

# Snakemake geeft alle bestanden van de 'expand' door als een lijst in snakemake.input
bestandsnamen = snakemake.input

dfs = []

for bestand in bestandsnamen:
    # Check of het bestand bestaat en niet leeg is
    if os.path.exists(bestand) and os.path.getsize(bestand) > 0:
        df = pd.read_csv(bestand)
        # Alleen toevoegen als er echt data in zit (behalve de header)
        if not df.empty:
            dfs.append(df)

if dfs:
    samengevoegde_df = pd.concat(dfs, ignore_index=True)
else:
    # Maak een lege dataframe als er helemaal geen hits waren in alle 4 de delen
    samengevoegde_df = pd.DataFrame()

# Sla op naar de locatie die Snakemake aangeeft
samengevoegde_df.to_csv(snakemake.output.outfile, index=False)

print(f"Succesvol samengevoegd naar {snakemake.output.outfile}")
