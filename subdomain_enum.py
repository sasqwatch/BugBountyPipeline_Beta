import tldextract
import luigi

from luigi.util import inherits
from src.task.data_collection import *
from src.task.helper.token import generate_token
from src.task.information_gathering.dns.local import *
from src.task.helper.database import return_database_handler


class _GetDataFromSource(GetDataFromSource.GetDataFromSource):

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-get_data_from_source-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _GetDomainsFromData(GetDomainsFromData.GetDomainsFromData):

    def requires(self):
        return _GetDataFromSource(nonce_token=self.nonce_token, data_source=self.data_source)

    def store(self, data: dict):
        my_db = return_database_handler()
        my_cursor = my_db.cursor()
        for _domain in data['domain']:
            sql = f"INSERT IGNORE INTO domains (id, domain) VALUES (NULL, '{_domain}')"
            my_cursor.execute(sql)
            my_db.commit()

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-get_domains_from_data-{self.nonce_token}.complete')


'''
@luigi.util.inherits(_GetDataFromSource)
class _ShodanExecutorTask(ShodanExecutor.ShodanExecutor):

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-shodan_executor-{self.nonce_token}.complete')
'''


@luigi.util.inherits(_GetDataFromSource)
class _ChaosExecutorTask(ChaosExecutor.ChaosExecutor):

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-chaos_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _AssetfinderExecutorTask(AssetfinderExecutor.AssetfinderExecutor):

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-assetfinder_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _AmassExecutorTask(AmassExecutor.AmassExecutor):

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-amass_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _SubfinderExecutorTask(SubfinderExecutor.SubfinderExecutor):

    def requires(self):
        return _GetDomainsFromData(nonce_token=self.nonce_token, data_source=self.data_source)

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-subfinder_executor-{self.nonce_token}.complete')


@luigi.util.inherits(_GetDataFromSource)
class _GetSubdomainsFromData(GetSubdomainsFromData.GetSubdomainsFromData):

    def requires(self):
        return {
            'task_a': _AmassExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source),
            'task_b': _AssetfinderExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source),
            'task_c': _ChaosExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source),
            # 'task_d': _ShodanExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source),
            'task_e': _SubfinderExecutorTask(nonce_token=self.nonce_token, data_source=self.data_source)
        }

    def store(self, data: dict):
        my_db = return_database_handler()
        my_cursor = my_db.cursor()
        for _subdomain in data['subdomain']:
            domain_parts = tldextract.extract(_subdomain)
            domain = f'{domain_parts.domain}.{domain_parts.suffix}'
            sql = f"INSERT IGNORE INTO subdomains (id, domain, subdomain) VALUES (NULL, '{domain}', '{_subdomain}')"
            my_cursor.execute(sql)
            my_db.commit()

    def output(self):
        return luigi.LocalTarget(f'/tmp/recon-collect_and_sort_domains-{self.nonce_token}.complete')


if __name__ == '__main__':
    token: str = generate_token()
    data_source: str = '/tmp/targets.txt'
    luigi.build([_GetSubdomainsFromData(nonce_token=token, data_source=data_source)], local_scheduler=True, workers=3)
