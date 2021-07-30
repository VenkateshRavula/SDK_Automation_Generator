# To add default values in config - python collection_config.py
# To add customised config - python collection_config.py -a "1.1.1.1" -u "Admin" -p "admin" -d "OVAD" -i "1.1.2.2" -v 3200 -w "Synergy" -l oneview-ansible-collection
import argparse
import os
config_file = 'oneview_config.json'


def replace_config_file(configfile, config):
    f_write = open(configfile, 'w')
    f_write.write(config)
    f_write.close()


def load_collection_config(config, path=""):
    if path:
        os.chdir(path)
    parent_dir = os.getcwd()
    os.chdir('roles')
    for item in os.listdir('.'):
        role_file_path = os.path.join(os.getcwd(), item, 'files')
        if os.path.exists(role_file_path):
            config_file_path = os.path.join(role_file_path, config_file)
            replace_config_file(config_file_path, config)


def main():
    parser = argparse.ArgumentParser(add_help=True, description='Usage')
    parser.add_argument('-a', '--appliance', dest='hostname', required=False,
                        default='<oneview_ip>', help='HPE OneView Appliance hostname or IP')
    parser.add_argument('-u', '--user', dest='user', required=False,
                        default='<user_name>', help='HPE OneView Username')
    parser.add_argument('-p', '--pass', dest='passwd', required=False,
                        default='<password>', help='HPE OneView Password')
    parser.add_argument('-d', '--domain', dest='domain', required=False,
                        default='<domain_directory>', help='HPE OneView auth login domain')
    parser.add_argument('-v', '--apiversion', dest='version', required=False,
                        default=3000, help='HPE OneView api version')
    parser.add_argument('-w', '--hardwarevariant', dest='variant', required=False,
                        default='Synergy', help='HPE OneView hardware variant')
    parser.add_argument('-i', '--i3s', dest='i3s', required=False,
                        default='<i3s_ip>', help='HPE OneView i3s ip')
    parser.add_argument('-l', '--path', dest='path', required=False,
                        default='oneview-ansible-collection', help='Ansible collection SDK path')

    args = parser.parse_args()

    arguments = (args.hostname, args.user, args.passwd, args.domain, args.i3s, args.version, args.variant)

    config = """{
    "ip": "%s",
    "credentials": {
        "userName": "%s",
        "password": "%s",
        "authLoginDomain": "%s"
    },
    "image_streamer_ip": "%s",
    "api_version": %s,
    "variant": "%s"\n}\n""" % (arguments)

    load_collection_config(config, args.path)


if __name__ == '__main__':
    main()
