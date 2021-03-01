import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CroatiaItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CroatiaSpider(scrapy.Spider):
	name = 'croatia'
	start_urls = ['https://www.croatiabanka.hr/hr/press/novosti-iz-poslovanja/']

	def parse(self, response):
		yield response.follow(response.url, self.parse_post, dont_filter=True)

		next_page = response.xpath('//li[@class="paging-next"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		articles = response.xpath('//dl[@class="faq"]/dt')
		length = len(articles)

		for index in range(length):
			item = ItemLoader(item=CroatiaItem(), response=response)
			item.default_output_processor = TakeFirst()

			date = response.xpath(f'(//dl[@class="faq"]/dt)[{index + 1}]//span//text()').get()
			title = response.xpath(f'(//dl[@class="faq"]/dt)[{index + 1}]//text()[2]').get()
			if title:
				title =title.strip()
			content = response.xpath(f'(//dl[@class="faq"]/dd)[{index + 1}]//text()').getall()
			content = [p.strip() for p in content if p.strip()]
			content = re.sub(pattern, "",' '.join(content))

			item.add_value('title', title)
			item.add_value('link', response.url)
			item.add_value('content', content)
			item.add_value('date', date)

			yield item.load_item()
