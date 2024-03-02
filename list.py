def remove_dups():
    with open('links.txt', 'r') as file:
        list1_lines = file.readlines()

    # Open and read the contents of list2.txt
    with open('links2.txt', 'r') as file:
        list2_lines = file.readlines()

    combined_lines = list1_lines + list2_lines

    # Remove duplicates by converting to a set
    unique_lines = set(combined_lines)

    # Write the unique lines to a new file (combined.txt)
    with open('combined.txt', 'w') as file:
        file.writelines(unique_lines)


import csv
def remove_duplicates(text_file):
    with open(text_file, "r") as file:
        lines = file.readlines()

    # Remove duplicates while preserving order
    unique_lines = list(dict.fromkeys(lines))

    # Open the file in write mode and overwrite with unique links
    with open(text_file, "w") as file:
        file.writelines(unique_lines)
def combined_csv():
    def extract_urls_from_csv(filename):
        urls = set()
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                urls.add(row['URL'])
        return urls


    # Read combined.txt
    with open('combined.txt', 'r') as file:
        combined_lines = file.readlines()

    # Extract URLs from douban.csv
    douban_urls = extract_urls_from_csv('douban.csv')

    # Remove URLs from combined.txt if they exist in douban.csv
    unique_lines = [line for line in combined_lines if line.strip() not in douban_urls]

    # Write the updated unique lines back to combined.txt
    with open('combined.txt', 'w') as file:
        file.writelines(unique_lines)

def failed_urls():
    existing_urls_combined = set()
    with open("combined.txt", "r") as file:
        for line in file:
            existing_urls_combined.add(line.strip())

    # Read existing URLs from failed_at_2.txt
    existing_urls_failed = set()
    with open("failed_at_2.txt", "r") as file:
        for line in file:
            existing_urls_failed.add(line.strip())
    with open("failed_at_1.txt", "r") as file:
        for line in file:
            existing_urls_failed.add(line.strip())

    # Remove URLs present in failed_at_2.txt from combined.txt
    urls_to_keep = existing_urls_combined - existing_urls_failed

    # Write remaining URLs to combined.txt
    with open("combined.txt", "w") as file:
        for link in urls_to_keep:
            file.write(f"{link}\n")


if __name__ == '__main__':
    file_to_clean = ["links.txt", "links2.txt", "combined.txt", "failed_at_2.txt", "failed_at_1.txt", "302.txt","douList.txt"]
    for file in file_to_clean:
        remove_duplicates(file)
        print(f"{file} cleaned successfully.")
    remove_dups()
    combined_csv()
    failed_urls()