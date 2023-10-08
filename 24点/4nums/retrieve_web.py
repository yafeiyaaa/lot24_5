import requests
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://www.4nums.com/game/difficulties/'  # 网站代码
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser') # 获得源代码



# 假设表格是通过<table>标签定义的，你可以根据实际情况修改这里的选择器
table = soup.find('table')

# 获取表格中的所有行
rows = table.find_all('tr')

# 将表格的每一行转换为DataFrame的行
data = [[td.text for td in row.find_all('td')]  for row in rows]

# 创建DataFrame对
df = pd.DataFrame(data[1:],columns=data[0])
num_list = [nums_string.split() for nums_string in df["Puzzles "]]
num_list = [[int(num) for num in nums] for nums in num_list]
df["nums"] = num_list

# 打印DataFrame
#print(df)


# 假设你已经有一个名为df的DataFrame对象

# 将DataFrame转换为CSV文件
df.to_csv('./4nums/4nums.csv', index=False)

# 绘制解答的概率密度函数
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

Solved_rate = df["Solved rate   "]

# 计算核密度估计
Solved_rate_density = gaussian_kde(Solved_rate)

# 生成一维横坐标范围
x = np.linspace(0,1, 100)

# 绘制概率密度函数
plt.plot(x, Solved_rate_density(x))
plt.xlabel('Value')
plt.ylabel('Probability Density')
plt.title('Probability Density Function')
plt.show()




