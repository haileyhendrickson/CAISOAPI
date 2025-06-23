import pandas as pd
df = pd.read_excel('HASP 06-18-2025 1102.xlsx')
max5 = sorted(df['LMP'], reverse = True)[:5]
print(max5)

min5 = sorted(df['LMP'], reverse = False)[:5]
print(min5)

top5col = df.sort_values(by='LMP', ascending=False).head(5) # prints top 5 rows based on LMP
min5col = df.sort_values(by='LMP', ascending=True).head(5) # bottom 5 rows based on LMP
print(top5col)
print(min5col)