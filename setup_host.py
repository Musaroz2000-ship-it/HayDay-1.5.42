import json
import sys
from Utils.Net import get_lan_ip


def main():
    ip = sys.argv[1] if len(sys.argv) > 1 else get_lan_ip()
    conf = json.load(open('config.json'))
    if conf.get('Host') != ip:
        conf['Host'] = ip
        json.dump(conf, open('config.json', 'w'), indent=4)
    print('[*] LAN IP: {} (written to config.json Host)'.format(ip))
    print('[*] Use this same IP when patching the client IPA')


if __name__ == '__main__':
    main()
