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
            return "".join(response.xpath(f"""
                set:difference(
                    {query},
                    //sup//text() | //s//text()
                )
            """).getall()).strip()

        def extract_aside(source: str, subquery="//div"):
            return extract(f'//aside//*[@data-source="{source}"]{subquery}//text()')

        def has_category(category: str):
            return response.css(".page-header__categories").xpath(f"""
                .//a[
                    translate(@href,
                        'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                        'abcdefghijklmnopqrstuvwxyz'
                    ) = "/wiki/category:{category.lower()}"
                ]
            """)

        def has_categories(categories: list[str]):
            for category in categories:
                if has_category(category):
                    return True
            return False

        name = extract_aside("name", subquery="")
        male = has_category("Male_characters")
        female = has_categories([
            "Female_characters",
            "Kuja_Pirates",
            "Queens",
            "Princesses",
            "Former_Princesses",
            "Gorgon_Sisters",
            "Kunoichi"
        ])
        if not name:
            return
        yield {
            "name": name,
            "gender": male and "Male" or female and "Female" or None,
            **self.parse_debut(extract_aside("first")),
            "affiliation": self.parse_affiliations(extract_aside("affiliation")),
            "origin": re.sub(r"\(.+\)", "", extract_aside("origin")),
            "aliases": self.parse_aliases(extract_aside("alias")) + self.parse_aliases(extract_aside("epithet")),
            "height": self.parse_height(extract_aside("height")),
            "bounty": self.parse_bounty(extract_aside("bounty")),
            "dfname": extract_aside("dfname"),
            "dftype": extract_aside("dftype").split(" ")[-1].strip("()"),
        }

    def parse_debut(self, text: str):
        chapter = re.search(r"Chapter (\d+)", text)
        if chapter is not None:
            chapter = int(chapter.group(1))
        episode = re.search(r"Episode (\d+)", text)
        if episode is not None:
            episode = int(episode.group(1))

        return {
            "anime_debut": chapter,
            "manga_debut": episode,
        }

    def parse_affiliations(self, text: str):
        affiliations = [
            affiliation.strip()
            for affiliation in text.split(";")
            if re.match(r"\bformer\b", affiliation) is None
        ]
        return affiliations[0] if len(affiliations) > 0 else None

    def parse_aliases(self, text: str):
        return [stripped for alias in text.split(";") if (stripped := re.sub(r"\(.*\)", "", alias).strip().strip('"'))]

    def parse_height(self, text: str):
        try:
            return int(re.findall(r"(\d+) ?cm", text)[-1])
        except IndexError:
            return None

    def parse_bounty(self, text: str):
        try:
            return int(re.search(r"^([\d,]+)", text).group(1).replace(",", ""))
        except AttributeError:
            return 0
