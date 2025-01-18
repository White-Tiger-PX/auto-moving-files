import os
import time
import json
import shutil
import logging

from datetime import datetime


def save_directory(directories_data, directory_path):
    for sub_directory_path in directories_data[directory_path]['sub_directories'].keys():
        save_directory(directories_data, sub_directory_path)

    directories_data[directory_path]['action'] = False
    directories_data[directory_path]['files'] = {}
    directories_data[directory_path]['sub_directories'] = {}


def checking_the_condition_for_action(program_start_time, path_settings, file_name_exceptions, directory_name_exceptions, directories_data):
    time_limit_for_modified_time = program_start_time - path_settings['time_limit_for_modified_time']
    time_limit_for_first_seen = program_start_time - path_settings['time_limit_for_first_seen']
    action_by_last_modified = path_settings['action_by_last_modified']
    action_by_first_seen = path_settings['action_by_first_seen']

    for directory_path, directory_info in directories_data.items():
        if any(directory_name_exception in directory_info['name'] for directory_name_exception in directory_name_exceptions):
            save_directory(directories_data, directory_path)
        else:
            new_files_info = {}

            for file_path, file_info in directory_info['files'].items():
                new_files_info[file_path] = True # move_restricted по умолчанию

                is_file_exception = any(file_name_exception in file_info['name'] for file_name_exception in file_name_exceptions)
                is_modified_time_condition = file_info['file_modified_time'] < time_limit_for_modified_time
                is_first_seen_condition = file_info['file_first_seen_time'] < time_limit_for_first_seen

                if is_file_exception:
                    continue

                if action_by_last_modified and action_by_first_seen:
                    if is_modified_time_condition and is_first_seen_condition:
                        new_files_info[file_path] = False
                elif action_by_last_modified and is_modified_time_condition:
                    new_files_info[file_path] = False
                elif action_by_first_seen and is_first_seen_condition:
                    new_files_info[file_path] = False

            directories_data[directory_path]['files'] = new_files_info


def append_time_str(string_datetime, destination_directory_path, period):
    period_formats = {
        'Y': '%Y',
        'm': '%m',
        'd': '%d',
        'md': '%m-%d',
        'Yd': '%Y-%d',
        'Ym': '%Y-%m',
        'Ymd': '%Y-%m-%d'
    }

    name = string_datetime.strftime(period_formats.get(period, ''))

    return os.path.join(destination_directory_path, name)


def sorting_with_date(program_start_time, setup, destination_directory_path):
    string_datetime = datetime.fromtimestamp(program_start_time)

    if setup['group_by_years']:
        destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'Y')

        if setup['group_by_months']:
            destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'm')

            if setup['group_by_days']:
                destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'd')
        elif setup['group_by_days']:
            destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'md')
    else:
        if setup['group_by_months']:
            destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'Ym')

            if setup['group_by_days']:
                destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'd')
        elif setup['group_by_days']:
            destination_directory_path = append_time_str(string_datetime, destination_directory_path, 'Ymd')

    return destination_directory_path


def copy_files(program_start_time, path_settings, directories_data):
    save_folders = path_settings['save_folders']
    sorting_with_date_options = path_settings['date_grouping_options']
    sort_by_date = any(sorting_with_date_options[key] for key in ['group_by_days', 'group_by_months', 'group_by_years'])

    for directory_path, directory_info in directories_data.items():
        relative_path = os.path.relpath(directory_path, path_settings['input'])

        for file_path, move_restricted in directory_info['files'].items():
            if move_restricted:
                continue

            if save_folders:
                if sort_by_date:
                    if sorting_with_date_options['create_date_folders_in_root']:
                        destination_directory_path = sorting_with_date(program_start_time, sorting_with_date_options, path_settings['output'])
                        destination_directory_path = os.path.join(destination_directory_path, relative_path)
                    else:
                        destination_directory_path = os.path.join(path_settings['output'], relative_path)
                        destination_directory_path = sorting_with_date(program_start_time, sorting_with_date_options, destination_directory_path)
                else:
                    destination_directory_path = os.path.join(path_settings['output'], relative_path)
            else:
                destination_directory_path = path_settings['output']

                if sort_by_date:
                    destination_directory_path = sorting_with_date(program_start_time, sorting_with_date_options, destination_directory_path)

            destination_path = os.path.join(destination_directory_path, os.path.basename(file_path))

            if file_path == destination_path: # Изначальная и конечный путь к файлы идентичны
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
                logger.info("Скопирован файл %s", destination_path)
            except Exception as err:
                logger.error("Ошибка при копировании файла %s в %s: %s", file_path, destination_directory_path, err)


def moving_files(program_start_time, path_settings, directories_data):
    save_folders = path_settings['save_folders']
    sorting_with_date_options = path_settings['date_grouping_options']
    sort_by_date = any(sorting_with_date_options[key] for key in ['group_by_days', 'group_by_months', 'group_by_years'])

    for directory_path, directory_info in directories_data.items():
        relative_path = os.path.relpath(directory_path, path_settings['input'])

        for file_path, move_restricted in directory_info['files'].items():
            if move_restricted:
                continue

            if save_folders:
                if sort_by_date:
                    if sorting_with_date_options['create_date_folders_in_root']:
                        destination_directory_path = sorting_with_date(program_start_time, sorting_with_date_options, path_settings['output'])
                        destination_directory_path = os.path.join(destination_directory_path, relative_path)
                    else:
                        destination_directory_path = os.path.join(path_settings['output'], relative_path)
                        destination_directory_path = sorting_with_date(program_start_time, sorting_with_date_options, destination_directory_path)
                else:
                    destination_directory_path = os.path.join(path_settings['output'], relative_path)
            else:
                destination_directory_path = path_settings['output']

                if sort_by_date:
                    destination_directory_path = sorting_with_date(program_start_time, sorting_with_date_options, destination_directory_path)

            destination_path = os.path.join(destination_directory_path, os.path.basename(file_path))

            if file_path == destination_path: # Изначальная и конечный путь к файлы идентичны
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

                shutil.move(file_path, destination_path)
                logger.info("Перемещен файл %s", file_path)
            except Exception as error:
                logger.error("Ошибка при перемещении файла %s в %s: %s", file_path, destination_directory_path, error)


def save_json(file_path, data):
    try:
        file_path = os.path.normpath(file_path)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as err:
        logger.error("Ошибка при сохранении файла %s: %s", file_path, err)


def update_files_info(program_start_time, directory_path, file_names, archive_directory_data, directory_data):
    files_data = {}

    for file_name in file_names:
        file_path = os.path.join(directory_path, file_name)

        try:
            archive_file_data = archive_directory_data.get(file_path, None)

            if archive_file_data:
                file_first_seen_time = archive_file_data['file_first_seen_time']
            else:
                file_first_seen_time = program_start_time
        except Exception as err:
            file_first_seen_time = program_start_time
            logger.error("Ошибка получения архивных данных первого обнаружения файла %s: %s", file_path, err)

        try:
            file_modified_time = os.path.getmtime(file_path)
        except Exception as err:
            file_modified_time = program_start_time
            logger.error("Ошибка получения времени последнего изменения файла %s: %s", file_path, err)

        files_data[file_path] = {
            "name": file_name,
            "file_modified_time": file_modified_time,
            "file_first_seen_time": file_first_seen_time
        }

    directory_data['files'] = files_data


def directory_walk(program_start_time, root_directory_path, archive_data, directories_data):
    for directory_path, sub_directories, file_names in os.walk(root_directory_path):
        try:
            archive_directory_data = archive_data.pop(directory_path)
            archive_directory_data = archive_directory_data['files']
        except Exception:
            archive_directory_data = {}

        directory_data = {
            'name': os.path.basename(directory_path),
            'files': {},
            'sub_directories': {}
        }

        update_files_info(program_start_time, directory_path, file_names, archive_directory_data, directory_data)

        for sub_directory_name in sub_directories:
            sub_directory_path = os.path.join(directory_path, sub_directory_name)
            directory_data['sub_directories'][sub_directory_path] = {}

        directories_data[directory_path] = directory_data


def update_dir_info(program_start_time, directory_with_scanned_directories, directory_path):
    directories_data, archive_data = {}, {}

    if not os.path.exists(directory_path):
        return archive_data

    archive_file_name = directory_path.replace('\\', '_').replace('/', '_').replace(':', '')
    path = f"{directory_with_scanned_directories}/{archive_file_name}.json"

    archive_data = load_json(path, default_type={})

    directory_walk(program_start_time, directory_path, archive_data, directories_data)
    save_json(path, directories_data)

    return directories_data


def main(settings):
    directory_with_scanned_directories = settings['directory_with_scanned_directories']

    for path_settings in settings['directories']:
        path_settings['input'] = os.path.normpath(path_settings['input'])
        path_settings['output'] = os.path.normpath(path_settings['output'])

        if not os.path.exists(path_settings['input']):
            continue

        file_list = []

        for root, _, files in os.walk(path_settings['input']):
            for file in files:
                file_list.append(os.path.join(root, file))

        if file_list:
            os.makedirs(path_settings['output'], exist_ok=True)

        program_start_time = time.time()
        file_name_exceptions = path_settings['file_name_exceptions']
        directory_name_exceptions = path_settings['directory_name_exceptions']

        directories_data = update_dir_info(program_start_time, directory_with_scanned_directories, path_settings['input'])
        checking_the_condition_for_action(program_start_time, path_settings, file_name_exceptions, directory_name_exceptions, directories_data)

        if path_settings['copy']:
            copy_files(program_start_time, path_settings, directories_data)
        else:
            moving_files(program_start_time, path_settings, directories_data)


def set_logger(log_folder=None):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    if log_folder:  # Создание файла с логами только если указана папка
        log_filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S.log')
        log_file_path = os.path.join(log_folder, log_filename)

        os.makedirs(log_folder, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def load_json(file_path, default_type):
    try:
        file_path = os.path.normpath(file_path)

        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        else:
            logger.warning("Файл %s не найден, возвращаем значение по умолчанию.", file_path)
    except Exception as err:
        logger.error("Ошибка при загрузке файла %s: %s", file_path, err)

    return default_type


if __name__ == "__main__":
    SETTING_PATH = 'settings.json'

    settings = load_json(SETTING_PATH, default_type={})

    if settings['save_logs']:
        logger = set_logger(log_folder=settings['log_folder'])
    else:
        logger = set_logger()

    main(settings)
