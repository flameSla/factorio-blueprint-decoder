python decode-export-string.py < tests\win\bp.txt | python encode-export-string.py > tests\win\new_bp.txt
python decode-export-string.py < tests\win\bp.txt > tests\win\json.txt
python encode-export-string.py < tests\win\json.txt > tests\win\export.txt
fc /b tests\win\bp.txt tests\win\new_bp.txt
pause