import json
import scrapy
import multiprocessing
from scrapy.crawler import CrawlerProcess
from flask import Flask
import time


app = Flask(__name__)

crawler_executado = False
tempo_atual = time.time()

# Converter o tempo em segundos para uma representação de data e hora legível
hora_execucao = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tempo_atual))
class WhiskSpider(scrapy.Spider):
    name="whisk"
    custom_settings={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    }
    def start_requests(self) :
        yield scrapy.Request('https://www.casadabebida.com.br/whisky/')

    def parse(self, response):
        products = response.css('div.produtos-categoria-thumb')
        for itens in products:
            yield{
                'name': itens.css("h3>a::text").get(),
                'price': itens.css('span.price span:nth-child(2)::text').get(),
                'time': hora_execucao
            }
        for x in range(2, 6):
            yield(scrapy.Request(f'https://www.casadabebida.com.br/whisky/pagina-{x}/', callback= self.parse))
def run_crawler():
    process = CrawlerProcess(settings={
        'FEEDS': {'output.json': {'format': 'json', 'overwrite': True}},  # new in 2.1
        'FEED_EXPORT_ENCODING': 'utf8',
        'LOG_ENABLED': False
    })

    process.crawl(WhiskSpider)
    process.start()
def ler_arquivo():
    global crawler_executado
    with open('output.json','r') as f:
        data = json.load(f)
        crawler_executado = False
        return data

@app.route('/')
def get_offers():
    global crawler_executado

    # Verificar se o crawler já foi executado
    if not crawler_executado:
        # Executar o crawler apenas se ainda não foi executado
        p = multiprocessing.Process(target= run_crawler)
        p.start()
        p.join()
        crawler_executado = True

    # Ler e retornar dados do arquivo JSON
    data = ler_arquivo()
    return data

if __name__ == '__main__':
    # Executar o aplicativo Flask no modo de desenvolvimento
    app.run(debug=True)