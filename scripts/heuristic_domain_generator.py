#!/usr/bin/python3
import re, argparse


p = argparse.ArgumentParser(description='DNStaker')
p.add_argument('-l', '--domain-list', type=str, help='Domain list filename')
p.add_argument('-o', '--output', help='dst')
args = p.parse_args()

def extract_sld(domain):
    domain = re.sub('.com.cn', '.com', domain)
    if match := re.search(r'\.([a-z0-9_-]+\.[a-z]+$)', domain):
        sld = match.group(1)
    else:
        sld = ''
    return re.sub(f'.{sld}', '', domain), sld

def main():
    domains = []
    with open(args.domain_list, 'r') as f:
        for line in f.readlines():
            line = line.strip('\r').strip('\n')
            if not line:
                continue
            domains.append(line)

    slds, subs = [], []
    for domain in domains:
        sub, sld = extract_sld(domain)
        if not sld:
            continue
        subs.append(sub)
        slds.append(sld)
    subs = sorted(list(set(subs)))
    slds = sorted(list(set(slds)))
    with open(args.output, 'w') as f:
        for sub in subs:
            for sld in slds:
                f.write(f'{sub}.{sld}\n')


if __name__ == '__main__':
    main()