# 2025秋音乐与数学期中研究作业
## 环境配置


python版本3.12

安装依赖：
```shell
pip install -r requirements.txt
```

也可以使用适当的包管理器

## 运行

```shell
python main.py
```

## 一些超参

```python
generations = 50      # 进化的代数 
initial_size = 20     # 初始种群数 
threshold = 200       # 适应度的threshold
population_size=50    # 每次种群进化产生的子代数目
crossover_rate=0.7    # 交换概率
mutation_rate=0.1     # 变异概率
transpose_rate=0.1    # 移调概率
inversion_rate=0.1    # 倒影概率
retrograde_rate=0.1   # 逆行变换概率

fitness_function的设计
```

此外还有一些细节的比如移调偏移量，倒影中心的位置都是可以改的

~~这些我现在都是瞎写的~~

## TODO

调参？
看看代码有没有错误？
**<span style="color : red"> fitness_function的设计</span>**