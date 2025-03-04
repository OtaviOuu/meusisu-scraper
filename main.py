import nodriver as uc
import aiofiles
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
import os
from pathlib import Path
import asyncio
from parsel.selector import Selector


keyboard = KeyboardController()
mouse = MouseController()

start_url = "https://meusisu.com"

# garbage
# 🔪 rpc


async def get_header(page: uc.Tab):
    b = await page.select(".-m01n")
    header_html = await b.get_html()
    doc = Selector(text=header_html)
    for svg in doc.css("svg"):
        svg.drop()
    return doc.get()


async def save_table(path, table_html, banner):
    final_table = "".join(table_html)

    rows = []
    doc = Selector(text=final_table)
    for row in doc.css(".MuiTableRow-root.AhZ0K.css-1rz7w7v"):
        rows.append(row.get())

    os.makedirs(path, exist_ok=True)
    async with aiofiles.open(f"{path}/table.html", "w") as f:
        await f.write(f"<div>{banner}</div><table>" + "".join(rows) + "</table>")


async def scrape(browser: uc.Browser):
    page = await browser.get(start_url)
    for course_id in range(1, 8395):
        await page.get(f"{start_url}/curso/{course_id}")
        await page.wait(t=0.07)

        course_name = await page.select(".-m01n .Nnvgc")
        course_name = course_name.text

        years_of_result_table = await page.select_all(".B2sMx")

        banner = await get_header(page)
        for section in years_of_result_table:
            table_year = section.text
            table_pages_btns = await section.query_selector_all(".ZxzaA li button")

            last_result_index = table_pages_btns[-2].text
            goto_next_index_btn = table_pages_btns[-1]

            final_table = []
            for table_frame_index in range(1, int(last_result_index)):
                table_frame = await section.query_selector(".MuiTable-root.css-qrs5bp")
                table_frame_html = await table_frame.get_html()
                final_table.append(table_frame_html)
                await goto_next_index_btn.click()
            path = Path(f"./results/{course_id}-{course_name}/{table_year}")
            await save_table(
                path=path,
                table_html=final_table,
                banner=banner,
            )
            await section.flash()


async def main():
    browser = await uc.start()
    await scrape(browser)


if __name__ == "__main__":
    asyncio.run(main())
