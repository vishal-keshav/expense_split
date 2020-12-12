
import webbrowser
import subprocess

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi, cgitb

import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument parser')
    parser.add_argument('--input', type=str, default='parsed.txt',
                        help='receipt pdf file path')
    parser.add_argument('--participant', type=str, nargs='+',
                        default=['V', 'K', 'M', 'S'],
                        help='split participants')
    parser.add_argument('--output', type=str, default='split.txt',
                        help='output file name')
    args = parser.parse_args()
    return args

args = parse_arguments()

def generate_html_header(title):
    """Generates html code for header

    Args:
        title (str): Title of the page.

    Returns:
        str: HTML header code as string.
    """
    header = """
    <!DOCTYPE html>
    <html>
    <head>
    <title>{}</title>
    </head>
    <body>
    """.format(title)
    return header


def get_html_footer():
    """Generates html code for footer

    Returns:
        str: HTML footer code as string.
    """
    footer = """
    </body>
    </html>
    """
    return footer

def generate_item_template(item, users):
    """Generates HTML code for the item and participant for the html body

    Args:
        item (List[str]): A list of item names
        users (List[str]): A list of user participants
    
    Returns:
        str: HTML code to generate parts of the body.
    """
    user_template = """
    {0} 
    <input type="checkbox" id="{1}:{2}:cb", name="{1}:{2}:cb", value={3}>
    <input type="text" id="{1}:{2}:tf" name="{1}:{2}:tf" size="2", value={4}>
    """
    template = """
    {} : {} <br>
    """.format(item[0], item[1])
    for u in users:
        template += user_template.format(u, item[0], u, "on", "")
    template += "<br><br>"
    return template


def generate_html_code(item_list, users):
    """Generates complete HTML code to render web page

    Args:
        item_list (List[str]): List of item names
        users (List[str]): List of participant names
    
    Returns:
        str: Returns the string constaiing HTML code.
    """
    html_code = generate_html_header("expense-split-web-interface")
    html_code += '<form method="post" enctype="multipart/form-data">'
    for item in item_list:
        html_code += generate_item_template(item, users)
    html_code += '<input type="submit" value="Update">'
    html_code += '</form>'
    html_code += get_html_footer()
    return html_code

def cfloat(frac_str):
    """Decodes a string having fractional value and returns float

    Args:
        frac_str (str): String containing the representation of fractional num
    
    Returns:
        float: floating point representation of fraction
    """
    #frac_str = frac_str.decode('utf-8')
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac

class ValueMismatch(Exception):
    pass

def parse_request(fields, old_item_list, users):
    """Parses the POST requests into python data structure.
    The field is a disctionary of POST request, with each element has a
    format like '<item name>:<User>:<tf?cb?>': ['<tf value, cb value or blank>']

    Args:
        fields (Dict[Post filed: List[str data]]): Constains POST data.
        old_item_list (List[str]): Original item list
        users (List[str]): List of participating users
    
    Returns:
        List[List[str, float, dict]]: Parsed items with expenses.

    """
    updated_item_list = []
    for item in old_item_list:
        updated_item = None
        item_name, item_value = item[0], item[1]
        item_partcipation = []
        for user in users:
            if item_name + ":" + user + ":" + "cb" in fields:
                item_partcipation.append(user)
        item_expense_distribution = {}
        for user in users:
            if len(fields[item_name + ":" + user + ":" + "tf"][0]) != 0:
                item_expense_distribution[user] = \
                    cfloat(fields[item_name + ":" + user + ":" + "tf"][0])
        if len(item_expense_distribution) == 0: # Equal distribution
            expense = {}
            for e in item_partcipation:
                expense[e] = float(item_value)/float(len(item_partcipation))
            updated_item = [item_name, item_value, expense]
        else:
            # Check if fraction is provided
            total_sum = sum(
                [item_expense_distribution[k] \
                    for k in item_expense_distribution])
            if abs(total_sum- 1.0) <= 0.01:
                expense = {}
                for k in item_expense_distribution:
                    expense[k] = item_expense_distribution[k]*item_value
                updated_item = [item_name, item_value, expense]
            elif abs(total_sum - item_value) <= 0.01:
                expense = {}
                for k in item_expense_distribution:
                    expense[k] = item_expense_distribution[k]
                updated_item = [item_name, item_value, expense]
            else:
                raise ValueMismatch("Total value does not match")
        updated_item_list.append(updated_item)
    return updated_item_list

def start_server(html_code, item_list, users):
    """Starts the server, opens the browser, render the html page

    Args:
        html_code (string): HTML code that needs to be rendered on web-page.
        item_list (List[str]): A list of item names.
        users (List[str]): List of participant names.
    """
    host_url = "http://127.0.0.1:7000"
    webbrowser.open(host_url)
    # Kill the already running process on localhost
    try:
        subprocess.call(['fuser', '-k', '7000/tcp'])
    except:
        print("Not using Ubuntu?")
    class server_request_handler(BaseHTTPRequestHandler):
        """HTTP Request handler class
        """
        def do_GET(self):
            """Response to GET command.
            Sets the content type to be sent to client.
            """
            self.send_response(200)
            content_type = 'text/html'
            self.send_header('content-type', content_type)
            self.end_headers()
            self.wfile.write(bytes(html_code, encoding='utf'))
            return

        def do_POST(self):
            """Response to POST commands
            Parses the client request, including the check box and text field.
            """
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            content_len = int(self.headers.get('content-length'))
            pdict['CONTENT-LENGHT'] = content_len
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                updated_item_list = parse_request(fields, item_list, users)
                with open(args.output, "w") as f:
                    f.write(str(updated_item_list))
            self.send_response(301)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("Close this window now", encoding='utf'))
    server = HTTPServer(('', 7000), server_request_handler)
    server.serve_forever()


if __name__ == "__main__":
    item_list = None
    with open(args.input, "r") as file:
        item_list = eval(file.readline())
    user_list = args.participant
    start_server(generate_html_code(item_list, user_list), item_list, user_list)
