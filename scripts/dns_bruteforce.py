#!/usr/bin/python3
import os
import sys
import argparse


output_dir = 'results'

p = argparse.ArgumentParser()
p.add_argument('-dL', '--domain-file', help='domain filename')
p.add_argument('-w', '--wordlist', help='wordlist')
args = p.parse_args()

domains = []
with open(args.domain_file, 'r') as f:
    for line in f.readlines():
        domain = line.strip('\r').strip('\n')
        domains.append(domain)

for domain in domains:
    cmd = f"puredns bruteforce {args.wordlist} {domain} -r resolvers.txt -w {output_dir}/{domain}.txt -q --wildcard-batch 1000000"
    sys.stderr.write(f'testing {domain}\n')
    os.popen(cmd).read()