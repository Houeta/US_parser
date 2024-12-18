import os
import logging
from argparse import ArgumentParser, Namespace
from os.path import join, dirname
from dotenv import load_dotenv

from modules.my_parser import UsersideParser, AbillsParser
from modules.class_workbook import MyWorkbook

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables
load_dotenv()

def validate_date(date_str):
    """
    Validate the date string format.

    Args:
        date_str (str): The date string to validate.

    Returns:
        datetime.datetime: The datetime object if the date string is valid.

    Raises:
        ValueError: If the date string has an incorrect format.
    """
    from datetime import datetime
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        logging.error('Incorrect data format, should be YYYY-MM-DD')
        exit(1)

def get_args():
    """
    Get command line arguments.

    Returns:
        Namespace: The parsed command line arguments.
    """
    parser = ArgumentParser(description="Parse data from us3.radionet.com.ua and bill-admin2.radionet.com.ua")
    parser.add_argument('-s', '--start', type=str, help="Start timestamp (format: YYYY-MM-DD)")
    parser.add_argument('-e', '--end', type=str, help="End timestamp (format: YYYY-MM-DD)")
    args: Namespace = parser.parse_args()

    # Validate the date strings 
    validate_date(args.start)
    validate_date(args.end)
    return args

def create_excel_sheet(wb_object, sheet_name, title, types, data, excel_columns):
    """
    Create an Excel sheet with specified data.

    Args:
        wb_object (MyWorkbook): The workbook object to create the sheet in.
        sheet_name (str): The name of the sheet.
        title (str): The title of the sheet.
        types (list): The types of the data columns.
        data (list): The data to be added to the sheet.
        excel_columns (list): The columns to adjust the width for.
    """
    wb_object.create_sheet(sheet_name)
    wb_object.change_active_sheet(sheet_name)
    wb_object.add_header(types, title)
    wb_object.format_header()
    wb_object.add_main_data(data)
    wb_object.set_border(start=3)
    wb_object.edit_width_for_columns(excel_columns, 2)
    wb_object.save_workbook()

def main():
    """
    Main function to parse data from Userside and Abills, and save it to an Excel file.
    """
    args = get_args()

    # Userside data
    us_auth_link = os.getenv("US_AUTH_LINK", "http://us3.radionet.com.ua/oper/index.php?w=555")
    userside_payload = {
        "action": "login",
        "username": os.getenv("US_USER"),
        "password": os.getenv("US_PASS"),
    }
    us_params = {
        "core_section": 'task_list',
        'filter_selector0': 'task_state',
        'task_state0_value': 2,
        'filter_selector1': 'task_staff',
        'employee_find_input': None,
        'employee_id1': 63,
        'filter_selector2': 'date_finish',
        'date_finish2_value2': 1,
        'date_finish2_date1': args.start,
        'date_finish2_date2': args.end,
    }

    # Abills data
    abills_auth_link = os.getenv("ABILLS_AUTH_LINK", "https://bill-admin2.radionet.com.ua:9443/admin/")
    abills_payload = {
        "DOMAIN_ID": "",
        "REFERER": abills_auth_link,
        "LOGIN": "1",
        "language": "english",
        "user": os.getenv("ABILLS_USER"),
        "passwd": os.getenv("ABILLS_PASS"),
        "logined": "Enter",
    }

    # Initialize parsers
    logging.info("Parsing data from Userside and Abills")
    us_parser = UsersideParser(us_auth_link, userside_payload, us_params)
    abills_parser = AbillsParser(abills_auth_link, abills_payload, params=None)

    # Parse data from Userside
    logging.info("Parsing data from Userside")
    us_dicts = us_parser.parse()
    if not us_dicts:
        logging.error("Failed to parse data from Userside")
        exit(1)
    
    us_dicts.reverse()

    # Generate Excel file
    excel_workfile = f"tasks-{args.start}-{args.end}.xlsx"
    wb_path = join(dirname(__file__), 'excel_data', excel_workfile)
    mywb = MyWorkbook(wb_path, first_page='New Connection')

    connect_title = f"Історія підключень за {args.start}-{args.end}"
    repair_title = f"Історія ремонтів за {args.start}-{args.end}"
    letter_list = ['A', 'B', 'C', 'D', 'E']

    # Split data into new connections and repairs
    only_new_conn, repairs = [], []
    logging.info("Processing data...")
    for us_dict in us_dicts:
        if 'Новое подключени' in us_dict['Task type']:
            try:
                us_dict["Contract ID"] = abills_parser.get_contract_id(us_dict["Firstname, Lastname"])
            except AttributeError:
                us_dict["Contract ID"] = "Incorrect_ID"
            only_new_conn.append(us_dict)
        elif 'Ремонт' in us_dict['Task type']:
            repairs.append(us_dict)
    
    # Create Excel sheets
    create_excel_sheet(mywb, "Connections", connect_title, list(only_new_conn[0].keys()), only_new_conn, letter_list)
    create_excel_sheet(mywb, "Repairs", repair_title, list(repairs[0].keys()), repairs, letter_list)

    logging.info(f"Data has been saved to {wb_path}")

if __name__ == '__main__':
    main()