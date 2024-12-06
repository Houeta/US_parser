import requests
import re
from bs4 import BeautifulSoup
import fake_useragent
from typing import Dict, Optional, Any, List


class Parser:
    def __init__(self, auth_link: str, payload: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> None:
        self.auth_link = auth_link
        self.fake_header = fake_useragent.UserAgent().random
        self.session = requests.Session()
        self.payload = payload
        self.params = params or {}

        self.header = {
            'user-agent': self.fake_header
        }

        self.response = self._authenticate()

    def _authenticate(self) -> str:
        try:
            response = self.session.post(self.auth_link, data=self.payload, headers=self.header)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise RuntimeError(f"Authentication failed: {e}")

    def get_html(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        try:
            response = self.session.get(url=url, headers=self.header, params=params)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get HTML content: {e}")

    def get_content(self) -> None:
        raise NotImplementedError("Subclasses should implement this method")

    def parse(self) -> None:
        raise NotImplementedError("Subclasses should implement this method")


class UsersideParser(Parser):
    def __init__(self, auth_link: str, payload: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(auth_link, payload, params)
        self.USERSIDE_URL = 'http://us3.radionet.com.ua/oper/index.php'
        self.auth_link = 'http://us3.radionet.com.ua/oper/index.php?w=555'

    def task_wrapper(self, args: List[str]) -> Dict[str, Optional[str]]:
        temp_dict = {
            'Execution date': args[3],
            'Contract ID': None,
            'Firstname, Lastname': None,
            'Task type': args[1],
            'Address': args[4],
            'Comments': None
        }

        name = re.search(r"\S+\s+\S+\s+\S+", args[5])
        if name:
            temp_dict['Firstname, Lastname'] = name.group(0).strip()
        else:
            temp_dict['Firstname, Lastname'] = f"Невірний синтакс: {args[5][:15]}..."

        if 'Ремонт' in temp_dict['Task type']:
            temp_dict['Comments'] = args[7] if len(args) > 7 else "Коментар відсутній"

        return temp_dict

    def _extract_text_with_indentation(self, html: str) -> Optional[str]:
        try:
            soup = BeautifulSoup(html, 'html.parser')
            td_tag = soup.find('td')
            if td_tag:
                return td_tag.prettify(formatter=None)
            else:
                raise ValueError('A tag <td> not found in entered HTML')
        except Exception:
            return None

    def get_content(self, html: str) -> List[Dict[str, Optional[str]]]:
        soup = BeautifulSoup(html, 'html.parser')
        tasks = soup.find_all('tr', {"class": "table_item"})
        task_content = []

        for task in tasks:
            one_task_content = []
            for child_str in task.children:
                task_data = self._extract_text_with_indentation(str(child_str))
                if not task_data:
                    task_data = child_str.get_text(strip=True)
                if task_data:
                    one_task_content.append(task_data)
            task_content.append(self.task_wrapper(one_task_content))

        return task_content

    def parse(self) -> List[Dict[str, Optional[str]]]:
        html = self.get_html(self.USERSIDE_URL, self.params)
        if html.status_code == 200:
            self.content = self.get_content(html.text)
            return self.content
        else:
            raise RuntimeError('Error fetching content')


class AbillsParser(Parser):
    def __init__(self, auth_link: str, payload: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(auth_link, payload, params)
        self.ABILLS_URL = 'https://bill-admin2.radionet.com.ua:9443/admin/index.cgi'
        self.auth_link = 'https://bill-admin2.radionet.com.ua:9443/admin/'

        self.search_payload = {
            "index": 7,
            "search": 1,
            "type": 10,
        }

    def find_value_by_class(self, html: str, xml_class: str) -> Optional[str]:
        soup = BeautifulSoup(html, 'html.parser')
        tag_contract = soup.find('input', {"id": xml_class})
        return tag_contract.get('value') if tag_contract else None

    def get_contract_id(self, name: str) -> Optional[str]:
        self.search_payload["LOGIN"] = name
        parsed_page = self.get_html(url=self.ABILLS_URL, params=self.search_payload)
        return self.find_value_by_class(parsed_page.text, "CONTRACT_ID")