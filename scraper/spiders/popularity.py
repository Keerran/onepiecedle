import scrapy
import re
import json


class PopularitySpider(scrapy.Spider):
    name = "popularity"
    allowed_domains = ["onepiece.fandom.com"]
    start_urls = ["https://onepiece.fandom.com/wiki/Popularity_Polls"]

    def parse(self, response):
        rows = response.xpath("//h3[span[@id='Results_Table']]/following-sibling::div[1]//table/tbody/tr")
        rows = [["".join(cell.xpath(".//text()").getall()).strip() for cell in row.xpath(".//td")] for row in rows]

        popularity = {}
        for row in rows:
            if not row:
                continue
            [name, *votes] = row
            votes = [int(match[-1]) for vote in votes if (match := re.findall(r"^\d+|(?<=\()\d+(?=\))", vote))]
            popularity[name] = max(votes)

        with open("../popularity.json", "w", encoding="utf-8") as f:
            json.dump(dict(sorted(popularity.items(), key=lambda item: -item[1])), f, indent=4, ensure_ascii=False)
