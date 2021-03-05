
import logging, fileinput, fnmatch, subprocess
import requests
from bs4 import BeautifulSoup
import sys
import os
from datetime import datetime
import re
from subprocess import Popen, STDOUT, PIPE
from ansible_playbook_runner import Runner

api_version = '2200'

rel_dict = {'FC Networks': 'fc_networks',
            'FCoE Networks': 'fcoe_networks',
            'Ethernet Networks': 'ethernet_networks',
            'Network Sets': 'network_sets',
            'Connection Templates': 'connection_templates',
            'Certificates Server': 'certificates_server',
            'Enclosures': 'enclosures',
            'Enclosure Groups': 'enclosure_groups',
            'Firmware Drivers': 'firmware_drivers',
            'Hypervisor Cluster Profiles': 'hypervisor_cluster_profiles',
            'Hypervisor Managers': 'hypervisor_managers',
            'Interconnects': 'interconnects',
            'Interconnect Types': 'interconnect_types',
            'Logical Enclosures': 'logical_enclosures',
            'Logical Interconnects': 'logical_interconnects',
            'Logical Interconnect Groups': 'logical_interconnect_groups',
            'Scopes': 'scopes',
            'Server Hardware': 'server_hardware',
            'Server Hardware Types': 'server_hardware_types',
            'Server Profiles': 'server_profiles',
            'Server Profile Templates': 'server_profile_templates',
            'Storage Pools': 'storage_pools',
            'Storage Systems': 'storage_systems',
            'Storage Volume Templates': 'storage_volume_templates',
            'Storage Volume Attachments': 'storage_volume_attachments',
            'Volumes': 'volumes',
            'Tasks': 'tasks',
            'Uplink Sets': 'uplink_sets'
            }

class DataFromWebScraping(object):
    def __init__(self, ele):
        self.ele = ele
        if self.ele == 'certificates_server':
            self.replaced_ele = self.ele.replace('certificates_server', '/certificates/servers')
        elif self.ele == 'volumes':
            self.replaced_ele = self.ele.replace('volumes', 'storage-volumes')
        else:
            self.replaced_ele = self.ele.replace('_', '-')

    def data_scraped(self):
        """
        Scrapping data for list of endpoints from API docs.
        """
        URL = "https://techlibrary.hpe.com/docs/enterprise/servers/oneview5.3/cicf-api/en/rest/" + self.replaced_ele + ".html.js"
        r = requests.get(URL)

        soup = BeautifulSoup(r.content, 'html5lib')  # If this line causes an error, run 'pip install html5lib' or install html5lib
        body = soup.find('body')
        string = str(body).replace('<body>define([],"', '').replace('");</body>', '')
        soup = BeautifulSoup(string, 'html5lib')
        api_list = soup.find('div', {"class": "\\\"api-list\\\""})
        api_with_method = []
        http_methods = []
        apis = []
        for span in api_list.find_all('span', {'class', '\\\"uri\\\"'}):
            apis.append(span.text.strip())
        for span in api_list.find_all('span', {'class', '\\\"method'}):
            http_methods.append(span.text.strip())
        for http_method, api in zip(http_methods, apis):
            api_with_method.append({api, http_method})
        
        return api_with_method

class Tee(object):
    """
    To show logs on console and flushing the same to logs file.
    """
    def __init__(self, filename):
        self.stdout = sys.stdout
        self.file = filename

    def write(self, obj):
        self.file.write(obj)
        self.stdout.write(obj)
        self.file.flush()

    def flush(self):
        self.stdout.flush()
        self.file.flush()

def runAnsiblePlaybooks(success_files, failed_files):
    """
    To run ansible playbooks using python module.
    """
    ansible_modules_list = open('ansible_modules_list', 'r')
    resources_for_ansible = ansible_modules_list.read().splitlines()
    ansible_modules_list.close()
    loaded_resources_for_ansible = modifyExecutedFiles(resources_for_ansible)
    print("loaded_resources for ansible are {}".format(str(loaded_resources_for_ansible)))
    try:
        for resource_for_ansible in resources_for_ansible:
            result = Runner(['/etc/ansible/hosts'], resource_for_ansible).run()
            if result == 0:
                success_files.append(resource_for_ansible)
            else:
                failed_files.append(resource_for_ansible)
    except Exception as e:
        print("Error while executing playbook {}".format(str(e)))

    return success_files, failed_files

def LoadResourcesFromFile():
    """
    To load resources(examples) from external config file.
    """
    resource_file = open('re.txt','r')
    resources_from_file = resource_file.read().splitlines()
    resource_file.close()
    return resources_from_file

def modifyExecutedFiles(executed_files):
    """
    Modifying ansible playbook names to make them uniform across all SDK's
    """
    exe = []
    for executed_file in executed_files:
        executed_file = executed_file.replace('.yml', '').replace('oneview_', '').replace('_facts', '')
        executed_file = executed_file + 's'
        exe.append(executed_file)
    return list(set(exe))

def ExecuteFiles(selected_sdk):
    is_ansible = False
    if selected_sdk not in ['ansible']:
        loaded_resources = LoadResourcesFromFile()
        print("loaded_resources are {}".format(str(loaded_resources)))
    cwd = os.getcwd()
    failed_files = []
    success_files = []
    examples = []
    val = selected_sdk
    valid_sdks = ['python', 'ruby', 'go', 'ansible', 'puppet', 'chef']
    if val in ['ruby', 'chef', 'puppet']:
        rel_dict2 = {'Storage Volume Templates': 'volume_templates',
                     'Storage Volume Attachments': 'volume_attachments',
                     'Certificates Server': 'server_certificates',
                     'Server Hardware': 'server_hardwares',
                    }
        rel_dict.update(rel_dict2)
    else:
        pass
    print("Started executing files")
    LOG_FILENAME = datetime.now().strftime('logfile_%H_%M_%d_%m_%Y.log')
    f = open(LOG_FILENAME, 'w')
    original = sys.stdout
    sys.stdout = Tee(f)
    
    if val in valid_sdks and val == 'ansible':
        is_ansible = True
        success_files, failed_files = runAnsiblePlaybooks(success_files, failed_files)
        return success_files, is_ansible
        f.close() 
    else:
        pass

    if val in valid_sdks and val != 'ansible':
        for ele in loaded_resources:
            examples.append(rel_dict[ele])
        for example in examples:
            example_file = cwd + '/' + example
            try:
                if val == 'python':
                    example_file_with_extension = example_file + str('.py')
                    print(">> Executing {}..".format(example))
                    exec(compile(open(example_file_with_extension).read(), example_file_with_extension, 'exec'))
                    success_files.append(example)
                elif val == 'ruby' and example not in ['tasks', 'interconnect_types']:
                    example_file_with_extension = example_file[:-1] + str('.rb')
                    cmd = "ruby {}".format(example_file_with_extension)
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                    p.wait()
                    contents = p.stdout.read()
                    print(contents)
                    output, errors = p.communicate()
                    if errors is  None:
                        success_files.append(example)
                    else:
                        failed_files.append(example)
                elif val == 'go':
                    value_updated = input("\nPlease provide \"true\" as input if below mentioned example have varaiable updated with described values as below else provide \"false\" as input to terminate\n\nexamples/server_certificate.go\n\tserver_certificate_ip\t= \"172.18.11.11\"\nexamples/hypervisor_managers.go\n\thypervisor_manager_ip\t= \"172.18.13.11\"//\"<hypervisor_manager_ip>\"\n\tusername\t= \"dcs\" //\"<hypervisor_user_name>\"\n\tpassword\t= \"dcs\" //\"<hypervisor_password>\"\nexamples/storage_systems.go\n\tusername\t=\"dcs\"\n\tpassword\t=\"dcs\"\n\thost_ip \t=\"172.18.11.11\"\n\thost2_ip\t=\"172.18.11.12\"\n>>")
                    if value_updated.lower() == 'false':
                        sys.exit()
                    example_file_with_extension = example_file + str('.go')
                    cmd = "go run {}".format(example_file_with_extension)
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                    p.wait()
                    contents = p.stdout.read()
                    print(contents)
                    output, errors = p.communicate()
                    if errors is  None:
                        success_files.append(example)
                    else:
                        failed_files.append(example)
                elif val == 'puppet'and example not in ['tasks', 'scopes', 'interconnect_types']:
                    example_file_with_extension = example_file[:-1] + str('.pp')
                    cmd = "puppet apply --modulepath={}".format(example_file_with_extension)
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                    p.wait()
                    contents = p.stdout.read()
                    print(contents)
                    output, errors = p.communicate()
                    if errors is  None:
                        success_files.append(example)
                    else:
                        failed_files.append(example)
                elif val == 'chef'and example not in ['tasks', 'scopes', 'interconnect_types']:
                    example_file_with_extension = example_file[:-1] + str('.rb')
                    cmd = "chef client -z -o oneview::{}".format(example)
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                    p.wait()
                    contents = p.stdout.read()
                    print(contents)
                    output, errors = p.communicate()
                    if errors is  None:
                        success_files.append(example)
                    else:
                        failed_files.append(example)
                else:
                    pass

            except Exception as e:
                print("Failed to execute {} with exception {}".format(str(example),(str(e))))
                failed_files.append(example)
        sys.stdout = original
        print("success files are {}".format(str(success_files)))
        return success_files, is_ansible, val
        f.close()

    else:
        print("Sorry, please enter the valid SDK among the following {}".format(str(valid_sdks)))

class WriteToChangeLog(object):
    """
    Here we have exception handling. In case if any of the value for the key is not present,
    then it will raise a exception and we are catching it. Our script will continue further and
    will add modules other than the missing one.

    Output will look like:
    ##### Features supported with the current release(v5.0.0)
    - FC Network
    - FCOE-Network

    :param rel_list:
    :param rel_version:
    :return:
    """
    def __init__(self, rel_list, sdk):
        self.rel_list = rel_list
        self.sdk = sdk
        if self.sdk == 'ruby':
            path_parent = os.path.dirname(os.getcwd())
            os.chdir(path_parent)
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)
        print(os.getcwd())
        f = open("CHANGELOG.md", "r")
        first_line = f.readline()
        file_name = 'CHANGELOG.md'
        list_of_linenos = self.search_string_in_file(first_line, file_name)
        if list_of_linenos is not None and len(list_of_linenos) is not None:
            self.delete_multiple_lines(file_name, list_of_linenos)
            self.added_integer = float(first_line[2:5])
        else:
            self.added_integer = float(first_line[2:5]) + float('0.1')
        self.final_version = str(self.added_integer) + '.0'

        f.close()

    def delete_multiple_lines(self, file_name, linenos):
        start = int(linenos[0])
        end = int(linenos[1])
        count = end - start
        for line in fileinput.input(file_name, inplace=1, backup='.orig'):
            if start <= fileinput.lineno() < start + count:
                pass
            else:
                print(line[:-1])
        fileinput.close()

    def search_string_in_file(self, first_line, file_name):
        line_number = 0
        count = 0
        list_of_results = []
        if(first_line[8:18] == 'unreleased' or first_line[8:18] == 'Unreleased'):
            with open(file_name, 'r') as read_obj:
                for line in read_obj:
                    if count == 2:
                        break
                    else:
                        line_number += 1
                        if re.search("^#\s([0-9][.]*){2}", line):
                            list_of_results.append(line_number)
                            count += 1
            return list_of_results

    def write_data(self):
        rel_modules = []
        oneview_api_version = 'OneView ' + 'v' + str(self.added_integer)
        try:
            for ele in self.rel_list:
                 rel_modules.append(list(rel_dict.keys())[list(rel_dict.values()).index(ele)])
            print(str(rel_modules))
        except Exception as e:
            logging.debug("Unable to find a module {0}".format(str(e)))

        print("Started writing to CHANGELOG")
        try:
            dummy_file = open("dummy_CHANGELOG.md", "w")
            dummy_file.write("# {}(unreleased)".format(str(self.final_version)))
            dummy_file.write("\n#### Notes\n")
            dummy_file.write("Extends support of the SDK to OneView REST API version {} ({})".format(str(api_version),str(oneview_api_version)))
            dummy_file.write("\n\n##### Features supported with the current release\n")
            for ele in sorted(rel_modules):
                dummy_file.write("- {0} \n".format(str(ele)))
            dummy_file.write("\n")
            dummy_file.close()

            original_file = open("CHANGELOG.md", "r")
            data = original_file.read()
            original_file.close()

            dummy_file = open("dummy_CHANGELOG.md", "r")
            data2 = dummy_file.read()
            dummy_file.close()

            data2 += data
            with open("CHANGELOG.md", "w") as final:
                final.write(data2)
            final.close()
            os.remove("dummy_CHANGELOG.md")
            print("Completed writing to CHANGELOG")
        except Exception as e:
            print("Exception occurred while writing to CHANGELOG {0}".format(str(e)))

resource_names = []

class WriteToEndpointsFile(object):
    def __init__(self, product_table_name, executed_files, is_ansible, sdk):
        self.line_nos = {}
        self.res_lines = {}
        self.product_table_name = product_table_name
        self.all_lines = None
        self.executed_files = executed_files
        self.is_ansible = is_ansible
        self.current_version = None
        self.sdk = sdk

    def write_md(self):
        file = open('endpoints-support.md', 'w')
        file.writelines(self.all_lines)
        file.close()

    def load_md(self):
        file = open('endpoints-support.md')
        self.all_lines = file.readlines()

    def add_column(self, product_table_name):

        count = 0
        self.load_md()
        for line in self.all_lines:
            count += 1
            if product_table_name in line:
                break

        head_line = self.all_lines[count + 1].split()
        self.current_version = int(head_line[-2].split('V')[-1])
        new_version = 'V' + str(self.current_version + 200)
        if int(api_version) == self.current_version:
            return

        column_added = False
        while count < len(self.all_lines):
            add_col = None
            line = self.all_lines[count].rstrip('\n')

            if "Endpoints" in self.all_lines[count]:
                add_col = line + " " + new_version + '               |\n'

            elif "---------" in self.all_lines[count]:
                add_col = line + ' :-----------------: |\n'
                column_added = True

            if add_col:
                self.all_lines[count] = add_col
                self.write_md()

            if column_added:
                break

            count += 1

    def get_rows(self, resource_name):
        count = 0
        resource_name_row_start = 0
        resource_name_row_end = 0
        self.load_md()
        for line in self.all_lines:
            count += 1
            if line.startswith('|     '+resource_name):
                resource_name_row_start = count

                for no in range(count, len(self.all_lines)):
                    if self.all_lines[no].startswith('|     **'):
                        resource_name_row_end = no
                        break

                return resource_name_row_start, resource_name_row_end

    def get_lines(self, st_no, end_no):
            lines = list()
            self.load_md()
            for no in range(st_no, end_no):
                lines.append(dict({'line_no': no, 'line': self.all_lines[no]}))
            return lines

    def get_old_end_points(self, st_no, end_no, webscraping_data):
        lines = self.get_lines(st_no, end_no)

        end_points_list = []
        old_end_points = []
        for ele in lines:
            line = ele.get('line')
            if line.startswith('|<sub>'):
                ln = line.split('|')
                split_module = ln[1].strip().split('<sub>')
                module = split_module[-1].split('</sub>')[0]
                end_points_list.append({module, ''.join((ln[2].split()))})

        for end_point in end_points_list:
            data_found = False
            for data in webscraping_data:
                if data == end_point:
                    data_found = True
                    break
            if not data_found:
                old_end_points.append(end_point)
        return old_end_points

    def validate_webscrapping_data(self, lines, end_point, str):
        self.current_version = int(api_version) - 200
        end_point_found = False
        for ele in lines:
            line_no = ele.get('line_no')
            line = ele.get('line')
            if line.startswith('|<sub>'):
                ln = line.split('|')
                ln_length = len(ln)
                desired_length = int(((((self.current_version+200)-800)/200)+3))
                split_module = ln[1].strip().split('<sub>')
                module = split_module[-1].split('</sub>')[0]
                if end_point == {module, ln[2].strip()}:
                    ln = line.rstrip('\n')
                    if (ln_length == desired_length):
                        add_col = ln + str
                        self.all_lines[line_no] = add_col
                    else:
                        pass
                    end_point_found = True
                    break
        if not end_point_found:
            return end_point
        return

    def add_checks(self, st_no, end_no, webscraping_data):
        lines = self.get_lines(st_no, end_no)

        old_end_points = self.get_old_end_points(st_no, end_no, webscraping_data)
        for old_end_point in old_end_points:
            self.validate_webscrapping_data(lines, old_end_point, '  :heavy_minus_sign:   |\n')

        new_end_points = []
        for end_point in webscraping_data:
            new_end_point = self.validate_webscrapping_data(lines, end_point, '  :white_check_mark:   |\n')
            if new_end_point:
                new_end_points.append(new_end_point)
        # below code is to add new endpoints into endpoints-support.md file and its commented, parked aside 
        # for end_point in new_end_points:
        #     if (len(list(end_point)[1]) > 5):
        #         add_col = '|<sub>'+list(end_point)[1]+'</sub>                                                      |'+' '+list(end_point)[0]+'      '+ '|  :heavy_minus_sign:   '*int(((((self.current_version+200)-800)/200)-1))+'|  :white_check_mark:   |\n'
        #     else:
        #         add_col = '|<sub>'+list(end_point)[0]+'</sub>                                                      |'+' '+list(end_point)[1]+'      '+ '|  :heavy_minus_sign:   '*int(((((self.current_version+200)-800)/200)-1))+'|  :white_check_mark:   |\n'            
        #     line_no = lines[-1].get('line_no')
        #     self.all_lines[line_no] = self.all_lines[line_no]+add_col
        #     self.write_md()
        #     self.load_md()
        #     lines.append(dict({'line_no':line_no+1, 'line':self.all_lines[line_no+1]}))

    def main(self):
        i = 0
        if self.is_ansible == True:
            exe = modifyExecutedFiles(self.executed_files)
            self.executed_files = exe
        else:
            pass
        print("------Initiating write to endpoints file--------")
        for ele in self.executed_files:
            resource = list(rel_dict.keys())[list(rel_dict.values()).index(ele)]
            formatted_resource_name = '**' + resource + '**'
            resource_names.append(formatted_resource_name)
        self.add_column(self.product_table_name)
        for resource_name in resource_names:
            webscraping_data = DataFromWebScraping(self.executed_files[i])
            data_returned_from_web_scraping = webscraping_data.data_scraped()
            st_no, end_no = self.get_rows(resource_name)
            self.add_checks(st_no, end_no, data_returned_from_web_scraping)
            i = i + 1
            self.write_md()
        print("-------Completed write to endpoints file--------")

def removeLogFiles(val):
    if val == True:
        print("Please check the working directory to check log files")
    else:
        print("---------Removing all log files---------------")
        cwd = os.getcwd()
        for rootDir, subdirs, filenames in os.walk(cwd):
            for filename in fnmatch.filter(filenames, 'logfile*.log'):
                try:
                    os.remove(os.path.join(rootDir, filename))
                except OSError:
                    print("Error while deleting file")
                    print("---------Completed removing log files--------------")


if __name__ == '__main__':
    selected_sdk = input("Please enter SDK you want to validate(python, ansible, ruby, go): ")
    executed_files, is_ansible, sdk = ExecuteFiles(selected_sdk)
    resources_from_textfile = LoadResourcesFromFile()
    val4 = input('Please provide value as true to reside log files, else provide false: ')
    if val4 == False:
        removeLogFiles(val4)
    else:
        pass
    val1 = input("Do you want to write data to CHANGELOG.md: ")
    if val1 in ['y', 'yes', '']:
        if len(executed_files) != len(resources_from_textfile):
            val3 = input("There are few failed resources, even then do you want to write data to CHANGELOG.md: ")
            if val3 in ['y','yes', '']:
                write_obj = WriteToChangeLog(executed_files, sdk)
                write_obj.write_data()
            else:
                print("Please check failed_resources list and procees with writing to CHANGELOG with successfully executed files")
        else:
            print("Started writing to CHANGELOG.md")
            write_obj = WriteToChangeLog(executed_files, sdk)
            write_obj.write_data()
            print("Completed writing to CHANGELOG.md")
    else:
        print("Please proceed with writing to endpoints file")
    val2 = input("Do you want to edit endpoints-support.md: ")
    if val2 in ['y', 'yes', '']:
        read_md_obj = WriteToEndpointsFile('## HPE OneView', executed_files, is_ansible, sdk)
        read_md_obj.main()
    else:
         print("Please proceed with editing endpoints file")
