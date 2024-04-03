import os
from argparse import ArgumentParser, Namespace
from os.path import join, dirname

from modules.my_parser import UsersideParser, AbillsParser
from modules.class_workbook import MyWorkbook

parser = ArgumentParser()

parser.add_argument('-s', '--start', type=str, help="Start timestamp")
parser.add_argument('-e', '--end', type=str, help="End timestamp")

args: Namespace = parser.parse_args()

us_auth_link = 'http://us3.radionet.com.ua/oper/index.php?w=555'
abills_auth_link = 'https://bill-admin2.radionet.com.ua:9443/admin/index.cgi?DOMAIN_ID=&language=english'

userside_payload = {
    "action": "login",
    "username": os.environ.get("user"),
    "password": os.environ.get("pass"),
}

us_petrivskyy_params = {
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

abills_payload = {
    "DOMAIN_ID": "",
    "REFERER": "https://bill-admin2.radionet.com.ua:9443/admin/index.cgi?DOMAIN_ID=&language=english",
    "LOGIN": "1",
    "language": "english",
    "user": os.environ.get("user"),
    "passwd": os.environ.get("pass"),
    "logined": "Enter",
}

def create_connect_sheet(wb_object, title, types, data, excel_columns):
    wb_object.add_header(types, title)
    wb_object.format_header()
    wb_object.add_main_data(data)
    wb_object.set_border(start=3)
    wb_object.edit_width_for_columns(excel_columns, 2)
    

def create_repair_sheet(wb_object, sheet_name, title, types, data, excel_columns):
    wb_object.create_sheet(sheet_name)
    wb_object.change_active_sheet(sheet_name)
    create_connect_sheet(wb_object, title, types, data, excel_columns)
    wb_object.save_workbook()
    

if __name__ == '__main__':
    us_parser = UsersideParser(us_auth_link, userside_payload, us_petrivskyy_params)
    abills_parser = AbillsParser(abills_auth_link, abills_payload, params=None)
    us_dicts = us_parser.parse()
    us_dicts.reverse()
    excel_workfile = f"tasks-{us_petrivskyy_params['date_finish2_date1']}-{us_petrivskyy_params['date_finish2_date2']}.xlsx"
    wb_path = join(dirname(__file__), 'excel_data', excel_workfile)
    connect_title = f"Історія підключень за {us_petrivskyy_params['date_finish2_date1']}-{us_petrivskyy_params['date_finish2_date2']} (Петрівський Володимир Романович)"
    repair_title = f"Історія ремонтів за {us_petrivskyy_params['date_finish2_date1']}-{us_petrivskyy_params['date_finish2_date2']} (Петрівський Володимир Романович)"
    letter_list = ['A', 'B', 'C', 'D', 'E']
    mywb = MyWorkbook(wb_path, first_page='New Connection')
    
    only_new_conn = []
    repairs = []
    for us_dict in us_dicts:
        if 'Новое подключени' in us_dict['Task type']:
            print(us_dict)
            try:
                us_dict["Contract ID"] = abills_parser.get_contract_id(us_dict["Firstname, Lastname"])
            except AttributeError:
                us_dict["Contract ID"] = "Incorrect_ID"
            only_new_conn.append(us_dict)
        if 'Ремонт' in us_dict['Task type']:
            repairs.append(us_dict)
        
    
    create_connect_sheet(mywb, connect_title, list(only_new_conn[0].keys()), only_new_conn, letter_list)
    create_repair_sheet(mywb, 'Repair', repair_title, list(repairs[0].keys()), repairs, letter_list)