import sys, codecs
import requests
from bs4 import BeautifulSoup

# set utf-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

TARGET_URL = 'https://192abc.com'

r = requests.get(TARGET_URL)
soup = BeautifulSoup(r.text, 'lxml')

# large_categories -> middle_categories -> small_categories
#
# start crawling
for categories in soup.find_all(class_='top-list__footer'):
	# large
	for large_categories in categories.find_all(class_='footer-tags-list'):
		print('Large_category : ' + large_categories.find('h2').text)

		# middle
		for mid_categories in large_categories.find_all(class_='footer-tags-list__wrap'):
			for mid_category_link in mid_categories.select('ul > li > a'):
				
				print("Middle_category : " + mid_category_link.text)
				mid_target_url = TARGET_URL + mid_category_link.get('href')
				print(mid_target_url)

				mid_r = requests.get(mid_target_url)
				mid_soap = BeautifulSoup(mid_r.text, 'lxml')
				
				
				# article
				for article_link in mid_soap.find_all(class_='list-article__link'):
					print('title :' + article_link.get('title'))
					print('article link : ' + article_link.get('href'))

					art_r = requests.get(article_link.get('href'))
					art_soap = BeautifulSoup(art_r.text, 'lxml')
						
					art_title = art_soap.find(class_='single-article__title entry-title')
					print('article title: ' + art_title.text)
						
					# small
					small_category = art_soap.find(class_='ranking__title')
					print('Small_category : ' + small_category.text)


					# supervisior
					supervisior_position = art_soap.find(class_='supervisor-profile__position')
					if supervisior_position is not None:
						print('supervisior position : ' + supervisior_position.text)

					supervisior_name = art_soap.find(class_='supervisor-profile__name')
					if supervisior_name is not None:
						print('supervisior name : ' + supervisior_name.text)

					# related article link
					for related_link in art_soap.find_all(class_='related__link'):
						print('related link : ' + related_link.text)
						# print('related link : ' + related_link.get('href'))

					# reference
					for reference_link in art_soap.find_all(class_='reference__link'):
						print('reference link : ' + reference_link.text)
						# print('reference link : ' + reference_link.get('href'))
						
						
					# related keyword
					related_kws = art_soap.find(class_="related-tags")
					for related_kw in related_kws.select('ul > li'):
						print('related kw : ' + related_kw.text)
						
					break
				break
print('end')
