import pandas as pd

crm = pd.read_csv('data/raw/crm.csv', encoding='utf-8-sig')
erp = pd.read_csv('data/raw/erp.csv', encoding='utf-8-sig')
bank = pd.read_csv('data/raw/bank_statements.csv', encoding='utf-8-sig')
ext = pd.read_csv('data/raw/external_data.csv', encoding='utf-8-sig')

print("=== CLIENTES POR SECTOR ===")
print(crm['sector'].value_counts().to_string())
print()

print("=== ESTADOS CRM ===")
print(crm['estado'].value_counts().to_string())
print()

print("=== CATEGORIAS ERP ===")
print(erp['categoria'].value_counts(dropna=False).to_string())
print()

print("=== SALDO BANCO ===")
print(f"Minimo: {bank['saldo_acumulado'].min():,.2f} EUR")
print(f"Maximo: {bank['saldo_acumulado'].max():,.2f} EUR")
print(f"Final:  {bank['saldo_acumulado'].iloc[-1]:,.2f} EUR")
print()

print("=== EXTERNAL ===")
print(ext.head(3).to_string())
print()

print("=== VERIFICACION: Los 4 archivos existen y son validos ===")
for name, df in [("CRM", crm), ("ERP", erp), ("Bank", bank), ("External", ext)]:
    print(f"  {name}: {len(df)} filas, {len(df.columns)} columnas")
