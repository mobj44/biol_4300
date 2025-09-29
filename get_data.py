from dataclasses import dataclass
from Bio import Entrez as ez
import json
from dotenv import load_dotenv
import os
import csv
from pathlib import Path
import argparse
from tqdm import tqdm


@dataclass
class Gene:
    name: str
    term: str
    file_prefix: str


@dataclass
class Tax_info:
    tax_id: str
    scientific_name: str | None = None
    accession: str | None = None
    seq_name: str | None = None
    seq_len: str | None = None
    fasta: str = ""

    def get_sci_name(self):
        '''sets the scientific name of the Tax_info class'''
        tax_sum = ez.read(ez.esummary(db="taxonomy", id=self.tax_id))[0]
        self.scientific_name = tax_sum["ScientificName"]

    def nuc_processing(self, gene: str):
        '''gets and sets the accession, seq name, and seq length on the Tax_info class'''
        nuc_search = ez.read(ez.esearch(
            db="nuccore", term=f'txid{self.tax_id}[ORGN] AND {gene}', retmax=1))

        nuc_id = nuc_search["IdList"][0] if len(
            nuc_search["IdList"]) >= 1 else None
        if nuc_id is None:
            return
        nuc_sum = ez.read(ez.esummary(db="nuccore", id=nuc_id))[0]

        self.accession = nuc_sum["AccessionVersion"]
        self.seq_name = nuc_sum["Title"]
        self.seq_len = int(nuc_sum["Length"])

    def get_fasta_data(self) -> str | None:
        '''gets and sets a fasta property for the Tax_info class'''
        if self.accession is None:
            return ""
        fasta_resp = ez.efetch(
            db="nuccore", id=self.accession, rettype="fasta", retmode="text")
        self.fasta = f'>{self.scientific_name}\n{''.join(fasta_resp.readlines()[1:-2])}'


def create_path(wd: Path) -> Path:
    '''set/create folder path data will go in'''
    folder_path: Path = wd / "data"

    try:
        folder_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating folder: {e}")
    return folder_path


def get_tax_ids(ids: set[str]) -> set[str]:
    '''Gets list of tax ids to use for querying data'''
    tax_ids: set[str] = set()

    for i in ids:
        resp: dict[str, str] = ez.read(
            (ez.esearch(db="taxonomy", term=f'txid{i}[ORGN]', retmax=2000)))

        tax_ids.update(resp["IdList"])

    tax_ids -= ids
    return tax_ids


def create_csv(csv_name: Path, data: list[Tax_info]):
    '''
    creates csv file per gene that contains infomration in the 
    Tax_info class besides fasta
    '''
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


def create_fasta(file_name: Path, data: list[Tax_info]):
    '''creates a multi-fasta per gene'''
    with open(file_name, 'w') as fasta:
        for row in data:
            fasta.write(row.fasta)


def main():
    '''This is the main function'''
    # set working directory
    wd = Path(__file__).absolute().resolve().parent

    # parse command line arguments
    parser = argparse.ArgumentParser(
        description="A simple program to take in a json config and get data from NBCI databases")

    parser.add_argument(
        '-f',
        '--file',
        default='config.json',
        help='name of file for the program to injest'
    )

    args = parser.parse_args()

    # load env variables for email and api key
    load_dotenv()
    ez.email = os.getenv("ncbi_email")
    ez.api_key = os.getenv("ncbi_key")

    folder_path = create_path(wd)

    # read in config file
    if not os.path.exists(wd / args.file):
        print('ERROR: Config file not found.')
        return

    with open(wd / args.file, 'r') as config_file:
        data = json.load(config_file)

    genera_ids: set[str] = set(data["genera_ids"])
    gene_json: list[dict[str, str]] = data["genes"]

    genes: list[Gene] = []

    for gene in gene_json:
        name, term, prefix = gene.values()
        genes.append(Gene(name, term, prefix))

    # gets tax ids
    txids: list[str] = list(get_tax_ids(genera_ids))

    for gene_config in genes:
        tax_data: list[Tax_info] = []

        fasta_name: Path = folder_path / \
            f'{gene_config.file_prefix}_seqs.fasta'
        csv_name: Path = folder_path / f'{gene_config.file_prefix}_table.csv'

        with tqdm(total=len(txids), desc=gene_config.name) as progress:
            for tax_id in txids:
                tax = Tax_info(tax_id)
                tax.get_sci_name()
                tax.nuc_processing(gene_config.term)
                tax_data.append(tax)
                tax.get_fasta_data()

                progress.update(1)

        create_csv(csv_name, tax_data)
        create_fasta(fasta_name, tax_data)


if __name__ == "__main__":
    main()
