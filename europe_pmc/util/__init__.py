import re
from pathlib import Path

import tqdm
import click
import requests
import human_readable
from simple_loggers import SimpleLogger


def safe_open(filename, mode='r'):
    """open file safely
    """
    file = Path(filename)

    if 'w' in mode and not file.parent.exists():
        file.parent.mkdir(parents=True)

    if str(filename).endswith('.gz'):
        import gzip
        return gzip.open(filename, mode=mode)

    return file.open(mode=mode)


def download(url, outfile=None, outdir='.', chunk_size=1024 * 4, progress=True):
    """download file from url
    """
    resp = requests.get(url, stream=True)
    length = int(resp.headers.get('Content-Length', 0))

    if not outfile:
        disposition = resp.headers.get('Content-Disposition')
        outfile = re.findall(r'filename="(.+)"', disposition)[0]

    SimpleLogger('Download').debug(f'downloading to: {Path(outdir).joinpath(outfile)} [{human_readable.file_size(length, gnu=True)}]')

    desc = click.style(f'downloading {outfile}', fg='bright_cyan', italic=True)
    with safe_open(Path(outdir).joinpath(outfile), 'wb') as out, file_download_bar(length, desc=desc) as bar:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            out.write(chunk)
            bar.update(len(chunk))


def file_download_bar(total, desc='', colour='green'):
    """generate file download progress bar
    """
    bar = tqdm.tqdm(total=total,
                    desc=desc,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    colour=colour)
    return bar


def check_term_type(term):
    """check term type: pmid, pmcid, doi or title
    """
    if re.match(r'pmc\d{7}', term, re.IGNORECASE):
        term_type = 'pmcid'
    elif term.isdigit():
        term_type = 'pmid'
    elif re.match(r'\d{2}\.\d{4}/', term):
        term_type = 'doi'
    else:
        term_type = 'title'
    return term_type
