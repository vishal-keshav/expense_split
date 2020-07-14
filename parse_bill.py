from PyPDF2 import PdfFileReader, PdfFileWriter
import re

def get_text(pdf_file, page_numbers):
    with open(pdf_file, 'rb') as f:
        pdfReader = PdfFileReader(f)
        pageObj = pdfReader.getPage(page_numbers[0])
        page_content = pageObj.extractText()
    return page_content

def sanitize(string):
    sanitized = string.replace('"', '').replace("'", "")
    return sanitized

def parse_receipt(data):
    pattern = "(([\d])+(\.[\d]+\slb)?\s{1}X\s{1}\$([\d]+\.[\d]+)(\(Refunded\)\s)?(\$[\d]+\.[\d]+))"
    #pattern = r'Refunded'
    regex = re.compile(pattern, re.IGNORECASE)
    splitted_list = regex.split(data)
    item_list = []
    for i in range(0, len(splitted_list), 7):
        try:
            item_name = sanitize(" ".join(splitted_list[i].split()))
            item_price = splitted_list[i+6][1:]
            item_list.append([item_name, float(item_price)])
        except Exception as e:
            print("Could not process " + " ".join(splitted_list[i].split()))
    return item_list

def main():
    pdf_file = 'bill.pdf'
    content_page1 = get_text(pdf_file, page_numbers=[1])
    items1 = parse_receipt(content_page1)
    content_page2 = get_text(pdf_file, page_numbers=[2])
    items2 = parse_receipt(content_page2)
    #print(items1)
    #print(items2)
    total_items = items1 + items2
    with open("parsed.txt", "w") as file:
        file.write(str(total_items))

if __name__ == "__main__":
    main()