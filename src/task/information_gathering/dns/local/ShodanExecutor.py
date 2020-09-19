import configparser
import luigi
import re

from ....helper.local_command import *

config = configparser.ConfigParser()


class ShodanExecutor(luigi.Task):
    """
    This luigi task is responsible for running the 'shodan' binary with options
    """
    config.read('src/task/config/command.ini')
    command_tpl = config.get('shodan', 'command')
    api_key = config.get('shodan', 'api_key')

    def requires(self):
        raise NotImplemented

    def store(self, data: dict):
        pass

    def run(self):
        _domains: list = []
        _subdomains: list = []

        with self.input().open('r') as fp:
            [_domains.append(line.rstrip()) for line in fp]

        for _domain in _domains:
            _command = self.command_tpl.replace('**DOMAIN**', _domain)
            _ = chain(f"/usr/bin/shodan init {self.api_key}")
            proc_out = chain(_command.rstrip())
            if proc_out:
                [_subdomains.append(_subdomain) for _subdomain in proc_out
                 if re.findall(r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$', _subdomain)]

        if _subdomains:
            _subdomains = list(set(_subdomains))
            self.store({'subdomain': _subdomains})

        with self.output().open('w') as fp:
            [fp.write(_sub.rstrip() + '\n') for _sub in _subdomains]

    def output(self):
        raise NotImplemented
