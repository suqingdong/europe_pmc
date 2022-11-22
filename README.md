# Open Access PDF Downloader with EuropePMC

## Installation
```bash
python3 -m pip install europe_pmc
```

## Usage
### CMD
```bash
epmc --help

# single download
epmc 30003000  # PMID
epmc PMC6039336 # PMCID
epmc 10.1007/s13205-018-1330-z # DOI
epmc "Identification of miRNAs and their targets in regulating tuberous root development" # Title

# batch download
epmc 30003000 30003001 30003002

# batch download from a file
epmc pmid.list

# specific output
epmc pmid.list --outdir paper --outfile {pubYear}.{pmid}.{title}.pdf

# multithreads download
epmc pmid.list --threads 4

# list only
epmc pmid.list --list

# show information only
epmc pmid.list --info
```

### Python
```python
from epmc import EuropePMC

pmc = EuropePMC()

r = pmc.fetch('30003000')
r = pmc.fetch('PMC6039336')
r = pmc.fetch('10.1007/s13205-018-1330-z')
print(r.pmid, r.pmcid, r.title)
print(r.data)
r.save()
r.save(outfile='output.pdf')
```
