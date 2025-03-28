import requests

from langcodes import Language


class APIHandler:
    def __init__(self, search, search_type, sort_type):
        self.API_PATH = 'https://openlibrary.org/search.json?'

        self.filter_dict = {
            'title': 'title',
            'author': 'author_name',
            'release date': 'first_publish_year'
        }

        self.search = search
        self.search_type = search_type
        self.sort_type = self.filter_dict[sort_type]

    def create_request(self):
        if self.search_type == 'author':
            self.API_PATH += 'author='
        elif self.search_type == 'title':
            self.API_PATH += 'title='

        for index, word in enumerate(self.search):
            self.API_PATH += f'{word}'
            if index != len(self.search) - 1:
                self.API_PATH += '+'

    def submit_request(self):
        response = requests.get(self.API_PATH)
        return response

    def determine_key(self, doc):
        sort_value = None

        try:
            if self.sort_type == 'first_publish_year':
                sort_value = doc[f'{self.sort_type}']
            else:
                sort_value = doc[f'{self.sort_type}'][0]
        except:
            sort_value = False

        if sort_value:
            if self.sort_type == 'first_publish_year':
                return int(sort_value)
            else:
                return sort_value
        else:
            if self.sort_type == 'first_publish_year':
                return 0
            else:
                return 'Z'

    def handle_response(self, response):
        book_info = []

        data = response.json()

        print(data['docs'][0])
        for doc in data['docs']:
            book_info.append(doc)

        book_info = sorted(book_info, key=self.determine_key)

        if self.sort_type != 'first_publish_year':
            book_info.reverse()
        return book_info

    def request_sequence(self):
        self.create_request()
        response = self.submit_request()
        book_info = self.handle_response(response)
        return book_info


class Main:
    def __init__(self):
        self.running = True

        self.user_choice = None
        self.search = None

        self.main_loop()

    def menu(self):
        print('\n' * 32)

        print('''
Welcome to BookSearcher!

Options:
    1. Search by Title
    2. Search by Author
    3. Quit
        ''')

        user_choice = None
        user_choice_valid = False

        while not user_choice_valid:
            user_choice = input("Enter your choice: ")

            if user_choice.isnumeric() and int(user_choice) in [1, 2, 3]:
                user_choice_valid =  True
            else:
                print("Invalid choice. Please try again.")

        self.user_choice = int(user_choice)

    def handle_user_choice(self):
        if self.user_choice == 1:
            self.search_by_title()
            sort_type = self.get_sort_type()
            results = APIHandler(self.search, 'title', sort_type).request_sequence()
            self.display_results(results)
        elif self.user_choice == 2:
            self.search_by_author()
            sort_type = self.get_sort_type()
            results = APIHandler(self.search, 'author', sort_type).request_sequence()
            self.display_results(results)
        elif self.user_choice == 3:
            self.running = False

    def get_sort_type(self):
        print('\n' * 32)

        sort_type = None

        print('''
Select sort type:
    1. By Author (ascending)
    2. By Title (ascending)
    3. By Release Date (descending)
        ''')

        user_choice = None
        user_choice_valid = False

        while not user_choice_valid:
            user_choice = input("Enter your choice: ")

            if user_choice.isnumeric() and int(user_choice) in [1, 2, 3]:
                user_choice_valid = True
            else:
                print("Invalid choice. Please try again.")

        match int(user_choice):
            case 1:
                sort_type = 'author'
            case 2:
                sort_type = 'title'
            case 3:
                sort_type = 'release date'

        return sort_type

    def search_by_title(self):
        print('\n' * 32)

        search_valid = False

        while not search_valid:
            self.search = input('Enter book title: ')
            if self.validate_search():
                search_valid = True
            else:
                print("Invalid book title. Please try again.")

        self.clean_search()

    def search_by_author(self):
        print('\n' * 32)

        search_valid = False

        while not search_valid:
            self.search = input('Enter book author: ')
            if self.validate_search():
                search_valid = True
            else:
                print("Invalid book author. Please try again.")

        self.clean_search()

    def clean_search(self):
        self.search = self.search.lower()
        self.search = self.search.split(' ')

    def validate_search(self):
        if any(char.isdigit() for char in self.search):
            return False
        else:
            return True

    def get_authors(self, result):
        try:
            authors = ', '.join(result['author_name'])
            return authors
        except:
            return None

    def get_release_date(self, result):
        try:
            release_date = result['first_publish_year']
            return release_date
        except:
            return None

    def get_languages(self, result):
        try:
            language_list = []
            languages = result['language']

            for language in languages:
                language_list.append(Language.get(language).display_name())

            languages = ', '.join(language_list)
            return languages
        except:
            return None

    def display_results(self, results):
        print('\n' * 32)

        print(f'Search results ({len(results)}):')
        for index, result in enumerate(results):
            print(f'''
-----------------------------------------------
{len(results)-index}:
    Title: {result['title']}
    Author(s): {self.get_authors(result)}
    
    Release Date: {self.get_release_date(result)}
    Language(s): {self.get_languages(result)}''')

    def quit(self):
        quit()

    def main_loop(self):
        while self.running:
            self.menu()
            self.handle_user_choice()
            input('\nEnter to return to menu: ')



if __name__ == '__main__':
    main = Main()