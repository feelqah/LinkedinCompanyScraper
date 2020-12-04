from bs4 import BeautifulSoup
import requests
import string
import pickle
import pyfiglet
from sys import stdout
from time import sleep
import creds

# TODO: Implement the company url scraper

class LinkedIn:

    def __init__(self):
        self.s = requests.Session()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36 OPR/67.0.3575.97"
        }

    def login(self, email, password):
        # creates a session
        try:
            sc = self.s.get("https://www.linkedin.com/login",
                            headers=self.headers).text
        except:
            return False
        csrfToken = sc.split('csrfToken" value="')[1].split('"')[0]
        sid = sc.split('sIdString" value="')[1].split('"')[0]
        pins = sc.split('pageInstance" value="')[1].split('"')[0]
        lcsrf = sc.split('loginCsrfParam" value="')[1].split('"')[0]
        data = {
            'csrfToken': csrfToken,
            'session_key': email,
            'ac': '2',
            'sIdString': sid,
            'parentPageKey': 'd_checkpoint_lg_consumerLogin',
            'pageInstance': pins,
            'trk': 'public_profile_nav-header-signin',
            'authUUID': '',
            'session_redirect': 'https://www.linkedin.com/feed/',
            'loginCsrfParam': lcsrf,
            'fp_data': 'default',
            '_d': 'd',
            'showGoogleOneTapLogin': 'true',
            'controlId': 'd_checkpoint_lg_consumerLogin-login_submit_button',
            'session_password': password,
            'loginFlow': 'REMEMBER_ME_OPTIN'
        }
        try:
            after_login = self.s.post(
                "https://www.linkedin.com/checkpoint/lg/login-submit", headers=self.headers, data=data).text
        except:
            return False
        is_logged_in = after_login.split('<title>')[1].split('</title>')[0]
        if is_logged_in == "LinkedIn":
            return True
        else:
            return False

    def get_all_urls(self, url):
        urls = list()
        parser = 'html.parser'

        resp = self.s.get(url, headers=self.headers, allow_redirects=True)

        soup = BeautifulSoup(resp.content, parser, from_encoding=resp.encoding)

        for link in soup.find_all('a', href=True):
            href = link['href']

            if href.startswith("http"):
                urls.append(href)

        return urls

    def get_public_dir_companies(self, csv_filename):

        num_companies = 0

        alphabet = list(string.ascii_lowercase)

        # gather all company URLs
        for letter in alphabet:
            page_urls = list()
            company_urls = list()

            print("Gathering company URls for comapnies starting with '%s'" % letter)

            url = "https://www.linkedin.com/directory/companies/%s-1" % letter

            urls = self.connection.get_all_urls(url)

            for url in urls:
                if url.startswith("https://www.linkedin.com/company/"):
                    company_urls.append(url)
                elif url.startswith("https://www.linkedin.com/directory/companies/%s-" % letter):
                    page_urls.append(url)

            for i, page_url in enumerate(page_urls[1:]):
                stdout.write("\rPage %s of %s" %
                             (str(i+1), len(page_urls[1:])))
                stdout.flush()
                sleep(1)

                urls = self.connection.get_all_urls(page_url)

                for url in urls:
                    if url.startswith("https://www.linkedin.com/company/"):
                        company_urls.append(url)

            stdout.write("\n")  # move the cursor to the next line

            # save companies to file
            with open(csv_filename, "a") as file:
                for company in company_urls:

                    file.write(company + "\n")

                    num_companies += 1

        print("Saved %s comapnies!" % str(num_companies))

    def get_company_info(self, url):
        # TODO: implement company info scraper
        pass


def main():
    csv_filename = "comapny_urls"

    banner = pyfiglet.figlet_format("LINKEDIN COMPANY FETCHER 3000")
    print(banner)

    linkedin_email = creds.linkedin_email
    linkedin_password = creds.linkedin_password

    connection = LinkedIn()
    login_state = connection.login(linkedin_email, linkedin_password)

    if login_state:
        print("Logged in to LinkedIn!")

        # get all companies and save them to csv
        connection.get_public_dir_companies(csv_filename)

        # TODO: implement get_company_info
        url = "https://www.linkedin.com/company/a2z-advisors-llc/?trk=companies_directory"
        company_info = connection.get_company_info(url)


if __name__ == "__main__":
    main()
