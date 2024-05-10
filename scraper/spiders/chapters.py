import scrapy


class ChaptersSpider(scrapy.Spider):
    name = "chapters"
    allowed_domains = ["onepiece.fandom.com"]
    start_urls = ["https://onepiece.fandom.com/wiki/Chapter_1"]

    def parse(self, response):
        characters = response.css("table.CharTable")\
                             .xpath(".//td//li//a/@title").getall()
        yield {"characters": characters}

        next_chapter = response.xpath("""
            //aside//caption[. = "Chapter Chronology"]/following-sibling::tbody/tr/td[2]/a/@href
        """).get()
        if next_chapter:
            yield response.follow(next_chapter, self.parse)
