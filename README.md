## Usage

A short tour through the workflow:

 - `decode-export-string.py` converts a import/export string into plain JSON:
```
      python decode-export-string.py < tests\win\bp.txt > tests\win\json.txt
      python decode-export-string.py --indent=8 --separator1=", " --separator2=": " < tests\win\bp.txt
```
 - `encode-export-string.py` converts JSON into a packed import/export string:
```
      python encode-export-string.py < tests\win\json.txt > tests\win\export.txt
      python encode-export-string.py < tests\win\json.txt
```
 - That import/export string can be read back into Factorio using the command
"import string".

[Python]: https://www.python.org/
