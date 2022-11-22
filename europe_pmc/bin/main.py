import time
import json
from pathlib import Path
from multiprocessing.pool import ThreadPool

import click

from europe_pmc import EuropePMC, version_info


__epilog__ = click.style('''

\b
examples:
    \b
    # single download PMID, PMCID, DOI or Title
    epmc --help
    epmc 30003000  # PMID
    epmc PMC6039336 # PMCID
    epmc 10.1007/s13205-018-1330-z # DOI
    epmc "Identification of miRNAs and their targets in regulating tuberous root development" # Title
    \b
    # batch download
    epmc 30003000 30003001 30003002
    \b
    # batch download from a file
    epmc pmid.list
    \b
    # specific output
    epmc pmid.list --outdir paper --outfile {{pubYear}}.{{pmid}}.{{title}}.pdf
    \b
    # multithreads download
    epmc pmid.list --threads 4
    \b
    # list only
    epmc pmid.list --list
    \b
    # show information only
    epmc pmid.list --info

contact: {author} <{author_email}>
''', fg='cyan').format(**version_info)

@click.command(
    name='epmc',
    no_args_is_help=True,
    epilog=__epilog__,
    help=click.style('Open Access PDF Downloader with EuropePMC', fg='green', bold=True, italic=True),
)
@click.argument('term', nargs=-1)
@click.option('-O', '--outdir', help='the output directory', default='pdf', show_default=True)
@click.option('-o', '--outfile', help='the template of output filename, eg. "{pmcid}.pdf", "{pubYear}.{pmid}.{title}.pdf"')
@click.option('-l', '--list', help='list pdf url only', is_flag=True)
@click.option('-i', '--info', help='show informations only', is_flag=True)
@click.option('--indent', help='the indent for information output', type=int)
@click.option('--threads', help='the threads number for downloading', type=int, default=1, show_default=True)
@click.version_option(version=version_info['version'], prog_name=version_info['prog'])
def cli(**kwargs):
    start_time = time.time()
    outfile = kwargs['outfile']
    outdir = kwargs['outdir']
    
    pmc = EuropePMC()

    terms = []
    for each in kwargs['term']:
        if Path(each).is_file():
            with Path(each).open() as f:
                for line in f:
                    terms += line.strip().split(',')
        else:
            terms.append(each)

    pmc.logger.debug(f'total terms: {len(terms)}')

    failed = []
    results = []
    dups = {}
    for term in terms:
        res = pmc.fetch(term)
        if res._error:
            pmc.logger.error(res._error)
            failed.append({'term': term, 'error': res._error})
            continue

        if res.pmid in dups:
            continue
        dups[res.pmid] = 1

        if kwargs['info']:
            results.append(res)
            continue

        if res.hasPDF == 'N':
            failed.append({'term': term, 'error': f'no pdf for PMID:{res.pmid}'})
            continue

        out = None
        if outfile:
            try:
                out = outfile.format(**res.data)
            except Exception:
                pmc.logger.warning(f'bad outfile format: {outfile}')
            
        res.outfile = out
        res.outdir = outdir
        results.append(res)

    if kwargs['list']:
        print('PMCID', 'PMID', 'PDF_URL', sep='\t')
        for res in results:
            print(res.pmcid, res.pmid, res.pdf_url, sep='\t')
    elif kwargs['info']:
        for res in results:
            info = json.dumps(res.data, indent=kwargs['indent'], ensure_ascii=False)
            print(info)
    else:
        pool = ThreadPool(kwargs['threads'])
        for res in results:
            pool.apply_async(res.save, kwds=dict(outfile=res.outfile, outdir=res.outdir))
        pool.close()
        pool.join()
        pmc.logger.info(f'all files are saved in: {outdir}')

    if failed:
        pmc.logger.warning('the failed terms are as follows:')
        for item in failed:
            print(item)

    pmc.logger.info('total times: {:.1f}s'.format(time.time() - start_time))


def main():
    cli()


if __name__ == '__main__':
    main()
