import os
import shutil
from datetime import datetime
import scrapy
from bs4 import BeautifulSoup


class WebSpider(scrapy.Spider):
    name = 'webspider'

    def __init__(self, domain=None, url=None):
        super(WebSpider, self).__init__()
        url = str(url) if url.startswith('http://') else 'http://%s' % str(url)
        self.start_urls = [str(url)]
        self.allowed_domains = [str(domain)]

        self.total_char = 0
        self.total_word = 0
        self.total_file = []

        now = datetime.now()
        self.timestamp = '{}-{}-{}'.format(now.day, now.month, now.year)

        self.dir_name = '{}_{}'.format(self.allowed_domains[0], self.timestamp)

        if os.path.exists(self.dir_name):
            shutil.rmtree(self.dir_name)
        os.mkdir(self.dir_name)

    def parse(self, response):
        for href in response.css("a::attr('href')"):
            url = response.urljoin(href.extract())
            yield scrapy.Request(url, callback=self.parse_dir_content)

    def parse_dir_content(self, response):
        filename = response.url.split('/')[-2]
        filename = filename if filename else response.url.split("/")[-1]
        filename += '.html'

        summary_file = 'summary_{}_{}.txt' \
            .format(self.allowed_domains[0], self.timestamp)

        text = WebSpider.remove_tags(response.body)

        # Words, characters, files statistics
        word_count = len(text.split())
        char_count = sum((len(word) for word in text.split()))
        self.total_char += char_count
        self.total_word += word_count
        self.total_file.append(filename)

        file_path = os.path.join(self.dir_name, filename)
        stats_path = os.path.join(self.dir_name, summary_file)
        with open(file_path, 'w') as f, open(stats_path, 'w') as s:
            f.write(text)
            s.write('Domain scraped: {}\n\n'.format(self.allowed_domains[0]))
            s.write('words: {wc:,}\ncharacters: {cc:,}\nin {file} file(s)'
                    .format(file=len(self.total_file), wc=self.total_word, cc=self.total_char))

    # Remove redundant tags with its content, and then superflous whitespaces
    @staticmethod
    def remove_tags(html):
        soup = BeautifulSoup(html, 'lxml')

        for script in soup(['script', 'style', 'meta']):
            script.extract()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text
