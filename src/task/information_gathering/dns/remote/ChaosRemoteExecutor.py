import configparser
import tldextract
import luigi
import re

from ....helper.remote_command import *
from ....helper.create_instance import *

config = configparser.ConfigParser()


class ChaosRemoteExecutor(luigi.Task):
    """
    This luigi task is responsible for running the 'chaos' binary with options
    """
    config.read('src/task/config/command.ini')
    command_tpl = config.get('chaos', 'command')
    api_key = config.get('chaos', 'api_key')

    template = luigi.Parameter()
    provider_token = luigi.Parameter()

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _parsed: list = []
        _domains: list = []
        _subdomains: list = []

        instance_ip = return_new_instance(
            self.provider_token.__str__(),
            self.template.__str__()
        )

        if not instance_ip:
            raise Exception(f"VM creation failed or IP not assigned")

        conn = return_ssh_context(instance_ip, username='root', key_file="src/task/key/terraform_rsa")

        with self.input().open('r') as fp:
            [_domains.append(line.rstrip()) for line in fp]

        for _domain in _domains:
            stub_domain = tldextract.extract(_domain)
            _domain = f"{stub_domain.domain}.{stub_domain.suffix}"
            if _domain in _parsed:
                continue
            _parsed.append(_domain)
            _command = self.command_tpl.replace('**DOMAIN**', _domain)
            _command = _command.replace('**APIKEY**', self.api_key)
            proc_out = execute_command(conn, _command)
            if proc_out:
                items = proc_out.decode('utf8').split('\n')
                [_subdomains.append(_subdomain) for _subdomain in items
                 if re.findall(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', _subdomain)]

        destroy_instance(
            self.provider_token.__str__(),
            self.template.__str__()
        )

        if _subdomains:
            _subdomains = list(set(_subdomains))
            self.store({'subdomain': _subdomains})

        with self.output().open('w') as fp:
            [fp.write(_sub.rstrip() + '\n') for _sub in _subdomains]

    def output(self):
        raise NotImplemented
