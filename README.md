# Open Access PDF Downloader with EuropePMC

## Installation
```bash
python3 -m pip install europe_pmc
```

## Usage
### CMD
```bash
europe_pmc --help

# single download
europe_pmc 30003000  # PMID
europe_pmc PMC6039336 # PMCID
europe_pmc 10.1007/s13205-018-1330-z # DOI
europe_pmc "Identification of miRNAs and their targets in regulating tuberous root development" # Title

# batch download
europe_pmc 30003000 30003001 30003002

# batch download from a file
europe_pmc pmid.list

# specific output
europe_pmc pmid.list --outdir paper --outfile {pubYear}.{pmid}.{title}.pdf

# multithreads download
europe_pmc pmid.list --threads 4

# list only
europe_pmc pmid.list --list

# show information only
europe_pmc pmid.list --info
```

### Python
```python
from europe_pmc import EuropePMC

pmc = EuropePMC()

r = pmc.fetch('30003000')
r = pmc.fetch('PMC6039336')
r = pmc.fetch('10.1007/s13205-018-1330-z')
print(r.pmid, r.pmcid, r.title)
print(r.data)
r.save()
r.save(outfile='output.pdf')
```
