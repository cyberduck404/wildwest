#!/usr/bin/python3
# todo://
import sys
import asyncio, aiohttp
import argparse, logging
import gc


paths = [
    '.well-known/security.txt',
    'security.txt'
]

# args
p = argparse.ArgumentParser(description='DNStaker')
p.add_argument('-l', '--domainlist', type=str, help='Domain list filename')
p.add_argument('-x', '--proxy', type=str, help='Specify http proxy, like http://127.0.0.1:8080')
p.add_argument('-mc', '--max-conn', type=int, default=500, help='Aiohttp max conn')
p.add_argument('-sw', '--single-waiting', type=int, default=30, help='Aiohhtp single waiting')
p.add_argument('--debug', action='store_true', help='Debug')
p.add_argument('-v', '--version', action='store_true', help='Print version')
args = p.parse_args()
max_conn = args.max_conn
single_waiting = args.single_waiting
proxies = {'http': args.proxy, 'https': args.proxy}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    "Cache-Control": "max-age=0",
}

async def async_request(session, domain, proxy=None):
    for path in paths:
        url = f'https://{domain}/{path}'
        try:
            async with session.get(url, proxy=proxy, allow_redirects=False) as resp:
                text = await resp.text()
                if (resp.status == 200) and ("Contact:" in text) and (1024 >= len(text) > 0):
                    sys.stdout.write(f'{url}\n')
                    break
        except (
            asyncio.TimeoutError,
            aiohttp.ClientConnectorCertificateError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientOSError,
            aiohttp.ClientConnectorError,
            aiohttp.ClientProxyConnectionError,
            aiohttp.ClientSSLError,
            aiohttp.ClientConnectorSSLError,
            aiohttp.ClientPayloadError,
            aiohttp.ClientResponseError,
            aiohttp.ClientHttpProxyError,
            aiohttp.WSServerHandshakeError,
            aiohttp.ContentTypeError,
        ) as e:
            logging.debug(f'[!] [{e}] {url}')
        except RuntimeError as e:
            logging.debug(f'[!] [{e}] {url}')
        except UnicodeDecodeError as e:
            logging.debug(f'[!] [{e}] {url}')

# main
async def main():
    logging.info('reading domains')
    domains = []
    with open(args.domainlist, 'r') as f:
        for line in f.readlines():
            domain = line.strip('\r').strip('\n')
            if not domain:
                continue
            domains.append(domain)
    domains = sorted(list(set(domains)))
    length = len(domains)

    # async dns resolve
    logging.info('searching bbp in wild')
    count = 0
    timeout = aiohttp.ClientTimeout(total=single_waiting, sock_connect=single_waiting, sock_read=single_waiting)
    connector = aiohttp.TCPConnector(limit=max_conn, ssl=False)
    async with aiohttp.ClientSession(headers=headers, connector=connector, timeout=timeout) as s:
        while count < length:
            sliced = domains[count:count+max_conn]
            tasks = []
            # async http
            for domain in sliced:
                tasks.append(asyncio.ensure_future(async_request(s, url, proxy=args.proxy)))
            await asyncio.gather(*tasks)
            s.cookie_jar.clear()

            # the end of loop
            del tasks
            gc.collect()
            count += max_conn


if __name__ == '__main__':
    asyncio.run(main())