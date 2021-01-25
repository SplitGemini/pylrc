#!/usr/bin/python3
import sys
import pylrc
import os

'''
lrc转换srt且格式化lrc（保存所有信息，去除时间重复但是内容空白行，拆开因重复内容而折叠的时间）！支持更长时间，支持offset标记

不带参数则目标目录为工作目录，否则视第一个参数为目标目录。注意，将递归处理所有目标路径下的所有文件！

注意，转换后的srt如果已存在，会直接覆盖！但是lrc会备份(备份的是转换编码后的)
'''

music_types = ['.m4a', '.mp3', '.wav', '.flac', '.mp4']
i = 0

if len(sys.argv) == 2:
    targetDirectory = sys.argv[1]
else:
    #targetDirectory = sys.path[0]
    targetDirectory = os.getcwd()
if not os.path.exists(targetDirectory):
    print("目标文件夹: " + targetDirectory + " 不存在")
    sys.exit()
print("目标文件夹: " + targetDirectory)

for root, dirs, files in os.walk(targetDirectory):  # 遍历目标文件夹
    # 编码转为utf-8后转换格式
    for f in files:
        if '.lrc' == os.path.splitext(f)[-1].lower():
            filePath = os.path.join(root,f)
            # 编码转换
            if pylrc.convert(filePath):
                with open(filePath, 'r', encoding='UTF-8') as lrc_file:
                    lrc_string = lrc_file.read()
            else:
                print('编码转换失败，请检查：{}'.format(filePath))
                continue
            
            # 同名媒体文件
            music_file = ''
            for type in music_types:
                if os.path.exists(filePath[:-4] + type):
                    music_file = filePath[:-4] + type
                    break
            print('格式转换：转换{}'.format(filePath))
            
            # 转换srt
            subs = pylrc.parse(lrc_string, music_file)
            srt = subs.toSRT() # convert lrc to srt string
            filename = filePath[:-3] + 'srt'
            if os.path.exists(filename):
                os.remove(filename)
            with open(filename, 'w', encoding='UTF-8') as t_file:
                t_file.write(srt)
            
            # 不存在备份则备份，存在则删除
            bak = filePath + '.bak'
            if not os.path.exists(bak):
                os.rename(filePath, bak)
            else:
                os.remove(filePath)
            
            # 保存lrc
            lrc = subs.toLRC() # lrc format check
            with open(filePath, 'w', encoding='UTF-8') as t_file:
                t_file.write(lrc)
            print('转换完成\n')
            i += 1
print('有{}个{}文件被处理'.format(i, 'lrc'))