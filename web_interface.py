
import webbrowser
import subprocess

from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi, cgitb

def generate_html_header(title):
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
    footer = """
    </body>
    </html>
    """
    return footer

def generate_item_template(item, users):
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
    users = ['V', 'K', 'M', 'S']
    html_code = generate_html_header("test")
    html_code += '<form method="post" enctype="multipart/form-data">'
    for item in item_list:
        html_code += generate_item_template(item, users)
    html_code += '<input type="submit" value="Update">'
    html_code += '</form>'
    html_code += get_html_footer()
    return html_code

def cfloat(frac_str):
    frac_str = frac_str.decode('utf-8')
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

def parse_request(fields, old_item_list, users):
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
                print("Total value does not match")
        updated_item_list.append(updated_item)
    return updated_item_list

def start_server(html_code, item_list, users):
    host_url = "http://127.0.0.1:7000"
    webbrowser.open(host_url)
    # Kill the already running process on localhost
    subprocess.call(['fuser', '-k', '7000/tcp'])
    class server_request_handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            content_type = 'text/html'
            self.send_header('content-type', content_type)
            self.end_headers()
            self.wfile.write(bytes(html_code, encoding='utf'))
            return

        def do_POST(self):
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            content_len = int(self.headers.get('content-length'))
            pdict['CONTENT-LENGHT'] = content_len
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                #print(fields)
                updated_item_list = parse_request(fields, item_list, users)
                #print(updated_item_list)
                with open("split.txt", "w") as f:
                    f.write(str(updated_item_list))
            self.send_response(301)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("Close this window now", encoding='utf'))
    server = HTTPServer(('', 7000), server_request_handler)
    server.serve_forever()


if __name__ == "__main__":
    item_list = None
    with open("parsed.txt", "r") as file:
        item_list = eval(file.readline())
    user_list = ['V', 'K', 'M', 'S']
    start_server(generate_html_code(item_list, user_list), item_list, user_list)
