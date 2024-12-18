import requests
import re
from bs4 import BeautifulSoup
import fake_useragent
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Parser:
    def __init__(self, auth_link, payload, params):
        self.auth_link = auth_link
        self.fake_header = fake_useragent.UserAgent().random
        self.session = requests.Session()
        self.payload = payload
        self.params = params        
        self.header = {'user-agent': self.fake_header}
        self.authenticate() 
    
    def authenticate(self):
        response = self.session.post(self.auth_link, data=self.payload, headers=self.header)
        if response.status_code != 200:
            logging.error(f'Authentication failed! Status code: {response.status_code}')
            raise ConnectionError('Authentication failed!')
        logging.info('Authentication successful!')

    def get_html(self, url, params=None):
        response = self.session.get(url=url, headers=self.header, params=params)
        if response.status_code != 200:
            logging.error(f'Failed to fetch URL: {url}. Status code: {response.status_code}')
            return None
        return response.text
    
    def get_content(self, html):
        raise NotImplementedError('Method get_content() must be implemented in subclass')
    
    def parse(self):
        raise NotImplementedError('Method parse() must be implemented in subclass')


class UsersideParser(Parser):
    def __init__(self, auth_link, payload, params):
        super().__init__(auth_link, payload, params)
        self.USERSIDE_URL = 'http://us3.radionet.com.ua/oper/index.php'
        
    def task_wrapper(self, args):
        task = {
            'Execution date': args[3],
            'Contract ID': None,
            'Firstname, Lastname': re.search(r"\S+\s+\S+\s+\S+", args[5]).group(0).strip(),
            'Task type': args[1],
            'Address': args[4],
            'Comments': args[7] if 'Ремонт' in args[1] else None,
        }  
        return task
    
    def _extract_text_with_indentation(self, tag):
        if not tag:
            return None
        return tag.get_text(strip=True)
        # try:
        #     soup = BeautifulSoup(html, 'html.parser')
        #     td_tag = soup.find('td')
            
        #     if td_tag:
        #         extracted_text = td_tag.prettify(formatter=None)
        #         return extracted_text
        #     else:
        #         raise ValueError('A tag <td> not found in entered HTML')
        # except Exception:
        #     return None
            
    def get_content(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tasks = soup.find_all('tr', class_="table_item")
        task_content = []

        for task in tasks:
            one_task_content = [self._extract_text_with_indentation(child) for child in task.children]
            task_content.append(self.task_wrapper(one_task_content))
            # for child_str in task.children:
            #     print(child_str)
            #     task_data = self._extract_text_with_indentation(child_str)
            #     if not task_data:
            #         task_data = child_str.get_text(strip=True)
            #     if task_data:
            #         one_task_content.append(task_data)
            # print(one_task_content)
            # task_content.append(self.task_wrapper(one_task_content))
        
        return task_content
    
    def parse(self):
        html = self.get_html(self.USERSIDE_URL, self.params)  
        if html:
            return self.get_content(html)
        logging.error('Failed to retrieve data from Userside')
        return None
            
class AbillsParser(Parser):
    def __init__(self, auth_link, payload, params):
        super().__init__(auth_link, payload, params)
        self.ABILLS_URL = 'https://bill-admin2.radionet.com.ua:9443/admin/index.cgi'
        self.search_payload = {"index": 7, "search": 1, "type": 10}
        
    def find_value_by_class(self, html, xml_class):
        soup = BeautifulSoup(html, 'html.parser')
        tag_contract = soup.find('input', {"id": xml_class})
        return tag_contract.get('value') if tag_contract else None
        
    def get_contract_id(self, name):
        self.search_payload["LOGIN"] = name
        parsed_page = self.get_html(url=self.ABILLS_URL, params=self.search_payload)
        if parsed_page:
            return self.find_value_by_class(parsed_page, "CONTRACT_ID")
        logging.warning(f'Contract ID not found for user: {name}')        
        return "Not found"
        