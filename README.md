# SealGenForOCR

## 项目介绍

针对OCR的印章识别，本项目根据印章特征在 localhost02 大佬的印章生成的基础上专门为OCR定制了可方便生成批量印章数据，并根据印章的特征，简单标注少量数据即可完成所有标注任务，节约人工标注的时间。

**生成：** 开发者仅需提供需要生成的公司名称文件，即可一键得到预设定的印章数据，也可以根据需要调整参数生成业务相符的印章风格。

**标签：** 开发者只需要标注少量的数据，即可一键为生成的印章生成标签。

注：目前印章编码使用随机生成的方式，不支持自定义

## 印章生成

### 快速入门

1. 安装java相关环境，小白可百度
2. 用IDE（推荐Intelli IDE，谁用谁知道）打开项目，可能需要选择java的SDK
3. 环境准备好之后，直接运行，在 `tools` 文件夹下存在三个文件夹即是所需要的印章

### 代码核心

感谢 localhost02 为我们封装了核心的代码，开发者仅需要了解以下几种即可。

| 类            | 方法                                                         |
| ------------- | ------------------------------------------------------------ |
| SealFont      | setFontText -> 字体内容<br />setFontFamily -> 字体<br />setMarginSize -> 字体边距<br />setFontSize -> 字体大小<br />setFontSpace -> 字体间距<br />setBold -> 加粗 |
| configuration | 按照印章文字从上到下<br />setMainFont -> 设置主名称<br />setCenterFont -> 设置印章中心(水平)<br />setTitleFont -> 设置标题<br />setViceFont -> 设置编码<br />印章圆圈从外到里<br />setBorderCircle -> 外边圆<br />setBorderInnerCircle -> 外边圆内侧<br />setInnerCircle -> 中心圆 |
| SealUtil      | buildAndStoreSeal -> 生成公章的方法，包含圆圈以及椭圆<br />buildAndStorePersonSeal -> 生成私人章的方法 |

开发者可以根据上述接口实现业务需求。本项目对以上方法又进一步封装，开发者实际使用仅需要配置四个变量，每个变量又以字典方式存储信息，其中 `hidden` 用来处理是否显示。

| 变量名     | 参数           |                                                              |
| ---------- | -------------- | ------------------------------------------------------------ |
| confInfo   | 所有文字的配置 | Text 文字内容<br />Size 字体大小<br />Bold 加粗<br />Margin 边距<br />Space 间距<br />Font 字体 |
| circleInfo | 圆圈的配置     | BorderCircle 粗细 宽 高<br />BorderInnerCircle 同上<br />InnerCircle 同上 |
| sealInfo   | 印章图片的配置 | ImgPath 图片输出路径<br />ImageSize 图片大小<br />BackgroundColor 背景颜色<br />LabelPath 印章文字信息文件路径<br />type 印章类型 |
| filepath   | 公司名称路径   | 根据私章还是公章，配置不同的文件路径                         |



## 标签生成

### 详细步骤

0. 按照印章生成步骤，在 `tools` 目录下得到如下结构：

   ```
   | - tools
     | - Oval
       | - image # 生成的印章图片
       | - SealInfo.csv #生成的印章信息
     | - ...
   ```

1. 提取需要标注的信息<br>
    使用 baseLabel.py 将需要做标注的文件放入到`tools\*\sample\*.png`(* 为 Circle, Oval, Person)文件下
    ```shell
    # SealUtil项目目录下
    python tools\baseLabel.py
    # 输出的结果中，mainList中的文件仅需要标注公司名称，otherList中文件仅需要除公司名称外其他名称
    ```
    执行结束后，得到如下目录结构

    | - tools
      | - Oval
        | - image # 生成的印章图片
        | - SealInfo.csv #生成的印章信息
        | - sample # 需要标注的图片
      | - ...


2. 标注数据<br>
   
该步骤可以采用默认的基础标注文件进行使用，步骤如下
   
   ```
   将 tools 文件夹下的baseLabel_*.json分别放入*文件夹下，表示该类印章已经标注，从而可以执行后续操作
   ```
   
   不采用默认标注文件，则需要用到多边形标注，采用labelme标注工具，详细标注方式见**labelme标注说明**
   
   ```shell
    # 安装labelme
    pip install labelme
    # 打开labelme
    labelme
    # 打开需要标注的文件夹路径
    # 如：打开 tools\*\sample 文件夹进行标注
   ```
   
3. 再次运行 baseLabel.py 脚本，得到如下目录结构
    ```
    | - SealGenForOCR
      | - image		# 汇总所有印章文件
      | - label.txt	# 汇总所有标签文件
      | - ...
      | - tools
        | - Oval
          | - image # 生成的印章图片
          | - SealInfo.csv #生成的印章信息
          | - sample # 需要标注的图片
          | - baseLabel_Oval.json # 基础的标注数据，用于自动标注的基础
          | - label_Circle.txt
        | - ...
    ```

### labelme标注说明

1. 标注采用左上角顺时针、左下角逆时针两种方式，程序会自动转化为左上角顺时针格式

2. 标签的标注方式比较特殊，核心是以字数作为标注核心，举例说明

3. 如图

      <div align="center">
        <img src="img/公章4.png" width="300">
      </div>
      
      欢乐无敌制图网淘宝店专用章：标签应根据字数来表示，用 **13** 表示
      123456789012345 ：标签需要自定一个标签，用 **c15** (center)表示
      
      正版认证：同理，用 **t4** (title) 表示
      
      若底部有编码数字，用 **v10** 表示
      
      ***强调说明后续的数字均是标注对象的字数***

3. 修改`baseLabel.py` 文件中标签的映射关系，变量为OvalTable、CircleTable。

   ```
   # 假设有 如下标签  8，10，c15, c20,t4,t6,v10,v12
   OvalTable = {15: "c15", 20: "c20", 4: "t4", 6: "t6",10:"v10",12:"v12"} 
   CircleTable = {15: "c15", 20: "c20", 4: "t4", 6: "t6",10:"v10",12:"v12"}
   ```

   注：不需要标注纯数字，即公司名称，而对于映射，若出现t4, v4这种会存在错误，但在实际印章中这种情况较少，暂不考虑

## TODO

1. 增加私人章的批量生成
2. 分离标注代码，可自定义选择步骤
3. 增加所有数据支持文件导入功能
4. 改善标签冲突问题

# 捐赠

路过的开发者如果有更好的设计模式，想法，非常欢迎大佬们指教，也欢迎各位开发者提pr。

开源不易，如果有能力的，可以资助作者一下，也算是对我的一种认可和激励。

| 支付宝                      | 微信                      |
| --------------------------- | ------------------------- |
| ![公众号](img/支付宝.png) | ![公众号](img/微信.png) |




# 参考仓库

1. https://github.com/localhost02/SealUtil
