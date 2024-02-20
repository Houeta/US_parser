import requests
import re

from bs4 import BeautifulSoup
import fake_useragent

class Parser():
    def __init__(self, auth_link, payload, params):
        self.auth_link = auth_link
        self.fake_header = fake_useragent.UserAgent().random
        self.session = requests.Session()
        self.payload = payload
        self.params = params
        
        self.header = {
            'user-agent': self.fake_header
        }
        
        self.response = self.session.post(self.auth_link, data=self.payload, headers=self.header).text
    
    def get_html(self, url, params=None):
        return self.session.get(url=url, headers=self.header, params=params)
    
    def get_content(self):
        raise
    
    def parse(self):
        raise


class UsersideParser(Parser):
    def __init__(self, auth_link, payload, params):
        super(UsersideParser, self).__init__(auth_link, payload, params)
        self.USERSIDE_URL = 'http://us3.radionet.com.ua/oper/index.php'
        self.auth_link = 'http://us3.radionet.com.ua/oper/index.php?w=555'
        
    def task_wrapper(self, args):
        temp_dict = dict()
        temp_dict['Execution date'] = args[3]
        temp_dict['Contract ID'] = None
        name = re.search(r"\S+\s+\S+\s+\S+", args[5])
        try:
            temp_dict['Firstname, Lastname'] = name.group(0).strip()
        except Exception:
            temp_dict['Firstname, Lastname'] = f"Невірний синтакс: {args[5][:15]}..."
        temp_dict['Task type'] = args[1]
        temp_dict['Address'] = args[4]
        
        if 'Ремонт' in temp_dict['Task type']:
            try:
                temp_dict['Comments'] = args[7]
            except IndexError:
                temp_dict['Comments'] = "Коментар відсутній"
        
        return temp_dict
    
    def _extract_text_with_indentation(self, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')
            td_tag = soup.find('td')
            
            if td_tag:
                extracted_text = td_tag.prettify(formatter=None)
                return extracted_text
            else:
                raise ValueError('A tag <td> not found in entered HTML')
        except Exception:
            return None
            
    def get_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tasks = soup.find_all('tr', {"class": "table_item"})
        task_content = []
        for task in tasks:
            one_task_content = []
            for child_str in task.children:
                print(child_str)
                task_data = self._extract_text_with_indentation(child_str)
                if not task_data:
                    task_data = child_str.get_text(strip=True)
                if task_data:
                    one_task_content.append(task_data)
            # print(one_task_content)
            task_content.append(self.task_wrapper(one_task_content))
        
        return task_content
    
    def parse(self):
        html = self.get_html(self.USERSIDE_URL, self.params)
            
        if html.status_code == 200:
            self.content = self.get_content(html.text)
            return self.content
        else:
            print('Error!')
            
class AbillsParser(Parser):
    def __init__(self, auth_link, payload, params):
        super(AbillsParser, self).__init__(auth_link, payload, params)
        self.ABILLS_URL = 'https://bill-admin2.radionet.com.ua:9443/admin/index.cgi'
        self.auth_link = 'https://bill-admin2.radionet.com.ua:9443/admin/'
        
        self.search_payload = {
            "index": 7,
            "search": 1,
            "type": 10,
        }
        
    def find_value_by_class(self, html, xml_class):
        soup = BeautifulSoup(html, 'html.parser')
        tag_contract = soup.find('input', {"id": xml_class})
        return tag_contract.get('value')
        
    def get_contract_id(self, name):
        self.search_payload["LOGIN"] = name
        parsed_page = self.get_html(url=self.ABILLS_URL, params=self.search_payload)
        
        return self.find_value_by_class(parsed_page.text, "CONTRACT_ID")
        