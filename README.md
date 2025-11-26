# Steps

1. Get Accession Numbers from Genbank. (`./scripts/get_tables.py`)
2. Create table with all accession numbers. (`./scripts/get_master_table.py`)
3. Get fasta data from Genbank. (`./scripts/get_fastas.py`)
4. Running initial alignments (`./scripts/get_alignments.sh`)
5. Trimming Alignments (`./scritps/trim_alignments.R`)
6. Create Supermatrix (`./scripts/supermat.R`)
7. Trees:
   - ML tres (see `./scripts/README.md` for more info)
   - Bayesian trees in BEAST (see `./scripts/README.md` for more info)
   - tree files are output to `./trees`
