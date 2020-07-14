# expense_split
A web-based tool to parse through bills, lanch split web interface and compute the expense.
A handy tool I use to split the bill before adding expense in splitwise.

Data model: bill.pdf -> parse_bill.py -> parsed.txt -> web_interface.py -> split.txt -> parse_bill.py -> Desired output.
In case, you are creating the parsed.txt by yourself, then below is the format.
```Python
[[Item1, 2.5], [Item2, 20], [Item3, 100.50], ...]
```