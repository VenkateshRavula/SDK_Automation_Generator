import os, re, shutil, git

api_version = 2200
# Resources dictionary
chef_resource_dict = {'Connection Template': 'connection_template_provider',
                      'Enclosure': 'enclosure_provider',
                      'Enclosure Group': 'enclosure_group_provider',
                      'Ethernet Network': 'ethernet_network_provider',
                      'FC Network': 'fc_network_provider',
                      'FCOE Network': 'fcoe_network_provider',
                      'Hypervisor Cluster Profile': 'hypervisor_cluster_profile_provider',
                      'Hypervisor Manager': 'hypervisor_manager_provider',
                      'Interconnect': 'interconnect_provider',
                      'Logical Enclosure': 'logical_enclosure_provider',
                      'Logical Interconnect': 'logical_interconnect_provider',
                      'Logical Interconnect Group': 'logical_interconnect_group_provider',
                      'Network Set': 'network_set_provider',
                      'Scope': 'scope_provider',
                      'Server Certificate': 'server_certificate_provider',
                      'Server Hardware': 'server_hardware_provider',
                      'Server Hardware Type': 'server_hardware_type_provider',
                      'Server Profile': 'server_profile_provider',
                      'Server Profile Template': 'server_profile_template_provider',
                      'Storage Pool': 'storage_pool_provider',
                      'Storage System': 'storage_system_provider',
                      'Uplink Set': 'uplink_set_provider',
                      'Volume': 'volume_provider',
                      'Volume Attachment': 'volume_attachment_provider',
                      'Volume Template': 'volume_template_provider'
                      }

path = os.getcwd()
clone_dir = 'chef'
# Deleting the clone directory if exists
if os.path.exists(clone_dir):
    shutil.rmtree(clone_dir, ignore_errors=True)

repo = git.Repo.clone_from('https://github.com/HewlettPackard/oneview-chef',
                           path + os.path.sep + clone_dir)
os.chdir(path + os.path.sep + clone_dir)
cwd = os.getcwd()  # gets the path of current working directory(should be SDK repo path)
lib_path_list = ['libraries', 'resource_providers']
lib_path = str(cwd) + os.path.sep + os.path.sep.join(lib_path_list)
spec_path = str(cwd) + os.path.sep + 'spec'

branchName = 'feature'
remote_branches = []
for ref in repo.git.branch('-r').split('\n'):
    remote_branches.append(ref.replace(" ", ""))

branch_present = True if 'origin/' + branchName in remote_branches else False


def checkIfBranchPresent(branchName, remote_branches):
    num = 0
    while True:
        branchName = branchName + '_' + str(num)
        num = num + 1
        branch_present = True if 'origin/' + branchName in remote_branches else False
        if branch_present is False:
            break
    return branchName


if branch_present is True:
    branchName = checkIfBranchPresent(branchName, remote_branches)
else:
    pass

new_branch = repo.create_head(branchName)
new_branch.checkout()


def generate_library_files(current_api_version, filepath, file_type, resource_name):
    """
    This method will generate the library/spec files for each api version for ruby SDK.
    :param
    current_api_version - oneview api version (2200 for OV 5.50)
    filepath - location of library/spec files
    file_type - Can be library (or) spec
    resource_name - Oneview resource name
    """
    prev_api_version = int(current_api_version) - 200
    prev_api_version_directory = 'api' + str(prev_api_version)
    current_api_version_directory = 'api' + str(current_api_version)
    file_extension = '.rb' if file_type == 'library' else '_spec.rb'

    prev_api_version_file = str(prev_api_version_directory) + file_extension
    current_api_version_file = str(current_api_version_directory) + file_extension
    c7000_variant_file = 'c7000' + file_extension
    synergy_variant_file = 'synergy' + file_extension

    # Create api.rb/api_spec.rb file and api folder structure for different variants
    create_api_version_file(prev_api_version, current_api_version, filepath, filepath,
                            prev_api_version_file, current_api_version_file)
    create_folder_structure(filepath, prev_api_version_directory, current_api_version_directory)

    # Create variant.rb/variant_spec.rb file(c7000 and synergy)
    old_api_path = filepath + os.path.sep + str(prev_api_version_directory)
    new_api_path = filepath + os.path.sep + str(current_api_version_directory)
    create_api_version_file(prev_api_version, current_api_version, old_api_path, new_api_path, c7000_variant_file, c7000_variant_file)
    create_api_version_file(prev_api_version, current_api_version, old_api_path, new_api_path, synergy_variant_file, synergy_variant_file)

    # Create library/spec files for a resource
    resource_file_name = chef_resource_dict[resource_name] + file_extension
    c7000_old_path = old_api_path + os.path.sep + 'c7000'
    c7000_new_path = new_api_path + os.path.sep + 'c7000'
    create_api_version_file(prev_api_version, current_api_version, c7000_old_path, c7000_new_path,
                            resource_file_name, resource_file_name)
    file_rewrite(c7000_new_path, resource_file_name, file_type)

    synergy_old_path = old_api_path + os.path.sep + 'synergy'
    synergy_new_path = new_api_path + os.path.sep + 'synergy'
    create_api_version_file(prev_api_version, current_api_version, synergy_old_path, synergy_new_path,
                            resource_file_name, resource_file_name)
    file_rewrite(synergy_new_path, resource_file_name, file_type)


def create_folder_structure(path, old_directory, new_directory):
    """
    Creates folder structures for each api version
    """
    os.chdir(path) # switches the python environment to resource directory
    if not os.path.exists(new_directory):
        print("Created new directory - '{}' in path - '{}'".format(new_directory, path))
        os.mkdir(new_directory)
    os.chdir(new_directory)
    if not os.path.exists('c7000'):
        print("Created new directory - '{}' in path - '{}'".format('c7000', new_directory))
        os.mkdir('c7000')
    if not os.path.exists('synergy'):
        print("Created new directory - '{}' in path - '{}'".format('synergy', new_directory))
        os.mkdir('synergy')


def create_api_version_file(prev_api_version, current_api_version, old_path, new_path, old_file, new_file):
    """
    Creates an api_version file for each release if not present (Ruby)
    """
    os.chdir(old_path) # switches the python environment to resource directory
    if os.path.exists(old_file):
        f_read = open(old_file).read()
    else:
        raise Exception("No such file named {}".format(old_file))

    os.chdir(new_path)
    if not os.path.exists(new_file):
        f_read = f_read.replace(str(prev_api_version), str(current_api_version))
        pre_prev_api_version = int(prev_api_version) - 200
        f_read = f_read.replace(str(pre_prev_api_version), str(prev_api_version)) # this changes inherit path

        f_out = open(new_file, 'w')  # open the file with the WRITE option
        print("Created file - '{}' in path - '{}'".format(new_file, new_path))
        f_out.write(f_read)  # write the the changes to the file
        f_out.close()


def modify_spec_helper(current_api_version, path):
    """
    Adds the spec context for latest api version in 'spec_helper.rb' file
    """
    prev_api_version = int(current_api_version) - 200
    next_api_version = int(current_api_version) + 200
    os.chdir(path)
    spec_helper_file = 'spec_helper.rb'
    search_string1 = "allow_any_instance_of(OneviewSDK::Client).to receive(:appliance_api_version).and_return({})".format(current_api_version)
    replace_string1 = search_string1.replace(str(current_api_version), str(next_api_version))
    search_string2 = "  let(:client{0}) do\n    OneviewSDK::Client.new(url: 'https://oneview.example.com', user: 'Administrator', password: 'secret123', api_version: {0})\n  end\n".format(prev_api_version)
    search_string3 = search_string2.replace(str(prev_api_version), str(current_api_version))
    replace_string2 = search_string2 + "\n" + search_string3
    f_read = open(spec_helper_file).read()
    if search_string1 in f_read and replace_string1 not in f_read:
        f_read = f_read.replace(str(search_string1), str(replace_string1))
        print("Updating '{}' file with '{}' api version".format(spec_helper_file, current_api_version))
    if search_string3 not in f_read and search_string2 in f_read:
        f_read = f_read.replace(str(search_string2), str(replace_string2))
        print("Updating '{}' file with spec context for '{}' api version".format(spec_helper_file, current_api_version))

    f_out = open(spec_helper_file, 'w')  # open the file with the WRITE option
    f_out.write(f_read)  # write the the changes to the file
    f_out.close()


def file_rewrite(file_path, filename, file_type):
    """
    Re-writes the file contents by removing extra code. Writes only basic inherit part.
    """
    if file_type == 'library':
        search_string = '^' + '\s+' + 'class'
        end_lines = 4
    else:
        search_string = '^' + '\s+' + 'end'
        end_lines = 1

    os.chdir(file_path)
    file_lines = open(filename).readlines()
    fw = open(filename, 'w')
    for line in file_lines:
        if re.match(search_string, line.strip("\n")):
            fw.write(line)
            break
        else:
            fw.write(line)
    fw.writelines(file_lines[-end_lines:])
    fw.close()


if __name__ == '__main__':
    for resource in chef_resource_dict:
        generate_library_files(api_version, lib_path, 'library', resource)
        modify_spec_helper(api_version, spec_path)

    repo.git.add(A=True)
    repo.git.commit('-m', 'PR for config changes #pr',
                    author='chebroluharika@gmail.com') # to commit changes
    repo.git.push('--set-upstream', 'origin', branchName)
    repo.close()
    os.chdir(path) # Navigate to parent directory
    # Delete ruby directory as cleanup
    if os.path.exists(clone_dir):
        shutil.rmtree(clone_dir, ignore_errors=True)