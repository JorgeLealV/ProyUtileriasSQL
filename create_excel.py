import pandas as pd

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter('DatosCatalogosOriginales.xlsx', engine='xlsxwriter')

# Create some dummy dataframes
df1 = pd.DataFrame({'Data': [10, 20, 30, 40]})
df2 = pd.DataFrame({'Data': [11, 22, 33, 44]})
df3 = pd.DataFrame({'Data': [12, 23, 34, 45]})
df4 = pd.DataFrame({'Data': [13, 24, 35, 46]})
df5 = pd.DataFrame({'Data': [14, 25, 36, 47]})

# Write each dataframe to a different worksheet.
df1.to_excel(writer, sheet_name='Tabla1', index=False)
df2.to_excel(writer, sheet_name='Tabla2', index=False)
df3.to_excel(writer, sheet_name='Hoja1', index=False)
df4.to_excel(writer, sheet_name='Hoja2', index=False)
df5.to_excel(writer, sheet_name='Tabla3', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.close()
