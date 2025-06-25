from sitemap_utils import fetch_all_urls,fetch_all_urls_ex_xlsx

def main():
    # Chỉ cần khai báo domain ở đây:
    domain = "https://cliniphy.com"
    output_file = 'sitemap_structure_cliniphy.xlsx'
    df = fetch_all_urls_ex_xlsx(domain)
    df.to_excel(output_file, index=False)
    print(f"Hoàn tất! File Excel đã được lưu: {output_file}")
    # fetch_all_urls(domain)

if __name__ == "__main__":
    main()
