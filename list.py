import csv
def remove_duplicates(text_file):
    with open(text_file, "r") as file:
        lines = file.readlines()

    unique_lines = list(dict.fromkeys(lines))

    with open(text_file, "w") as file:
        file.writelines(unique_lines)

def failed_urls():
    existing_urls_combined = set()
    with open("txt/links.txt", "r") as file:
        for line in file:
            existing_urls_combined.add(line.strip())
    # Read existing URLs from failed_at_2.txt
    existing_urls_failed = set()
    with open("txt/failed_at_2.txt", "r") as file:
        for line in file:
            existing_urls_failed.add(line.strip())
    with open("txt/failed_at_1.txt", "r") as file:
        for line in file:
            existing_urls_failed.add(line.strip())
    with open('douban.csv', mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            existing_urls_failed.add(row['URL'])
    urls_to_keep = existing_urls_combined - existing_urls_failed

    with open("txt/links.txt", "w") as file:
        for link in urls_to_keep:
            file.write(f"{link}\n")


if __name__ == '__main__':
    file_to_clean = ["txt/links.txt", "txt/failed_at_2.txt", "txt/failed_at_1.txt", "txt/302.txt","txt/douList.txt"]
    for file in file_to_clean:
        remove_duplicates(file)
        print(f"{file} cleaned successfully.")
    failed_urls()