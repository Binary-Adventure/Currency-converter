import asyncio
import aiohttp

from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from json import load, dump
from time import localtime, strftime



class App:
	def __init__(self):
		pass


	async def currency_update(self, currency_block):
		info = currency_block.find('div', {'class': 'xxx-tbl-cell xxx-tbl-cell--center-v xxx-fs-18'})
		price = currency_block.find('span', {'class': 'xxx-fs-18'})

		if info != None:
			info = info.text.split()

			if int(info[0]) == 1:
				self.currency_dict[info[1]] = float(price.text)

			else:
				price = float(price.text) / int(info[0])
				self.currency_dict[info[1]] = float('%.4f' % price)


	async def parser(self, link, headers):
		async with aiohttp.ClientSession() as session:
			async with session.get(url=link, headers=headers) as response:
				response = await aiohttp.StreamReader.read(response.content)
				soup = BeautifulSoup(response, 'lxml')

				tasks = []

				for currency_block in soup.find_all('div', {'class': 'xxx-tbl-row'}):
					tasks.append(self.currency_update(currency_block))

				asyncio.gather(*tasks)


	async def exam_update_time(self):
		with open('currencies.json', 'r+') as file:
			data = load(file)
			lastUpdateTime = data['lastUpdateTime']
			timeNow = int(strftime('%H', localtime()))

			if lastUpdateTime > timeNow:
				self.currency_dict = {}

				await self.parser(
					link='https://bankiros.ru/currency/cbrf',
					headers={'user-agent': UserAgent().random}
				)

				data['lastUpdateTime'] = timeNow
				data['RUB'] = self.currency_dict

				file.seek(0)
				dump(data, file, indent=4)

				await asyncio.sleep(.25)


async def main(app):
	await app.exam_update_time()


if __name__ == '__main__':
	asyncio.run(main(App()))