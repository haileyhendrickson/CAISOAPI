import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('pull#0.csv')

# df['MW'].hist()
# plt.show() # shows distribution of MW prices

cross_tab = pd.crosstab(df['MW'], df['INTERVALSTARTTIME_GMT'])

# Convert to a numpy array for plotting
data = cross_tab.values

# Plot the heatmap
plt.imshow(data, cmap='viridis')
plt.colorbar(label='Count')
plt.xticks(np.arange(len(cross_tab.columns)), cross_tab.columns)
plt.yticks(np.arange(len(cross_tab.index)), cross_tab.index)
plt.xlabel('Date')
plt.ylabel('MW')
plt.title('Cross-Tabulation Heatmap')
plt.show()