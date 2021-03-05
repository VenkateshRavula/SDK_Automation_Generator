import os
import re

api_version = 2200
i3s_api_versions = [1000, 1020, 1600, 2000]

# Resources dictionary
ruby_resource_dict = {'Connection Template': 'connection_template',
                      'Enclosure': 'enclosure',
                      'Enclosure Group': 'enclosure_group',
                      'Ethernet Network': 'ethernet_network',
                      'FC Network': 'fc_network',
                      'FCOE Network': 'fcoe_network',
                      'Firmware Driver': 'firmware_driver',
                      'Hypervisor Cluster Profile': 'hypervisor_cluster_profile',
                      'Hypervisor Manager': 'hypervisor_manager',
                      'Interconnect': 'interconnect',
                      'Interconnect Type': 'interconnect_type',
                      'LIG Uplink Set': 'lig_uplink_set',
                      'Logical Enclosure': 'logical_enclosure',
                      'Logical Interconnect': 'logical_interconnect',
                      'Logical Interconnect Group': 'logical_interconnect_group',
                      'Network Set': 'network_set',
                      'OS Deployment Plan': 'os_deployment_plan',
                      'Scope': 'scope',
                      'Server Certificate': 'server_certificate',
                      'Server Hardware': 'server_hardware',
                      'Server Hardware Type': 'server_hardware_type',
                      'Server Profile': 'server_profile',
                      'Server Profile Template': 'server_profile_template',
                      'Storage Pool': 'storage_pool',
                      'Storage System': 'storage_system',
                      'Uplink Set': 'uplink_set',
                      'Volume': 'volume',
                      'Volume Attachment': 'volume_attachment',
                      'Volume Template': 'volume_template'
                      }

ruby_i3s_resource_dict = {
    'Artifact Bundle': 'artifact_bundle',
    'Golden Image': 'golden_image',
    'Plan Script': 'plan_script',
    'Build Plan': 'build_plan',
    'Deployment Plan': 'deployment_plan',
    'Deployment Group': 'deployment_group',
    'OS Volume': 'os_volume'
}

cwd = os.getcwd()  # gets the path of current working directory(should be SDK repo path)
lib_path_list = ['lib', 'oneview-sdk', 'resource']
lib_path = str(cwd) + os.path.sep + os.path.sep.join(lib_path_list)
spec_path_list = ['spec', 'unit', 'resource']
spec_path = str(cwd) + os.path.sep + os.path.sep.join(spec_path_list)
i3s_lib_path_list = ['lib', 'oneview-sdk', 'image-streamer', 'resource']
i3s_lib_path = str(cwd) + os.path.sep + os.path.sep.join(i3s_lib_path_list)
i3s_spec_path_list = ['spec', 'unit', 'image-streamer', 'resource']
i3s_spec_path = str(cwd) + os.path.sep + os.path.sep.join(i3s_spec_path_list)


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
    resource_file_name = ruby_resource_dict[resource_name] + file_extension
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


def generate_i3s_library_files(current_api_version, filepath, file_type, resource_name):
    """
    This method will generate the library/spec files for i3s for each api version for ruby SDK.
    :param
    current_api_version - i3s api version (2000 for OV 5.40)
    filepath - location of library/spec files
    file_type - Can be library (or) spec
    resource_name - i3s resource name
    """
    prev_api_version = i3s_api_versions[-2]
    pre_prev_api_version = i3s_api_versions[-3]
    prev_api_version_directory = 'api' + str(prev_api_version)
    current_api_version_directory = 'api' + str(current_api_version)
    file_extension = '.rb' if file_type == 'library' else '_spec.rb'

    prev_api_version_file = str(prev_api_version_directory) + file_extension
    current_api_version_file = str(current_api_version_directory) + file_extension

    # Create api.rb/api_spec.rb file and api folder structure for different variants
    create_i3s_api_version_file(pre_prev_api_version, prev_api_version, current_api_version, filepath, filepath,
                                prev_api_version_file, current_api_version_file)
    create_i3s_folder_structure(filepath, prev_api_version_directory, current_api_version_directory)

    old_api_path = filepath + os.path.sep + str(prev_api_version_directory)
    new_api_path = filepath + os.path.sep + str(current_api_version_directory)

    # Create library/spec files for a resource
    resource_file_name = ruby_i3s_resource_dict[resource_name] + file_extension
    create_i3s_api_version_file(pre_prev_api_version, prev_api_version, current_api_version, old_api_path, new_api_path,
                                resource_file_name, resource_file_name)
    file_rewrite(new_api_path, resource_file_name, file_type)


def ruby_library_extra_config_files(current_api_version, path):
    """
    Extra changes in ruby library files for each release are done by this method
    Files covered - lib/oneview-sdk.rb & .rubocop.yml
    """
    os.chdir(path)
    sdk_rb_file = os.path.sep.join([path, 'lib', 'oneview-sdk.rb'])
    prev_api_version = int(current_api_version) - 200
    new_version_string = str(prev_api_version) + ', ' + str(current_api_version)
    f_read = open(sdk_rb_file).read()
    if str(current_api_version) not in f_read and str(prev_api_version) in f_read:
        f_read = f_read.replace(str(prev_api_version), str(new_version_string))
        f_out = open(sdk_rb_file, 'w')  # open the file with the WRITE option
        print("Updating '{}' file with '{}' api version".format(sdk_rb_file, current_api_version))
        f_out.write(f_read)  # write the the changes to the file
        f_out.close()

    rubocop_file = '.rubocop.yml'
    client_var = '$client_' + str(current_api_version)
    old_client_variable = '$client_' + str(prev_api_version) + '_synergy'
    new_client_variable = old_client_variable + ', ' + client_var + ', ' + client_var + '_synergy'
    fr = open(rubocop_file).read()
    if client_var not in fr and old_client_variable in fr:
        fr = fr.replace(old_client_variable, new_client_variable)
        fo = open(rubocop_file, 'w')  # open the file with the WRITE option
        print("Updating '{}' file with '{}'".format(rubocop_file, new_client_variable))
        fo.write(fr)  # write the the changes to the file
        fo.close()


def ruby_i3s_library_extra_config_files(current_api_version, path):
    """
    Extra changes in ruby i3s library files for each release are done by this method
    Files covered - lib/oneview-sdk/image_streamer.rb
    """
    os.chdir(path)
    sdk_rb_file = os.path.sep.join([path, 'lib', 'oneview-sdk', 'image_streamer.rb'])
    prev_api_version = i3s_api_versions[-2]
    new_version_string = str(prev_api_version) + ', ' + str(current_api_version)
    f_read = open(sdk_rb_file).read()
    if str(current_api_version) not in f_read and str(prev_api_version) in f_read:
        f_read = f_read.replace(str(prev_api_version), str(new_version_string))
        f_out = open(sdk_rb_file, 'w')  # open the file with the WRITE option
        print("Updating '{}' file with '{}' api version".format(sdk_rb_file, current_api_version))
        f_out.write(f_read)  # write the the changes to the file
        f_out.close()


def ruby_spec_extra_config_files(current_api_version, path):
    """
    Extra changes in ruby spec files for each release are done by this method
    Files covered - spec/unit/oneview_sdk_spec.rb, spec/unit/resource_spec.rb, spec/unit/client_spec.rb,
    spec/cli/version_spec.rb and spec/spec_helper.rb
    """
    spec_unit_path = os.path.sep.join([path, 'spec', 'unit'])
    spec_cli_path = spec_unit_path + os.path.sep + 'cli'
    spec_helper_path = path + os.path.sep + 'spec'

    prev_api_version = int(current_api_version) - 200
    next_api_version = int(current_api_version) + 200
    os.chdir(spec_unit_path)
    sdk_spec_file = 'oneview_sdk_spec.rb'

    # Replace api versions for 'oneview_sdk_spec.rb'
    search_string1 = ', ' + str(prev_api_version)
    replace_string1 = search_string1 + ', ' + str(current_api_version)
    search_string2 = 'API' + str(prev_api_version)
    replace_string2 = search_string2 + ' ' + 'API' + str(current_api_version)
    f_read = open(sdk_spec_file).read()
    if str(current_api_version) not in f_read and str(prev_api_version) in f_read:
        f_read = f_read.replace(str(search_string1), str(replace_string1))
        f_read = f_read.replace(str(search_string2), str(replace_string2))
        f_out = open(sdk_spec_file, 'w')  # open the file with the WRITE option
        print("Updating '{}' file with '{}' api version".format(sdk_spec_file, current_api_version))
        f_out.write(f_read)  # write the the changes to the file
        f_out.close()

    # Replaces current api version to next api version as part of negative case
    replace_api_version_file(current_api_version, next_api_version, spec_unit_path, 'resource_spec.rb')
    replace_api_version_file(current_api_version, next_api_version, spec_unit_path, 'client_spec.rb')

    # client_spec.rb has both current and previous api versions, so perform one more replace operation
    replace_api_version_file(prev_api_version, current_api_version, spec_unit_path, 'client_spec.rb')

    # Replaces previous api version to current api version
    replace_api_version_file(prev_api_version, current_api_version, spec_cli_path, 'version_spec.rb')
    replace_api_version_file(prev_api_version, current_api_version, spec_helper_path, 'spec_helper.rb')

    # Replaces previous api version to current api version in files which have mixed api versions
    search_str1 = "The API999 method or resource does not exist for OneView API version {}".format(prev_api_version)
    string_search_and_replace(search_str1, prev_api_version, current_api_version, spec_unit_path, sdk_spec_file)

    os.chdir(spec_helper_path)
    spec_context_file = 'shared_context.rb'
    search_string1 = "# Context for API{0} integration testing:\nRSpec.shared_context 'integration api{0} context', " \
                     "a: :b do\n  before :all do\n    integration_context\n    $client_{0} ||= OneviewSDK::Client.new" \
                     "($config.merge(api_version: {0}))\n    $client_{0}_synergy ||= OneviewSDK::Client.new" \
                     "($config_synergy.merge(api_version: {0}))\n  end\nend\n".format(prev_api_version)

    search_string2 = "RSpec.shared_context 'system api{0} context', a: :b do\n  before(:each) do\n    " \
                     "load_system_properties\n    generate_clients({0})\n  end\nend\n".format(prev_api_version)

    search_string3 = "  when {0}\n    $client_{0} ||= OneviewSDK::Client.new($config.merge(api_version: api_version))\n" \
                     "    $client_{0}_synergy ||= OneviewSDK::Client.new($config_synergy.merge" \
                     "(api_version: api_version))\n".format(prev_api_version)

    f_read = open(spec_context_file).read()
    f_read = string_merge_and_replace(search_string1, f_read, prev_api_version, current_api_version, "\n")
    f_read = string_merge_and_replace(search_string2, f_read, prev_api_version, current_api_version, "\n")
    f_read = string_merge_and_replace(search_string3, f_read, prev_api_version, current_api_version)

    f_out = open(spec_context_file, 'w')  # open the file with the WRITE option
    f_out.write(f_read)  # write the the changes to the file
    f_out.close()


def ruby_i3s_spec_extra_config_files(current_api_version, path):
    """
    Extra changes in ruby i3s spec files for each release are done by this method
    Files covered - spec/unit/image-streamer/client_spec.rb, spec/spec_helper.rb
    """
    i3s_spec_unit_path = os.path.sep.join([path, 'spec', 'unit', 'image-streamer'])
    spec_helper_path = path + os.path.sep + 'spec'

    prev_api_version = i3s_api_versions[-2]
    next_api_version = int(current_api_version) + 200

    search_string1 = "allow_any_instance_of(OneviewSDK::ImageStreamer::Client).to receive"\
                     "(:appliance_i3s_api_version).and_return({})".format(i3s_api_versions[-2])
    string_search_and_replace(search_string1, prev_api_version, current_api_version, spec_helper_path, 'spec_helper.rb')

    # Replaces current api version to next api version as part of negative case
    replace_api_version_file(int(prev_api_version)+200, next_api_version, i3s_spec_unit_path, 'client_spec.rb')


def string_search_and_replace(search_string, prev_api_version, current_api_version, path, filename):
    """
    Searches for a search string in file, if not found then replaces search string with replace string
    """
    os.chdir(path) # switches the python environment to resource directory
    f_read = open(filename).read()
    replace_string = search_string.replace(str(prev_api_version), str(current_api_version))
    if replace_string not in f_read and search_string in f_read:
        f_read = f_read.replace(str(search_string), str(replace_string))
        f_out = open(filename, 'w')  # open the file with the WRITE option
        print("Replaced api version '{}' to '{}' in file - '{}'".format(prev_api_version, current_api_version, filename))
        f_out.write(f_read)  # write the the changes to the file
        f_out.close()


def string_merge_and_replace(search_string, main_string, prev_api_version, current_api_version, append_string=""):
    """
    Searches for a string in main string, if not found merge it with search string and appends to main string
    """
    search_string_new = search_string.replace(str(prev_api_version), str(current_api_version))
    replace_string = search_string + append_string + search_string_new
    if search_string_new not in main_string and search_string in main_string:
        main_string = main_string.replace(str(search_string), str(replace_string))
        print("Appending shared context for '{}' api version".format(current_api_version))
    return main_string


def create_folder_structure(path, old_directory, new_directory):
    """
    Creates folder structures for each api version
    """
    os.chdir(path) # switches the python environment to resource directory
    if not os.path.exists(new_directory):
        print("Created new directory - '{}' in path - '{}'".format(new_directory, path))
        os.mkdir(new_directory)
        os.chdir(new_directory)
    else:
        os.chdir(new_directory)
    if not os.path.exists('c7000'):
        print("Created new directory - '{}' in path - '{}'".format('c7000', new_directory))
        os.mkdir('c7000')
    if not os.path.exists('synergy'):
        print("Created new directory - '{}' in path - '{}'".format('synergy', new_directory))
        os.mkdir('synergy')


def create_i3s_folder_structure(path, old_directory, new_directory):
    """
    Creates folder structures for each i3s api version
    """
    os.chdir(path) # switches the python environment to resource directory
    if not os.path.exists(new_directory):
        print("Created new directory - '{}' in path - '{}'".format(new_directory, path))
        os.mkdir(new_directory)
        os.chdir(new_directory)
    else:
        os.chdir(new_directory)


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


def create_i3s_api_version_file(pre_prev_api_version, prev_api_version, current_api_version, old_path, new_path, old_file, new_file):
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
        f_read = f_read.replace(str(pre_prev_api_version), str(prev_api_version)) # this changes inherit path

        f_out = open(new_file, 'w')  # open the file with the WRITE option
        print("Created file - '{}' in path - '{}'".format(new_file, new_path))
        f_out.write(f_read)  # write the the changes to the file
        f_out.close()


def replace_api_version_file(prev_api_version, current_api_version, path, filename):
    """
    Replaces old api version with current api_version in the file if not updated already (Ruby)
    """
    os.chdir(path) # switches the python environment to resource directory
    f_read = open(filename).read()
    if str(current_api_version) not in f_read and str(prev_api_version) in f_read:
        f_read = f_read.replace(str(prev_api_version), str(current_api_version))
        f_out = open(filename, 'w')  # open the file with the WRITE option
        print("Replaced api version '{}' to '{}' in file - '{}'".format(prev_api_version, current_api_version, filename))
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
    generate_library_files(api_version, lib_path, 'library', 'Logical Interconnect')
    generate_library_files(api_version, spec_path, 'spec', 'Logical Interconnect')
    ruby_library_extra_config_files(api_version, cwd)
    ruby_spec_extra_config_files(api_version, cwd)
    generate_i3s_library_files(i3s_api_versions[-1], i3s_lib_path, 'library', 'Plan Script')
    generate_i3s_library_files(i3s_api_versions[-1], i3s_spec_path, 'spec', 'Plan Script')
    ruby_i3s_library_extra_config_files(i3s_api_versions[-1], cwd)
    ruby_i3s_spec_extra_config_files(i3s_api_versions[-1], cwd)