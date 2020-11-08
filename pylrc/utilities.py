from datetime import datetime
import re
import subprocess
import codecs
import chardet


def validateTimecode(timecode):
    """Checks if a string is a timecode of format [%M:%S.%f]"""

    try:
        unpackTimecode(timecode)
        return True

    except ValueError:
        return False


def unpackTimecode(timecode):
    """unpacks a timecode to minutes, seconds, and milliseconds"""

    if "." in timecode:
        x = datetime.strptime(timecode, '[%M:%S.%f]')
    else:
        x = datetime.strptime(timecode, '[%M:%S]')
    minutes = x.minute
    seconds = x.second
    milliseconds = int(x.microsecond / 1000)
    return minutes, seconds, milliseconds


def findEvenSplit(line):
    """
    Given a string, splits it into two evenly spaced lines
    """
    word_list = line.split(' ')
    differences = []
    for i in range(len(word_list)):
        group1 = ' '.join(word_list[0:i + 1])
        group2 = ' '.join(word_list[i + 1::])
        differences.append(abs(len(group1) - len(group2)))
    index = differences.index(min(differences))
    for i in range(len(word_list)):
        if i == index:
            group1 = ' '.join(word_list[0:i + 1])
            group2 = ' '.join(word_list[i + 1::])

    return ''.join([group1, '\n', group2]).rstrip()


def getDuration(file):
    max_time = '99:59:59,999'
    if not file:
        print("文件路径为空，设为默认的最长时间，请检查同名音频是否存在")
        return max_time
    try:
        result = subprocess.Popen('ffprobe "{}"'.format(file), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        alist = [x.decode('utf-8').replace('\n', '').strip() for x in result.stdout.readlines()]
        # Duration: 00:00:14.42, start: 0.000000, bitrate: 4042 kb/s  从这里面匹配出时长
        duration = re.match(".+?:\s([\d:\.]+),\s?.+",
                            [i for i in alist if "Duration" in i][0]).group(1).replace('.',',')+'0'
    except:
        print("未获取到音频长度，设为默认的最长时间，请检查ffprobe是否可用")
        return max_time
    else:
        print("获取到音频长度：{}".format(duration))
        return duration


def convert(file, out_enc="UTF-8"):
    """
    该程序用于将目录下的文件从使用chardet识别后格式转换到指定格式，默认是utf-8
    :param file:    文件路径
    :param out_enc: 输出文件格式
    :return:  转换是否成功
    """
    
    with open(file, "rb") as f:
        data = f.read()
        in_enc = chardet.detect(data)['encoding']
    if in_enc == None:
        return False
    in_enc = in_enc.upper()
    out_enc = out_enc.upper()
    if in_enc == out_enc:
        print("编码转换：{} 已经是{}编码了".format(file.split('\\')[-1], out_enc))
        return True
    try:
        print("编码转换：转换 \"{}\" 从 {} --> {}".format(file.split('\\')[-1], in_enc, out_enc))
        #GB18030兼容GB2312和GBK，避免它们出现不包含字符
        if in_enc == 'GB2312' or in_enc == 'GBK':
            in_enc = 'GB18030'
        with codecs.open(file, 'r', in_enc) as f:
            new_content = f.read()
        with codecs.open(file, 'w', out_enc) as f_out:
            f_out.write(new_content)
    # print (f.read())
    except IOError as err:
        print("I/O error: {0}".format(err))
        return False
    except:
        return False
    else:
        return True

def containsAny(seq):
    '''
    aset某成员是seq的子串
    '''
    aset = ['字幕', '汉化', '译', '出品', '作品']
    return True if any(i in seq for i in aset) else False
        