import scrapy
import re


class CharInfoSpider(scrapy.Spider):
    name = "char_info"
    allowed_domains = ["onepiece.fandom.com"]
    start_urls = ["https://onepiece.fandom.com/wiki/List_of_Canon_Characters"]

    def parse(self, response):
        selector = "table:first-of-type td:nth-of-type(2) a::attr(href)"
        for href in response.css(selector):
            yield response.follow(href, callback=self.parse_char)

    def parse_char(self, response: scrapy.http.Response):
        def extract(query: str):
            return re.sub(r"\[\d+\]", "", "".join(response.css(query).getall()).strip())

        def extract_aside(source: str, subquery=" div"):
            return extract(f'aside [data-source="{source}"]{subquery} *::text')

        yield {
            "name": extract_aside("name", subquery=""),
            "debut": self.parse_debut(extract_aside("first")),
            "affiliation": self.parse_affiliations(extract_aside("affiliation")),
            "origin": re.sub(r"\(.+\)", "", extract_aside("origin")),
            "aliases": self.parse_aliases(extract_aside("alias")) + self.parse_aliases(extract_aside("epithet")),
            "height": self.parse_height(extract_aside("height")),
            "bounty": self.parse_bounty(extract_aside("bounty")),
            "dfname": extract_aside("dfname"),
            "dftype": extract_aside("dftype").split(" ")[-1],
        }

    def parse_debut(self, text: str):
        chapter = re.search(r"Chapter (\d+)", text)
        if chapter is not None:
            chapter = int(chapter.group(1))
        episode = re.search(r"Episode (\d+)", text)
        if episode is not None:
            episode = int(episode.group(1))

        return {
            "chapter": chapter,
            "episode": episode,
        }

    def parse_affiliations(self, text: str):
        affiliations = [
            affiliation.strip()
            for affiliation in text.split(";")
            if "(" not in affiliation
        ]
        return affiliations[0] if len(affiliations) > 0 else None

    def parse_aliases(self, text: str):
        return [re.sub(r"\(.*\)", "", alias).strip().strip('"') for alias in text.split(";") if alias]

    def parse_height(self, text: str):
        try:
            return int(re.search(r"(?s:.*)(\d+) ?cm", text).group(1))
        except AttributeError:
            return None

    def parse_bounty(self, text: str):
        try:
            return int(re.search(r"([\d,]+)", text).group(1).replace(",", ""))
        except AttributeError:
            return 0
