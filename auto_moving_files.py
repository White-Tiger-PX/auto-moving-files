import os
import shutil

import config

from set_logger import set_logger
from utils_json import save_json, load_json


def save_directory(directories_data, directory_path):
    for sub_directory_path in directories_data[directory_path]['sub_directories'].keys():
        save_directory(directories_data=directories_data, directory_path=sub_directory_path)

    directories_data[directory_path]['files']           = {}
    directories_data[directory_path]['sub_directories'] = {}


def checking_the_condition_for_action(path_settings, file_name_exceptions, directory_name_exceptions, directories_data):
    time_limit_for_modified_time = config.program_start_time - path_settings['time_limit_for_modified_time']
    time_limit_for_first_seen    = config.program_start_time - path_settings['time_limit_for_first_seen']
    action_by_last_modified      = path_settings['action_by_last_modified']
    action_by_first_seen         = path_settings['action_by_first_seen']

    for directory_path, directory_info in directories_data.items():
        directory_has_exception = any(
            directory_name_exception in directory_info['name']
            for directory_name_exception in directory_name_exceptions
        )

        if directory_has_exception:
            save_directory(directories_data=directories_data, directory_path=directory_path)

            continue

        for file_path, file_info in directory_info['files'].items():
            directory_info['files'][file_path]['it_is_forbidden_to_move'] = True # True по умолчанию

            file_has_exception = any(
                file_name_exception in file_info['name']
                for file_name_exception in file_name_exceptions
            )

            if file_has_exception:
                continue

            first_seen_condition    = file_info['file_first_seen_time'] < time_limit_for_first_seen
            modified_time_condition = file_info['file_modified_time']   < time_limit_for_modified_time

            if action_by_last_modified and action_by_first_seen:
                if modified_time_condition and first_seen_condition:
                    directory_info['files'][file_path]['it_is_forbidden_to_move'] = False
            elif action_by_last_modified and modified_time_condition:
                directory_info['files'][file_path]['it_is_forbidden_to_move'] = False
            elif action_by_first_seen and first_seen_condition:
                directory_info['files'][file_path]['it_is_forbidden_to_move'] = False


def sorting_with_date(setup, directory_path):
    string_datetime =config.string_program_start_time

    if setup['group_by_years']:
        name = string_datetime.strftime('%Y')
        directory_path = os.path.join(directory_path, name)

        if setup['group_by_months']:
            name = string_datetime.strftime('%m')
            directory_path = os.path.join(directory_path, name)

            if setup['group_by_days']:
                name = string_datetime.strftime('%d')
                directory_path = os.path.join(directory_path, name)
        elif setup['group_by_days']:
            name = string_datetime.strftime('%m-%d')
            directory_path = os.path.join(directory_path, name)
    else:
        if setup['group_by_months']:
            name = string_datetime.strftime('%Y-%m')
            directory_path = os.path.join(directory_path, name)

            if setup['group_by_days']:
                name = string_datetime.strftime('%d')
                directory_path = os.path.join(directory_path, name)
        elif setup['group_by_days']:
            name = string_datetime.strftime('%Y-%m-%d')
            directory_path = os.path.join(directory_path, name)

    return directory_path


def copy_files(path_settings, directories_data):
    save_folders = path_settings['save_folders']
    sorting_options = path_settings['date_grouping_options']
    sort_by_date = any(sorting_options[key] for key in ['group_by_days', 'group_by_months', 'group_by_years'])

    for directory_path, directory_info in directories_data.items():
        relative_path = os.path.relpath(directory_path, path_settings['input'])

        for file_path, file_info in directory_info['files'].items():
            if file_info['it_is_forbidden_to_move']:
                continue

            if save_folders:
                if sort_by_date:
                    if sorting_options['create_date_folders_in_root']:
                        destination_directory_path = sorting_with_date(setup=sorting_options, directory_path=path_settings['output'])
                        destination_directory_path = os.path.join(destination_directory_path, relative_path)
                    else:
                        destination_directory_path = os.path.join(path_settings['output'], relative_path)
                        destination_directory_path = sorting_with_date(setup=sorting_options, directory_path=destination_directory_path)
                else:
                    destination_directory_path = os.path.join(path_settings['output'], relative_path)
            else:
                destination_directory_path = path_settings['output']

                if sort_by_date:
                    destination_directory_path = sorting_with_date(setup=sorting_options, directory_path=destination_directory_path)

            destination_path = os.path.join(destination_directory_path, os.path.basename(file_path))

            if file_path == destination_path:
                logger.warning('Изначальный и конечный путь файла совпадает.')

                continue

            # Проверяем, что не существует файла без расширения с названием совпадающим с конечной папкой
            if os.path.isfile(destination_directory_path):
                logger.error("Невозможно создать директорию %s, так как файл с таким же именем уже существует.", destination_directory_path)

                continue

            if os.path.exists(destination_path): # Файл уже существует в папке output
                if not path_settings['overwrite_files']: # Настройки не позволяют перезаписывать существующий файл
                    continue

                file1_stat = os.stat(file_path)
                file2_stat = os.stat(destination_path)

                if file1_stat.st_size == file2_stat.st_size: # Файлы идентичны
                    continue

            try:
                os.makedirs(destination_directory_path, exist_ok=True)

                shutil.copy2(file_path, destination_path)
                logger.info("Файл '%s' скопирован в папку '%s'.", file_path, destination_directory_path)
            except Exception as err:
                logger.error("Ошибка при копировании файла '%s' в '%s': %s", file_path, destination_directory_path, err)


def moving_files(path_settings, directories_data):
    sorting_options = path_settings['date_grouping_options']
    sort_by_date = any(sorting_options[key] for key in ['group_by_days', 'group_by_months', 'group_by_years'])

    for directory_path, directory_info in directories_data.items():
        relative_path = os.path.relpath(directory_path, path_settings['input'])

        for file_path, file_info in directory_info['files'].items():
            if file_info['it_is_forbidden_to_move']:
                continue

            if path_settings['save_folders']:
                if sort_by_date:
                    if sorting_options['create_date_folders_in_root']:
                        destination_directory_path = sorting_with_date(setup=sorting_options, directory_path=path_settings['output'])
                        destination_directory_path = os.path.join(destination_directory_path, relative_path)
                    else:
                        destination_directory_path = os.path.join(path_settings['output'], relative_path)
                        destination_directory_path = sorting_with_date(setup=sorting_options, directory_path=destination_directory_path)
                else:
                    destination_directory_path = os.path.join(path_settings['output'], relative_path)
            else:
                destination_directory_path = path_settings['output']

                if sort_by_date:
                    destination_directory_path = sorting_with_date(setup=sorting_options, directory_path=destination_directory_path)

            destination_path = os.path.join(destination_directory_path, os.path.basename(file_path))

            if file_path == destination_path:
                logger.warning('Изначальный и конечный путь файла совпадает.')

                continue

            # Проверяем, что не существует файла без расширения с названием совпадающим с конечной папкой
            if os.path.isfile(destination_directory_path):
                logger.error("Невозможно создать директорию %s, так как файл с таким же именем уже существует.", destination_directory_path)

                continue

            if os.path.exists(destination_path):         # Файл уже существует в папке output
                if not path_settings['overwrite_files']: # Настройки не позволяют перезаписывать существующий файл
                    continue

                file1_stat = os.stat(file_path)
                file2_stat = os.stat(destination_path)

                if file1_stat.st_size == file2_stat.st_size: # Файлы идентичны
                    continue

            try:
                os.makedirs(destination_directory_path, exist_ok=True)

                shutil.move(file_path, destination_path)
                logger.info("Файл '%s' перемещён в папку '%s'.", file_path, destination_directory_path)
            except Exception as error:
                logger.error("Ошибка при перемещении файла '%s' в '%s': %s", file_path, destination_directory_path, error)


def update_files_info(directory_path, file_names, archive_directory_data, directory_data):
    files_data = {}

    for file_name in file_names:
        file_path = os.path.join(directory_path, file_name)

        try:
            archive_file_data = archive_directory_data.get(file_path)
            file_first_seen_time = config.program_start_time

            if archive_file_data:
                file_first_seen_time = archive_file_data['file_first_seen_time']
        except Exception as err:
            file_first_seen_time = config.program_start_time
            logger.error("Ошибка получения архивных данных первого обнаружения файла '%s': %s", file_path, err)

        try:
            file_modified_time = os.path.getmtime(file_path)
        except Exception as err:
            file_modified_time = config.program_start_time
            logger.error("Ошибка получения времени последнего изменения файла '%s': %s", file_path, err)

        files_data[file_path] = {
            "name": file_name,
            "file_modified_time": file_modified_time,
            "file_first_seen_time": file_first_seen_time
        }

    directory_data['files'] = files_data


def directory_walk(root_directory_path, archive_data, directories_data):
    for directory_path, sub_directories, file_names in os.walk(root_directory_path):
        try:
            archive_directory_data = archive_data.pop(directory_path)
            archive_directory_data = archive_directory_data['files']
        except Exception:
            archive_directory_data = {}

        directory_data = {
            'name':            os.path.basename(directory_path),
            'files':           {},
            'sub_directories': {}
        }

        update_files_info(
            directory_path         = directory_path,
            file_names             = file_names,
            archive_directory_data = archive_directory_data,
            directory_data         = directory_data
        )

        for sub_directory_name in sub_directories:
            sub_directory_path = os.path.join(directory_path, sub_directory_name)
            directory_data['sub_directories'][sub_directory_path] = {}

        directories_data[directory_path] = directory_data


def update_dir_info(directory_path, directories_data):
    archive_data = {}

    if not os.path.exists(directory_path):
        return archive_data

    archive_data_file_name = f"{directory_path.replace('\\', '_').replace('/', '_').replace(':', '')}.json"
    archive_data_file_path = os.path.join(config.DIRECTORY_WITH_SCANNED_DIRECTORIES, archive_data_file_name)

    archive_data = load_json(file_path=archive_data_file_path, default_type={}, logger=logger)

    directory_walk(
        root_directory_path = directory_path,
        archive_data        = archive_data,
        directories_data    = directories_data
    )

    save_json(file_path=archive_data_file_path, data=directories_data, logger=logger)


def main():
    for path_settings in config.DIRECTORIES_SETTINGS:
        if not os.path.exists(path_settings['input']):
            continue

        file_list = []

        for root, _, files in os.walk(path_settings['input']):
            for file in files:
                file_path = os.path.join(root, file)
                file_list.append(file_path)

        if file_list:
            os.makedirs(path_settings['output'], exist_ok=True)

        directories_data          = {}
        file_name_exceptions      = path_settings['file_name_exceptions']
        directory_name_exceptions = path_settings['directory_name_exceptions']

        update_dir_info(
            directory_path     = path_settings['input'],
            directories_data   = directories_data
        )

        checking_the_condition_for_action(
            path_settings             = path_settings,
            file_name_exceptions      = file_name_exceptions,
            directory_name_exceptions = directory_name_exceptions,
            directories_data          = directories_data
        )

        if path_settings['copy']:
            copy_files(path_settings=path_settings, directories_data=directories_data)
        else:
            moving_files(path_settings=path_settings, directories_data=directories_data)


if __name__ == "__main__":
    logger   = set_logger(log_folder=config.LOG_FOLDER)

    main()
