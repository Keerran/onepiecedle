import scrapy


class HakiSpider(scrapy.Spider):
    name = "haki"
    allowed_domains = ["onepiece.fandom.com"]
    start_urls = [
        "https://onepiece.fandom.com/wiki/Haki/Haoshoku_Haki",
        "https://onepiece.fandom.com/wiki/Haki/Kenbunshoku_Haki",
        "https://onepiece.fandom.com/wiki/Haki/Busoshoku_Haki",
    ]

    def parse(self, response: scrapy.http.Response):
        yield {
            "type": response.url.split("/")[-1].split("_")[0],
            "users": response.xpath("""
                .//h2[span[re:test(@id, '_Haki_Users$')]]
                /following-sibling::table[1]
            """).xpath("""
                set:difference(
                    .//td/a[not(.//sup[@title='Non-Canon'])],
                    ./tbody/tr[.//span[contains(., 'Non-Canon')]]
                    /following-sibling::tr//a
                )/@title
            """).getall()
        }
