from bs4 import BeautifulSoup

from src.article import Article


class Parser:
    @staticmethod
    def parse_feed(html):
        """
        Performs search of the articles on the feed page
        :param html:
        :return: map (url) -> (headline)
        """
        root_url = "https://kommersant.ru/"
        soup = BeautifulSoup(html, "html.parser")

        # 1. find div.rubric_lenta which contains news items
        selector = "body > main > div > div > section:nth-child(1) > div.grid-col.grid-col-s3 > div.rubric_lenta"
        rubric_lenta_items = soup.select(selector)
        article_search_result = dict()

        # 2. in each rubric_lenta select all news items:
        for item in rubric_lenta_items:
            article_tag = item.select("article")
            if len(article_tag) > 0:
                article_tag = article_tag[0]

                # Headline
                headline = article_tag.get("data-article-title")

                # Link to the article's full page
                link = article_tag.select("a.uho__link")[0].get("href")
                article_search_result[root_url + link] = headline
        return article_search_result


    @staticmethod
    def parse_article(html):
        soup = BeautifulSoup(html, "html.parser")
        result = Article()
        articles = soup.select("div.lenta_top_doc > article")
        if len(articles) == 0:
            print("Couldn't find selector: div.lenta_top_doc > article")
            return None

        result.headline = articles[0].get("data-article-title")
        result.topic = articles[0].get("data-article-rubric-name")
        article_body = articles[0].select("div.doc__body")
        if len(article_body) == 0:
            result.parsing_errors.append("Couldn't find element: div.doc__body")

        text_elements = article_body[0].select("p.doc__text")
        for t in text_elements:
            result.text += t.text + "\n"
        return result





