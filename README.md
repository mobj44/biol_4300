# Getting the Data
## Running Script
To run the `get_data.py` script 
```bash
python3 get_data.py
```
<img src="./images/program_running.png" alt="Alt Text" style="width:60%; height:auto;">

## JSON Configuration
This script automatically looks for a `JSON` file in the same folder as the script named `config.json` if you want to pass in a differnt file it is the first argument given after the file name or you can specify using the `-f` or `--file` flag

<img src="./images/help_menu.png" alt="Alt Text" style="width:60%; height:auto;">

This program creates a folder called data in the same folder as the script if it doesn't already exist, and two files for every gene listed in the json. One is the table information and one is the multi-fasta file.  

The JSON has a list of any tax id you want to search for
As well as the following information on each gene you want to search for:
- **Name:** for logging on the console loading bar
- **Term:** used in the entrez term parameter 
- **File Prefix:** used to name each file, for example if I have a file prefix of `mt` I will get two files named, `mt_seqs_fasta` and `mt_table.csv`
Give the name 
For an example of the JSON format see `config.json`

# Environment Setup  
## Dependencies 
All of the library dependencies are located in the requirements.txt to install them into your own environemnt run:  
```python
pip install -r requirements.txt
```

## NCBI API Key
This code requires a API key from NCBI and email address. These should be in a .env file and never input directly into the code. 
For more informtion on getting an api key visit: [NCBI API Keys](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)

To setup your environment variables, edit the `api-key` and `email` in `.env.sample` and rename the file to remove `.sample`

```bash
ncbi_key=<api-key>
ncbi_email=<email>
```