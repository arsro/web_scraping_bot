# coding: UTF-8
import codecs
import re
import requests
import sys
from bs4 import BeautifulSoup
from time import sleep

# エンコードの設定
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

# 対象のURL
TARGET_URL = 'https://192abc.com'

# topページをクローリング
top_r = requests.get(TARGET_URL)
top_soup = BeautifulSoup(top_r.text, 'lxml')

# 大カテゴリ(large_category) -> 中カテゴリ(middle_category) -> 小カテゴリ(small_category)の順でクローリングします。

# start crawling
# topページの下にある大カテゴリを取得します。
for categories in top_soup.find_all(class_='top-list__footer'):
	# Large categoryを取得
	for large_categories in categories.find_all(class_='footer-tags-list'):
		# 大カテゴリ
		print('Large_category : ' + re.sub(u'の関連カテゴリ', '', large_categories.find('h2').text))

		# 大カテゴリ内の中カテゴリを取得します。
		for mid_categories in large_categories.find_all(class_='footer-tags-list__wrap'):
			for mid_category_link in mid_categories.select('ul > li > a'):
				
				# 中カテゴリ
				print("Middle_category : " + mid_category_link.text)
				
				# 中カテゴリのリンク
				mid_target_url = TARGET_URL + mid_category_link.get('href')

				is_last = False
				page    = 0
				while not(is_last):
					page += 1
					sleep(1)
					print(mid_target_url + '/page/' + str(page))

					#　中カテゴリページをクローリングします。
					mid_r = requests.get(mid_target_url + '/page/' + str(page))
					mid_soap = BeautifulSoup(mid_r.text, 'lxml')
						
					# コンテンツがないページに行き付いたらクローリングを終了します。
					not_found_page = mid_soap.find('h1', class_='not-found__title')
					if not_found_page is not None:
						is_last = True
						continue

					# 中カテゴリに表示された各記事のリンクを取得します。
					for article_link in mid_soap.find_all(class_='list-article__link'):
						# 記事へのリンク
						print('article link : ' + article_link.get('href'))

						sleep(1)
						# 記事内をクローリングします。
						art_r = requests.get(article_link.get('href'))
						art_soap = BeautifulSoup(art_r.text, 'lxml')

						# 記事タイトル
						art_title = art_soap.find(class_='single-article__title entry-title')
						print('article title: ' + art_title.text)
							
						# 記事の小カテゴリ
						small_category = art_soap.find(class_='ranking__title')
						print('Small_category : ' + re.sub(u'人気ランキング', '', small_category.text))


						# 監修者がいれば、監修者の専門と名前を取得
						supervisior_position = art_soap.find(class_='supervisor-profile__position')
						if supervisior_position is not None:
							print('supervisior position : ' + supervisior_position.text)
						supervisior_name = art_soap.find(class_='supervisor-profile__name')
						if supervisior_name is not None:
							print('supervisior name : ' + supervisior_name.text)

						
						# 記事内の関連リンク
						for related_link in art_soap.find_all(class_='related__link'):
							print('related link : ' + related_link.text)
							# print('related link : ' + related_link.get('href'))

						# 参考記事
						for reference_link in art_soap.find_all(class_='reference__link'):
							print('reference link : ' + reference_link.text)
							# print('reference link : ' + reference_link.get('href'))
							
							
						# 関連キーワード
						related_kws = art_soap.find(class_="related-tags")
						for related_kw in related_kws.select('ul > li'):
							print('related kw : ' + related_kw.text)
							
						break
				break
			break
		break
	break
print('end')
