#!/usr/bin/python3
import os, sys
import datetime
import argparse
import logging

storage_dir = os.path.expanduser('~/.wildwest')
domain_list = 'data/opendns-top-domains.txt'
resolver_file = 'data/resolvers.txt'
subfinder_config = 'configs/provider-config.yaml'

p = argparse.ArgumentParser(description='Assets Monitor')
p.add_argument('-x', '--proxy', type=str, help='Specify http proxy, like http://127.0.0.1:8080')
p.add_argument('-t', '--threads', type=int, default=10, help='Threads of subfinder, default 10')
p.add_argument('-v', '--version', action='store_true', help='Print version')
args = p.parse_args()
proxies = {'http': args.proxy, 'https': args.proxy}
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, stream=sys.stderr, datefmt='%Y-%m-%d %H:%M:%S')


def main():
    # storage
    storage_domains = storage_dir + '/domains.txt'
    storage_wilds = storage_dir + '/wilds.txt'  # ~/.asseter/wilds.txt
    storage_sub = storage_dir + '/subs'
    storage_all = storage_dir + '/all'
    batch = datetime.datetime.now().strftime('%Y-%m-%d')
    storage_sub_batch = f'{storage_sub}/{batch}'  # ~/.asseter/subs/2023-01-01
    storage_all_batch = f'{storage_all}/{batch}'
    last_batch = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    storage_all_last = f'{storage_all}/{last_batch}'
    os.popen(f'mkdir -p {storage_sub_batch} {storage_all_batch} 2>/dev/null').read()
    os.popen(f'rm {storage_sub_batch}/* 2>/dev/null').read()

    domains = []
    with open(domain_list, 'r') as f:
        for line in f.readlines():
            domain = line.strip('\r').strip('\n')
            if not domain:
                continue
            domains.append(domain)
    domains = sorted(domains)

    for domain in domains:
        logging.info(f'[{domain}] subdomain discovering')
        cmd = f"subfinder -silent -d {domain} -t {args.threads} -rL {resolver_file} -config {subfinder_config} > {storage_sub_batch}/{domain}.txt"
        os.popen(cmd).read()
        logging.info(f'[{domain}] dnstaker executing')
        cmd = f"dnstaker -s -l {storage_sub_batch}/{domain}.txt"
        os.popen(cmd).read()


if __name__ == '__main__':
    main()