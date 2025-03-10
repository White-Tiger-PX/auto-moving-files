import time

from datetime import datetime


program_start_time        = time.time()
string_program_start_time = datetime.fromtimestamp(program_start_time)

LOG_FOLDER                         = "logs"
DIRECTORY_WITH_SCANNED_DIRECTORIES = "data/scanned_directories"
DIRECTORIES_SETTINGS = [
    {
        "input": "C:/Users/user/Pictures",
        "output": "D:/Backup/Pictures",
        "time_limit_for_modified_time": 604800,
        "time_limit_for_first_seen":    604800,
        "action_by_last_modified": True,
        "action_by_first_seen":    True,
        "save_folders":            True,
        "copy":                    True,
        "overwrite_files":         False,
        "file_name_exceptions": [

        ],
        "directory_name_exceptions": [

        ],
        "date_grouping_options": {
            "create_date_folders_in_root": False,
            "group_by_days":   False,
            "group_by_months": False,
            "group_by_years":  False
        }
    }
]
