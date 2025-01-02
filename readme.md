# 音乐 tag 清洗工具  

### 简介

FLAC 、DSF、MP3 音乐 tag 清洗工具。
对音乐文件进行批量操作前，务必复制小部分音乐文件进行小范围测试！！！

### 使用方法

修改`confiy.py`中`SRC_DIR`和`TARGET_DIR`，运行`main.py`脚本进行音乐Tag清洗

![示例](example.png)

### 功能列表  
1. 清洗被整理的目录内FLAC音乐文件，移动到目标目录，并根据tag信息创建 歌手—专辑 子文件夹  
2. 将音乐文件名和tag转成简体中文  
3. 重命名文件名，改为 ”编号. 歌曲名.flac“ 或者 ”碟号—音轨号 歌曲名.flac“  
4. 支持flac格式、dsf格式 ，如需支持其他格式请自行添加`Cleaner`进行扩展

### 注意事项  

 1. 如果不想清空源目录，请将`IS_DELETE_SRC`设置为False
 2. 如果清洗日文歌曲，请将`IS_CC_CONVERT`设置为False
