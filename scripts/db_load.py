import os
import pandas as pd
import psycopg2
import re

def connect_to_db():
    # Establish connection to the PostgreSQL database
    conn = psycopg2.connect(
        dbname='plasmid_project_batch',
	host='localhost',   # Belangrijk: forceer verbinding via localhost
        port='5434'
    )
    print("Successfully connected with the database!")
    return conn

def drop_tables(cur):
    # Drop existing tables to avoid conflicts when recreating
    cur.execute("DROP TABLE IF EXISTS PLASMIDFINDER;")
    cur.execute("DROP TABLE IF EXISTS AMR;")
    # Uncomment if you want to drop Metadata or other tables as well
    cur.execute("DROP TABLE IF EXISTS Metadata;")
     #The following commented code could drop gene presence absence tables dynamically
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'gene_presence_absence_%';")
    tables = cur.fetchall()
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table[0]};")
    print("Tables dropped if they existed.")

def create_metadata_table(cur):
    # Create Metadata table if it doesn't already exist
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Metadata (
        accession VARCHAR PRIMARY KEY,
        organism VARCHAR,
        location VARCHAR,
        host VARCHAR,
	isolation_source VARCHAR,
	size VARCHAR
    );
    """)
    print("✅ Table 'Metadata' created with VARCHAR columns.")

def insert_metadata(cur, metadata_df):
    count = 1
    for index, row in metadata_df.iterrows():
        try:
            # Oorspronkelijke code voor het invoegen van de rij
            cur.execute("SELECT COUNT(*) FROM Metadata WHERE accession = %s", (row['accession'],))
            if cur.fetchone()[0] == 0:
                insert_query = "INSERT INTO Metadata (accession, organism, location, host, isolation_source, size) VALUES (%s, %s, %s, %s, %s, %s)"
                cur.execute(insert_query, row.tolist())
                count += 1
            else:
                print(f"Duplicate found for accession: {row['accession']}, skipping row.")
        except IndexError as e:
            print(f"Fout bij het verwerken van rij {index}: {e}. Rijinhoud: {row.to_dict()}")
            continue  # Ga door naar de volgende rij

def create_gpa_table(cur):
    # Create table for gene presence/absence test with foreign key to Metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Gene_presence_absence_test (
        accession VARCHAR,
        gene VARCHAR,
        presence VARCHAR,
        CONSTRAINT FK_accession FOREIGN KEY (accession) REFERENCES Metadata (accession)
    );
    """)
    print("Gene presence/absence test table created.")

def insert_gpa(cur, conn):
    # Insert gene presence/absence data from CSV, only if accession exists in Metadata
    with open('merged_gene_presence_long.csv', 'r') as file:
        for line in file.readlines()[1:]:
            line = line.strip().split(",")
            print(line)
            cur.execute("SELECT COUNT(*) FROM METADATA WHERE accession = %s", (line[0],))
            if cur.fetchone()[0] > 0:
                insert_query = "INSERT INTO Gene_presence_absence_test (accession, gene, presence) VALUES (%s, %s, %s)"
                cur.execute(insert_query, (line[0], line[1], line[2]))
    conn.commit()
    print("All data added to Gene_presence_absence_test table.")

def create_amr_table(cur):
    # Create AMR table with foreign key relation to Metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS AMR (
        accession VARCHAR,
        amr_gene VARCHAR,
        amr_gene_family VARCHAR,
        drug_class VARCHAR,
        resistance_mechanism VARCHAR,
        CONSTRAINT FK_accession FOREIGN KEY (accession) REFERENCES Metadata (accession)
    );
    """)
    print("AMR table created.")

def insert_amr_data(cur, amr_df):
    # Insert AMR data only if accession exists in Metadata
    for index, row in amr_df.iterrows():
        cur.execute("SELECT COUNT(*) FROM Metadata WHERE accession = %s", (row['accession'],))
        if cur.fetchone()[0] > 0:
            insert_query = "INSERT INTO AMR (accession, amr_gene, amr_gene_family, drug_class,  resistance_mechanism) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(insert_query, row.tolist())
        else:
            print(f"Accession {row['accession']} not found in Metadata, skipping row.")
    print("AMR data inserted into table.")

def create_plasmidfinder_table(cur):
    # Create PlasmidFinder table with foreign key to Metadata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS plasmidfinder (
        accession VARCHAR,
        inc_type VARCHAR,
        position VARCHAR,
        CONSTRAINT FK_accession FOREIGN KEY (accession) REFERENCES Metadata (accession)
    );
    """)
    print("PlasmidFinder table created.")

def insert_plasmidfinder_data(cur):
    # Insert plasmidfinder data from CSV, handle different line lengths
    with open(snakemake.input.pf, 'r') as infile:
        count = 1
        for line in infile.readlines()[1:]:
            line = line.strip().split(",")
            if len(line) == 10:
                inc, pos, accession = line[1], line[6], line[9].strip(".fasta_results_tab.tsv")
            elif len(line) < 10:
                inc, pos, accession = line[1], line[4], line[8].strip(".fasta_results_tab.tsv")
            elif len(line) == 11:
                inc, pos, accession = line[1], line[7], line[10].strip(".fasta_results_tab.tsv")
            elif len(line) == 12:
                inc, pos, accession = line[1], line[8], line[11].strip(".fasta_results_tab.tsv")
            cur.execute("SELECT COUNT(*) FROM Metadata WHERE accession = %s", (accession,))
            if cur.fetchone()[0] > 0:
                insert_query = "INSERT INTO Plasmidfinder (accession, inc_type, position) VALUES (%s, %s, %s)"
                cur.execute(insert_query, (accession, inc, pos))
                count += 1
            else:
                print(f"Accession {accession} not found in Metadata, skipping row.")
        print(f"{count - 1} records inserted into PlasmidFinder table.")

def sanitize_column_name(name):
    # Replace non-alphanumeric characters with underscores for SQL safety
    return re.sub(r'\W+', '_', name)

def create_gene_presence_absence_table(cur, table_name, df):
    # Dynamically create a table for gene presence/absence with sanitized column names
    column_names = df.columns.tolist()
    sanitized_columns = [sanitize_column_name(col) for col in column_names]
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({sanitize_column_name(column_names[0])} VARCHAR PRIMARY KEY, "
    for col in sanitized_columns[1:]:
        create_table_query += f"{col} VARCHAR, "
    create_table_query = create_table_query.rstrip(', ') + ");"
    cur.execute(create_table_query)
    print(f"Table '{table_name}' created.")
    return sanitized_columns

def insert_gene_presence_absence(cur, table_name, df, sanitized_columns):
    # Insert data into dynamically created gene presence/absence table
    for index, row in df.iterrows():
        insert_query = f"INSERT INTO {table_name} ({', '.join(sanitized_columns)}) VALUES ({', '.join(['%s'] * len(sanitized_columns))})"
        cur.execute(insert_query, row.tolist())
    print(f"Data inserted into table '{table_name}'.")

def process_directory(directory, cur):
    # Process a directory containing gene presence/absence results
    results_path = os.path.join(directory, 'gene_presence_absence.Rtab')
    cluster_name = os.path.basename(directory)
    safe_cluster = re.sub(r'-+', '_', cluster_name)
    table_name = f"gene_presence_absence_{safe_cluster}"
    print(table_name)
    if not os.path.exists(results_path):
        print(f"❌ File does not exist: {results_path}")
        return False
    if os.path.getsize(results_path) == 0:
        print(f"⚠️ File is empty and will be skipped: {cluster_name}")
        with open("leeg_clusters_log.txt", "a") as log:
            log.write(f"{cluster_name}\n")
        return False
    try:
        df = pd.read_csv(results_path, header=0, sep='\t')
    except pd.errors.EmptyDataError:
        print(f"⚠️ No data found in file: {results_path}")
        with open("leeg_clusters_log.txt", "a") as log:
            log.write(f"{cluster_name}\n")
        return False
    if 'Unnamed: 0' in df.columns:
        df = df.rename(columns={'Unnamed: 0': 'Gene'})
    if df.shape[1] > 1600:
        print(f"🚫 Cluster '{cluster_name}' has too many columns ({df.shape[1]}) and will be skipped.")
        with open("te_grote_clusters_log.txt", "a") as log:
            log.write(f"{cluster_name}\n")
        return False
    sanitized_columns = create_gene_presence_absence_table(cur, table_name, df)
    insert_gene_presence_absence(cur, table_name, df, sanitized_columns)
    print(f"✅ Table '{table_name}' created and populated with data from '{results_path}'.")
    return True

def main():
    # Main function to orchestrate database setup and data insertion
    base_directory = "panaroo/panaroo_results/"
    conn = connect_to_db()
    cur = conn.cursor()
    drop_tables(cur)
    conn.commit()
    # Uncomment to create and insert Metadata table
    create_metadata_table(cur)
    conn.commit()
    try:
        metadata_df = pd.read_csv(snakemake.input.md, sep="|", engine='python')
        metadata_df = metadata_df.dropna(subset=['accession'])
        insert_metadata(cur, metadata_df)
        conn.commit()
    except pd.errors.ParserError as e:
        print(f"Error reading metadata: {e}")
    create_amr_table(cur)
    conn.commit()

    amr_df = pd.read_csv(snakemake.input.amr, sep="|")
    insert_amr_data(cur, amr_df)
    conn.commit()

    create_plasmidfinder_table(cur)
    conn.commit()

    insert_plasmidfinder_data(cur)
    conn.commit()
    with open(snakemake.output.outfile, "w") as confirmation:
        confirmation.write("Database uploaded!")
    

main()
