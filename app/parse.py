import os
from argparse import ArgumentParser, Namespace
from os.path import join, dirname
from typing import Dict, Any

from modules.my_parser import UsersideParser, AbillsParser
from modules.class_workbook import MyWorkbook


def get_args() -> Namespace:
    """
    Parse and return command line arguments.
    """
    parser = ArgumentParser()
    parser.add_argument('-s', '--start', type=str, help="Start timestamp")
    parser.add_argument('-e', '--end', type=str, help="End timestamp")
    return parser.parse_args()


def get_userside_payload() -> Dict[str, str]:
    """
    Return the payload for Userside authentication.
    """
    return {
        "action": "login",
        "username": os.environ.get("user"),
        "password": os.environ.get("pass"),
    }


def get_us_petrivskyy_params(args: Namespace) -> Dict[str, Any]:
    """
    Return the parameters for Userside request.
    """
    return {
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


def main() -> None:
    """
    Main function to execute the script.
    """
    args = get_args()

    us_auth_link = 'http://us3.radionet.com.ua/oper/index.php?w=555'
    abills_auth_link = 'https://bill-admin2.radionet.com.ua:9443/admin/index.cgi?DOMAIN_ID=&language=english'

    userside_payload = get_userside_payload()
    us_petrivskyy_params = get_us_petrivskyy_params(args)

    # Initialize parsers
    userside_parser = UsersideParser(auth_link=us_auth_link, payload=userside_payload, params=us_petrivskyy_params)
    abills_parser = AbillsParser(auth_link=abills_auth_link, payload=userside_payload)

    # Example usage of parsers (implement your logic here)
    try:
        userside_content = userside_parser.parse()
        print(userside_content)
    except RuntimeError as e:
        print(f"Error parsing Userside content: {e}")

    # Parse Abills content
    try:
        abills_content = abills_parser.get_contract_id("example_name")  # Replace "example_name" with actual name
        print(abills_content)
    except RuntimeError as e:
        print(f"Error parsing Abills content: {e}")

    # Create workbook
    try:
        workbook = MyWorkbook()
        workbook.add_sheet("Userside Data", userside_content)
        workbook.add_sheet("Abills Data", abills_content)
        workbook.save("output.xlsx")
    except Exception as e:
        print(f"Error creating workbook: {e}")


if __name__ == "__main__":
    main()