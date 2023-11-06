# FormularEdit
A Formula Editor Based on PyQt5. <br />
Language Support: Chinese, English. <br />
Libraries of Extension:by [@JungGyuYoon](https://github.com/yjg30737). <br />
```
## 5 basic libs ##
absresgetter
pyqt_svg_label
pyqt_svg_button
pyqt_resource_helper
pyqt_svg_abstractbutton
```
```
## 3 applied libs ##
qt_sass_theme
pyqt_hidable_menubar
pyqt_instant_search_bar
```
Packed Source on [PanBaidu](https://pan.baidu.com/s/1g7giPjlMIgHcuYsfVHCDow).(key: m89e) <br />
For instructions, please click "Document Options" in the "Help" menu bar.<br />
Any good suggestions, please contact me at `liskello_o@outlook.com` or `leoliskell@gmail.com`.<br />
**2023.11.1 Update\***: The project is now open source, but copyrighted. Patent Registration number (in China): 2023SR1200770.

# 公式编辑器
一个基于PyQt5的公式编辑器。 <br />
语言支持：简体中文、英文。 <br />
感谢[@JungGyuYoon](https://github.com/yjg30737)自建库的支持： <br />
```
## 5 basic libs ##
absresgetter
pyqt_svg_label
pyqt_svg_button
pyqt_resource_helper
pyqt_svg_abstractbutton
```
```
## 3 applied libs ##
qt_sass_theme
pyqt_hidable_menubar
pyqt_instant_search_bar
```
这是打包文件的[百度网盘链接](https://pan.baidu.com/s/1g7giPjlMIgHcuYsfVHCDow)。(密钥：m89e) <br />
**2023.11.1 更新\***：本项目现已开源，但是具有版权保护。专利登记号（中国）： 2023SR1200770。

# 一份简明的公式编辑器说明书(2022.12.25 Version)
### 一、模块目的
#### 表达式将一方面在Python上可执行，另一方面可转换为LaTex代码展示。
### 二、编辑规则
#### 新变量需在等式左边输入。
### 三、特殊符号
`[]` 自由下角标 例如`x[mn]`: xₘₙ （一般用于希腊字母下标，不可用于变量名） <br />
`_` 限制下角标 例如`x_1`: x₁ （可以开启自由下角标功能，适用于全局） <br />
### 四、一般运算
`+-*/` 加减乘除 <br />
`x//y` 整除 <br />
`x**2` 乘方 <br />
`2e3` 科学计数法 <br />
### 五、一般函数（三角函数、反三角函数、对数函数/圆函数）
fabs()/abs() 绝对值 <br />
sqrt() 根号 <br />
ln()/log2()/log10() 基本对数函数 <br />
### 六、特殊函数
factorial() 阶乘 <br />
floor()/ceil() 向上/下取整 <br />
max(x₁, x₂, x₃ , …)/min(x₁, x₂, x₃ , …) 最大最小函数 <br />
默认输入弧度degree()，角度输入为angle() <br />
### 七、其他函数
prod() 求积 存在问题：括号问题，np只能对数组，需提前引入第三方库math (存疑) <br />
sum() 求和 存在问题：表达式sqrt(sum(x**2 for x in coordinates)) <br />
> 无法以公式显示但合法存在的函数(语句)如下：
>> exp() 自然指数函数 <br />
>v log(x[, base]) 任意底数的对数函数，需提前引入第三方库math <br />
>> gcd(x₁, x₂) 最大公约数 <br />
>> lcm(x₁, x₂) 最小公倍数 <br />
>> np 只能两个或数组形式，需提前引入第三方库math <br />
>> fmod(x, y) 取余数 <br />
>> 其余math, numpy 库中存在的科学计算函数 <br />
### 八、附录
以下为math, numpy 两个库共有的计算函数： <br />
`['ceil', 'copysign', 'cos', 'cosh', 'degrees', 'e', 'exp', 'expm1', 'fabs', 'floor', 'fmod', 'frexp', 'gcd',
'hypot', 'inf', 'isclose', 'isfinite', 'isinf', 'isnan', 'lcm', 'ldexp', 'log', 'log10', 'log1p', 'log2', 'modf',
'nan', 'nextafter', 'pi', 'prod', 'radians', 'remainder', 'sin', 'sinh', 'sqrt', 'tan', 'tanh', 'trunc']`
### 九、参考资料
Python math 模块 | [菜鸟教程](runoob.com) <br />
Python numpy 帮助文档 | [官网](https://numpy.org/doc/)
### 十、联系方式
电邮：liskello_o@outlook.com 或者leoliskell@gmail.com

