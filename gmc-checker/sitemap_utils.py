import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_sitemap_url(domain: str) -> str:
    """
    Truy cập domain/robots.txt, đọc và trả về URL sitemap (dòng bắt đầu bằng 'Sitemap:')
    """
    robots_url = domain.rstrip('/') + '/robots.txt'
    resp = requests.get(robots_url)
    resp.raise_for_status()
    for line in resp.text.splitlines():
        if line.lower().startswith('sitemap:'):
            return line.split(':', 1)[1].strip()
    raise ValueError(f"Không tìm thấy Sitemap trong {robots_url}")

def get_main_sections(sitemap_url: str) -> list[str]:
    """
    Truy cập sitemap_url (HTML), lấy tất cả <a> không có class và trả về list các href
    """
    resp = requests.get(sitemap_url)
    resp.raise_for_status()
    # Đảm bảo đã pip install lxml để parser XML chính xác
    soup = BeautifulSoup(resp.content, 'xml')
    return [loc.text.strip() for loc in soup.find_all('loc')]

def get_subsection_links(section_url: str) -> list[str]:
    """
    Truy cập từng section_url, lấy các <a> không có class và trả về list các href con
    """
    resp = requests.get(section_url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'xml')
    return [loc.text.strip() for loc in soup.find_all('loc')]

def fetch_all_urls(domain: str):
    """
    Gọi lần lượt các bước:
     1) tìm sitemap URL
     2) lấy list các mục lớn
     3) với mỗi mục lớn, lấy list các mục con
    Và in ra kết quả ngay trong hàm này.
    """
    try:
        sitemap_url = get_sitemap_url(domain)
        print(f"Sitemap URL: {sitemap_url}\n")

        main_sections = get_main_sections(sitemap_url)
        print("=== Các mục lớn trong sitemap ===" )
        for idx, sec in enumerate(main_sections, 1):
            print(f"{idx}. {sec}")
        print()

        print("=== Các mục con (subsections) ===")
        for sec in main_sections:
            subs = get_subsection_links(sec)
            print(f"\nSubsections của {sec}:")
            for s in subs:
                print(f"  - {s}")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


def fetch_all_urls_ex_xlsx(domain: str) -> pd.DataFrame:
    """
    Trả về DataFrame với 3 cột:
      - link_site_map: chỉ xuất ở ô đầu tiên,
      - link_cha: xuất ở mỗi lần bắt đầu sitemap con mới,
      - link_con: cho từng URL con.
    """
    sitemap_index = get_sitemap_url(domain)
    main_sitemaps = get_main_sections(sitemap_index)

    rows = []
    first_row = True
    for sm in main_sitemaps:
        children = get_subsection_links(sm)
        for i, child in enumerate(children):
            if first_row and i == 0:
                rows.append({
                    'link_site_map': sitemap_index,
                    'link_cha': sm,
                    'link_con': child
                })
                first_row = False
            else:
                rows.append({
                    'link_site_map': '' if not (first_row and i==0) else sitemap_index,
                    'link_cha': sm if i == 0 else '',
                    'link_con': child
                })

    df = pd.DataFrame(rows, columns=['link_site_map','link_cha','link_con'])
    return df
