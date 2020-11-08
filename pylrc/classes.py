from .utilities import unpackTimecode, findEvenSplit, getDuration, containsAny

class LyricLine:
    """An object that holds a lyric line and it's time"""

    def __init__(self, timecode, text=""):
        self.hours = 0
        self.minutes, self.seconds, self.milliseconds = unpackTimecode(timecode)
        self.time = 0
        self.text = text
        self._check()

    def shift(self, minutes=0, seconds=0, milliseconds=0):
        """Shift the timecode by the given amounts"""
        self.addMinutes(minutes)
        self.addSeconds(seconds)
        self.addMillis(milliseconds)

    def addMillis(self, milliseconds):
        summation = self.milliseconds + milliseconds
        if summation >= 1000 or summation <= -1000:
            self.milliseconds = summation % (1000 if (summation > 0) else -1000)
            self.addSeconds(int(summation / 1000))
        else:
            self.milliseconds = summation
        self._check()

    def addSeconds(self, seconds):
        summation = self.seconds + seconds
        if summation >= 60 or summation <= -60:
            self.seconds = summation % (60 if (summation > 0) else -60)
            self.addMinutes(int(summation / 60))
        else:
            self.seconds = summation
        self._check()

    def addMinutes(self, minutes):
        summation = self.minutes + minutes
        if summation >= 60 or summation <= -60:
            self.minutes = summation % (60 if (summation > 0) else -60)
            self.addHours(int(summation / 60))
        else:
            self.minutes = summation
        self._check()

    def addHours(self, hours):
        summation = self.hours + hours
        if summation > 23:
            self.hours = 23
        elif summation < 0:
            self.hours = 0
            self.minutes = 0
            self.seconds = 0
            self.milliseconds = 0
        else:
            self.hours = summation
        self._check()

    def _check(self):
        if self.hours < 0 < self.minutes:
            self.hours += 1
            self.minutes -= 60
        elif self.minutes < 0 < self.hours:
            self.hours -= 1
            self.minutes += 60
        if self.minutes < 0 < self.seconds:
            self.minutes += 1
            self.seconds -= 60
        elif self.seconds < 0 < self.minutes:
            self.minutes -= 1
            self.seconds += 60
        if self.seconds < 0 < self.milliseconds:
            self.seconds += 1
            self.milliseconds -= 1000
        elif self.milliseconds < 0 < self.seconds:
            self.seconds -= 1
            self.milliseconds += 1000
        self.time = sum([(self.hours * 3600), (self.minutes * 60),
                         self.seconds, (self.milliseconds / 1000)])

    def toSrtTimeCode(self):
        ho = "{:02d}".format(self.hours)
        min = "{:02d}".format(self.minutes)
        sec = "{:02d}".format(self.seconds)
        milli = "{:03d}".format(self.milliseconds)
        timecode = ''.join([ho, ':', min, ':', sec, ',', milli])
        return timecode

    def toLrcTimeCode(self):
        # 分钟 + 小时 * 60，大于99截断前部，只取后部
        min = "{:02d}".format(self.minutes + self.hours * 60)[-2:]
        sec = "{:02d}".format(self.seconds)
        milli = "{:03d}".format(self.milliseconds)
        timecode = ''.join(['[', min, ':', sec, '.', milli, ']'])
        return timecode

    def __lt__(self, other):
        """For sorting instances of this class"""
        return self.time < other.time


class Lyrics(list):
    """A list that holds the contents of the lrc file"""

    def __init__(self, items=None):
        super().__init__()
        if items is None:
            items = []
        self.artist = ""
        self.album = ""
        self.title = ""
        self.author = ""
        self.lrc_creator = ""
        self.length = ""
        self.extend(items)
        self.music_path = ""
        
        
    def toSRT(self):
        """Returns an SRT string of the LRC data"""
        output = []
        j = 1
        for i in range(len(self)):
            if not self[i].text.isspace() and self[i].text:
                # print("lyric " + str(j) + ": " + self[i].text + ", time: " + str(self[i].time))
                # 去除字幕组简介
                if j == 1 and containsAny(self[i].text):
                    continue
                srt = str(j) + '\n'
                j += 1
                if not i == len(self) - 1:
                    end_timecode = self[i + 1].toSrtTimeCode()
                else:
                    end_timecode = getDuration(self.music_path)
                srt = srt + self[i].toSrtTimeCode() + ' --> ' + end_timecode + '\n'
                if len(self[i].text) > 31:
                    srt = srt + findEvenSplit(self[i].text).strip() + '\n'
                else:
                    srt = srt + self[i].text.strip() + '\n'
                output.append(srt)

        return '\n'.join(output).rstrip()

    def toLRC(self):
        output = []
        if self.artist != "":
            output.append('[ar:' + self.artist + ']')
        if self.album != "":
            output.append('[al:' + self.album + ']')
        if self.title != "":
            output.append('[ti:' + self.title + ']')
        if self.author != "":
            output.append('[au:' + self.author + ']')
        if self.lrc_creator != "":
            output.append('[by:' + self.lrc_creator + ']')
        if self.length != "":
            output.append('[length:' + self.length + ']')

        if output:
            output.append('')
        first = True
        for i in self:
            # 去除字幕组简介
            if first and containsAny(i.text):
                continue
            # 去除前面空白
            if first and (i.text.isspace() or not i.text):
                continue
            first = False
            lrc = i.toLrcTimeCode() + i.text.strip()
            output.append(lrc)
        return '\n'.join(output).rstrip()

    def check(self):
        j = 0
        lastItem = self[len(self) - 1]
        for i in range(len(self) - 2,-1,-1):
            currentItem = self[i]
            if currentItem.time == lastItem.time:
                if currentItem.text.isspace() or not currentItem.text:
                    self.remove(currentItem)
                    j += 1
                elif lastItem.text.isspace() or not lastItem.text:
                    self.remove(lastItem)
                    j += 1
            else:
                lastItem = currentItem
        if j != 0:
            print("删除重复时间" + str(j) + "次")