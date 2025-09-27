# Getting the Data


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