import sys, openpyxl
sys.stdout.reconfigure(encoding='utf-8')
wb = openpyxl.load_workbook(r'E:\workspace\github\film-tvs\res\data_new.xlsx')
ws = wb['动漫资源']
cleared = 0
for r in range(182, 217):
    v = ws.cell(r, 4).value
    if v and str(v).strip():
        title = ws.cell(r, 3).value
        print(f'  Row {r} {title}: 副标题 "{v}" -> empty')
        ws.cell(r, 4).value = ''
        cleared += 1
wb.save(r'E:\workspace\github\film-tvs\res\data_new.xlsx')
print(f'Cleared {cleared} 副标题 values')
