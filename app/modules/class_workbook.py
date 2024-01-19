from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side

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
    
    def format_header(self):
        cols = range(1, self.ws.max_column+1)
        rows = range(1, self.ws.max_row+1)
        for col in cols:
            for row in rows:
                self.ws.cell(row=row, column=col).alignment = Alignment(horizontal='center')
                self.ws.cell(row=row, column=col).font = Font(bold=True)
                
    def set_border(self, side=None, blank=True, start=1):
        side = side if side else Side(border_style='thin', color='8A0101')
        # Main columns
        for col in range(1, self.ws.max_column+1):
            self.ws.cell(row=start, column=col).border = Border(top=side, bottom=side, left=side, right=side)
        # Another cells
        for col in range(1, self.ws.max_column+1):
            for row in range(start+1, self.ws.max_row):
                self.ws.cell(row=row, column=col).border = Border(left=side, right=side)
        # Bottom row
        for col in range(1, self.ws.max_column+1):
            self.ws.cell(row=self.ws.max_row, column=col).border = Border(left=side, bottom=side, right=side)
    
    def add_main_data(self, data):
        for counter in range(len(data)):
            self.ws.append(list(data[counter].values()))
        
    def edit_width_for_columns(self, list_of_excel_column, min_row):
        for letter in list_of_excel_column:
            max_width = 0
            for row_number in range(min_row, self.ws.max_row + 1):
                value = self.ws[f'{letter}{row_number}'].value
                if not value:
                    continue
                if len(value) > max_width:
                    max_width = len(value)
            self.ws.column_dimensions[letter].width = max_width + 1
        self.edit_height_for_row(min_row)
            
    def edit_height_for_row(self, min_row=1):
        for row in range(min_row, self.ws.max_row+1):
            max_height = 0
            for col in range(1, self.ws.max_column+1):
                value = self.ws.cell(row=row, column=col).value
                if value and len(value.splitlines()) > 1:
                    print(value)
                    counter = len(str(value).split('\n'))
                    max_height = counter if counter > max_height else max_height
            self.ws.row_dimensions[row].height = max_height
        
    def save_workbook(self):
        self.wb.save(self.wb_file)
    
    
    
    