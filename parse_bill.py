from PyPDF2 import PdfFileReader
import re
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument parser')
    parser.add_argument('--input', type=str, default='bill.pdf',
                        help='receipt pdf file path')
    parser.add_argument('--output', type=str, default='parsed.txt',
                        help='output file name')
    args = parser.parse_args()
    return args

def get_text(pdf_file, page_numbers):
    """Parses the pdf content

    Args:
        pdf_file (str): file name
        page_number (int): page number

    Returns:
        str: Raw string parsed from the pdf page
    """
    with open(pdf_file, 'rb') as f:
        pdfReader = PdfFileReader(f)
        pageObj = pdfReader.getPage(page_numbers[0])
        page_content = pageObj.extractText()
    return page_content

def sanitize(string):
    """Sanitizes the string

    Args:
        string (str): input string

    Returns:
        str: sanitized string
    """
    sanitized = string.replace('"', '').replace("'", "")
    return sanitized

def parse_receipt(data):
    """Applies regex pattern to parse item and price

    Args:
        data (str): Sanitized string
    
    Returns:
        List: A list of item name and it's price
    """
    pattern = "(([\d])+(\.[\d]+\slb)?\s{1}X\s{1}\$([\d]+\.[\d]+)(\(Refunded\)\s)?(\$[\d]+\.[\d]+))"
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
    args = parse_arguments()
    pdf_file = args.input
    content_page1 = get_text(pdf_file, page_numbers=[1])
    items1 = parse_receipt(content_page1)
    content_page2 = get_text(pdf_file, page_numbers=[2])
    items2 = parse_receipt(content_page2)
    #print(items1)
    #print(items2)
    total_items = items1 + items2
    with open(args.output, "w") as file:
        file.write(str(total_items))

if __name__ == "__main__":
    main()