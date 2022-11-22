import requests
from simple_loggers import SimpleLogger

from europe_pmc import util


class PMCResult(object):
    def __init__(self, data):
        self.data = data
        self.pmcid = data.get('pmcid')
        for k, v in data.items():
            setattr(self, k, v)

    def __str__(self):
        return f'PMCResult<PMCID:{self.pmcid}>'


    def save(self, outfile=None, outdir='.', **kwargs):
        if hasattr(self, 'pdf_url'):
            util.download(self.pdf_url, outfile=outfile, outdir=outdir, **kwargs)
            return True

        return False

    __repr__ = __str__


class EuropePMC(object):
    """https://europepmc.org/RestfulWebService
    """
    REST_URL = 'https://www.ebi.ac.uk/europepmc/webservices/rest'

    def __init__(self):
        self.params = {'format': 'json', 'pageSize': '1'}
        self.logger = SimpleLogger('EuropePMC')

    def fetch(self, term):
        """fetch a term: pmid, pmcid, doi or title
        """
        term_type = util.check_term_type(term)
        self.logger.debug(f'search: {term_type} = {term}')
        if term_type == 'pmid':
            data = self.article(term)
        else:
            data = self.search(f'{term_type}:{term}')


        data['_search'] = f'{term}[{term_type}]'

        pmcid = data.get('pmcid')
        if pmcid:
            data['pdf_url'] = f'https://europepmc.org/backend/ptpmcrender.fcgi?accid={pmcid}&blobtype=pdf'

        result = PMCResult(data)

        return result

    def search(self, query):
        """search entrypoint
        """
        url = self.REST_URL + '/search'
        params = {**self.params, 'query': query}
        res = requests.get(url, params=params).json()
        count = res['hitCount']
        result = res['resultList']['result']

        error = ''
        data = {}
        if count == 1:
            data = result[0]
        elif count == 0:
            error = f'no result found: {query}'
        else:
            error = f'{count} results found: {query}'

        return {**data, '_error': error}

    def article(self, _id, source='MED'):
        """article entrypoint
        https://europepmc.org/Help#contentsources
        """
        url = self.REST_URL + f'/article/{source}/{_id}'
        result = requests.get(url, params=self.params).json()['result']
        error = f'no result found: {_id} [{source}]' if not result else ''

        return {**result, '_error': error}


if __name__ == '__main__':
    pmc = EuropePMC()

    # pmc.fetch('30003000')
    # pmc.fetch('PMC6039336')
    # pmc.fetch('10.1007/s13205-018-1330-z')
    # pmc.fetch('Identification of miRNAs and their targets in regulating tuberous root development')

    # pmc.fetch('123123123123123')
    # pmc.fetch('ngs')
    # pmc.fetch('sdfsdfsdfsdfsdf')

    r = pmc.fetch('30003000')

    util.download(r.pdf_url, r.pmcid + '.pdf')



