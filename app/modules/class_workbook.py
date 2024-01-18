from openpyxl import Workbook
from openpyxl.styles import Font

class MyWorkbook():
    def __init__(self, wb_file, first_page=''):
        self.wb = Workbook()
        self.wb_file = wb_file
        self.ws = self.wb.active
        self.ws.title = first_page if first_page else 'First Page'
    
    def create_sheet(self, ws_title):
        self.wb.create_sheet(ws_title)
    
    def change_active_sheet(self, ws_title):
        self.ws = self.wb[ws_title]
        
    def add_header(self, types, title):
        self.ws.append([title,])
        self.ws.merge_cells(start_row=1, end_row=1, start_column=1, end_column=len(types))
        self.ws.append([''])
        self.ws.append(types)
    
    def add_main_data(self, data):
        for counter in range(len(data)):
            self.ws.append(list(data[counter].values()))
        
    def edit_width_for_columns(self, list_of_excel_column):
        for letter in list_of_excel_column:
            max_width = 0
            for row_number in range(1, self.ws.max_row + 1):
                value = self.ws[f'{letter}{row_number}'].value
                print(value)
                if len(value) > max_width:
                    max_width = len(value) 
            self.ws.column_dimensions[letter].width = max_width + 1
        
    def save_workbook(self):
        self.wb.save(self.wb_file)
    
    
    
    