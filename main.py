from dataclasses import dataclass
from Bio import Entrez as ez
import json
from dotenv import load_dotenv
import os
import csv
from pathlib import Path

@dataclass
class Gene:
    name: str
    term: str
    file_prefix: str

@dataclass
class Tax_info:
    tax_id: str
    scientific_name: str
    accession: str | None = None
    seq_name: str | None = None
    seq_len: str | None = None

    def __str__(self) -> str:
        return f'Tax ID: {self.tax_id}\nScientific Name: {self.scientific_name}\nAccession: {self.accession}\nSeq Name: {self.seq_name}\nSeq Length: {self.seq_len}'
    

def get_tax_ids(ids: set[str]) -> set[str]:
    tax_ids: set[str] = set()

    for i in ids:
        resp: dict[str, str] = ez.read((ez.esearch(db = "taxonomy", term=f'txid{i}[ORGN]', retmax = 2000))) # type: ignore
        
        tax_ids.update(resp["IdList"])
    
    tax_ids -= ids
    return tax_ids

def create_csv(csv_name: str, data: list[Tax_info]):
    headers = ["tax_id", "scientific_name", "accession", "seq_name", "seq_len"]

    with open(csv_name, 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        writer.writeheader()

        for row in data:
            writer.writerow({
                'tax_id':  row.tax_id,
                'scientific_name': row.scientific_name,
                'accession': row.accession,
                'seq_name': row.seq_name,
                'seq_len': row.seq_len
            })

def main(): 
    # load env variables for email and api key
    load_dotenv()
    ez.email = os.getenv("ncbi_email")
    ez.api_key = os.getenv("ncbi_key")

    # set/create folder path data will go in
    folder_path: Path  = Path("./data")

    try:
        folder_path.mkdir(parents = True, exist_ok = True)
    except OSError as e:
        print(f"Error creating folder: {e}")
        return

    # read in config file
    with open('./genes.json', 'r') as config_file:
        data = json.load(config_file)
    
    genera_ids: set[str] = set(data["genera_ids"])
    gene_json: list[dict[str, str]] = data["genes"]

    genes: list[Gene] = []

    for gene in gene_json:
        name, term, prefix = gene.values()
        genes.append(Gene(name, term, prefix))

    # gets tax ids
    txids: list[str] = list(get_tax_ids(genera_ids))


    gene = genes[0].term

    
    tax_data: list[Tax_info] = []

    for i in range(len(txids)):
        tax_sum = ez.read(ez.esummary(db = "taxonomy", id = txids[i]))[0] # type: ignore
        scientific_name: str = tax_sum["ScientificName"] # type: ignore

        nuc_search = ez.read(ez.esearch(db = "nuccore", term = f'txid{txids[i]}[ORGN] AND {gene}', retmax = 1)) # type: ignore

        nuc_id = nuc_search["IdList"][0] if len(nuc_search["IdList"]) >= 1 else None # type: ignore
        if not nuc_id:
            tax_data.append(Tax_info(txids[i], scientific_name))
        
        else:
            nuc_sum = ez.read(ez.esummary(db = "nuccore", id = nuc_search["IdList"][0]))[0] # type: ignore

            accession: str = nuc_sum["AccessionVersion"] # type: ignore
            seq_name: str = nuc_sum["Title"] # type: ignore
            seq_len: str = int(nuc_sum["Length"]) # type: ignore

            tax_data.append(Tax_info(txids[i], scientific_name, accession, seq_name, seq_len))

            fasta_resp = ez.efetch(db = "nuccore", id = tax_data[i].accession, rettype = "fasta", retmode= "text") # type: ignore
            fasta_data = f'>{tax_data[i].scientific_name}\n{''.join(fasta_resp.readlines()[1:-2])}'

            fasta_name: str = f'{folder_path}/{genes[0].file_prefix}_seqs.fasta'

            with open(fasta_name, 'a') as fasta:
                fasta.write(fasta_data)


    csv_name: str = f'{folder_path}/{genes[0].file_prefix}_table.csv'
    create_csv(csv_name, tax_data)
    

if __name__=="__main__":
    main()