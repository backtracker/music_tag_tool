#!/usr/bin/env python3
from abc import abstractmethod, ABC
from mutagen.dsf import DSF
from opencc import OpenCC
from mutagen.flac import FLAC
import os
import shutil
from typing import List
from mutagen import FileType
from mutagen.id3 import TIT2, TALB, TPE1, TPE2, TRCK, TDRC, TPOS

# 设置简繁转换，如果不想转换，将IS_CC_CONVERT设置为False
# OpenCC  conversion ： 'hk2s', 's2hk', 's2t', 's2tw', 's2twp', 't2hk', 't2s', 't2tw', 'tw2s', and 'tw2sp'
cc = OpenCC('t2s')

IS_CC_CONVERT = True  # 是否需要opencc转换
IS_DELETE_SRC_EMPTY_DIR = True  # 是否清空源目录空文件夹
IS_KEEP_SRC_DIR_COVER = True  # 是否保留封面，根据文件名是"cover"判断封面
IS_MOVE_FILE_TO_TARGET_DIR = True  # 是否移动文件到目标目录

# 源目录
SRC_DIR = "音乐修复\待整理"

# 目标目录
TARGET_DIR = '音乐修复\已整理'

# 支持清洗的音乐类型
SUPPORT_MUSIC_TYPE = ['.flac', '.dsf']

# 创建目录中需要的专辑艺术家和专辑名，以及FLAC文件名，将不支持的字符替换为支持的字符
CHAR_REPLACE_DICT = {'.': '_', ':': '：', '?': '？', '"': '“', '|': ' ', '*': '', '<': '', '>': '', '\\': '', '/': ''}

# 需要删除的源文件中的文件后缀名，如果想要保留cover，则需要IS_KEEP_SRC_DIR_COVER设置为True
DELETE_FILE_SUFFIX_LIST = ['.cue', '.log', '.txt', '.m3u', '.m3u8', '.nfo', '.md5', '.jpg', '.png', '.tif', '.gif',
                           '.url']

# FLAC tag中需要删除的key, 另外musicbrainz和itunes开头的key也会删除
FLAC_POP_KEY_LIST = ['author', 'albumartistsort', 'artistsort', 'albumsort', 'arranger', "acoustid_id", "isrc",
                     "length",
                     "script", "originalyear", "originaldate", "barcode", "media", "releasecountry", "publisher",
                     "label",
                     "releasestatus", "id", "comment", "encoder", "performer", 'discid', 'ctdbtrackconfidence',
                     'cdtoc', "album artist", "notes", 'gnid']

# DSF tag中需要删除的key, 另外TXXX开头的key也会删除
DSF_POP_KEY_LIST = ['TSO2', 'TSOP', 'TSRC', 'TMED']

# tag信息缺失文件列表
lack_tag_file_list = []


class MusicCleaner(ABC):
    def __init__(self, filename):
        self.filename = filename
        self.music: FileType = None

    # 标题
    @property
    @abstractmethod
    def title(self):
        pass

    @title.setter
    @abstractmethod
    def title(self, value):
        pass

    # 艺术家
    @property
    @abstractmethod
    def artist(self):
        pass

    @artist.setter
    @abstractmethod
    def artist(self, value):
        pass

    # 专辑名称
    @property
    @abstractmethod
    def album(self):
        pass

    @album.setter
    @abstractmethod
    def album(self, value):
        pass

    #  音轨号
    @property
    @abstractmethod
    def track_number(self):
        pass

    @track_number.setter
    @abstractmethod
    def track_number(self, value):
        pass

    # 发行日期
    @property
    @abstractmethod
    def date(self):
        pass

    @date.setter
    @abstractmethod
    def date(self, value):
        pass

    #  专辑艺术家
    @property
    @abstractmethod
    def album_artist(self):
        pass

    @album_artist.setter
    @abstractmethod
    def album_artist(self, value):
        pass

    # 碟号
    @property
    @abstractmethod
    def disc_number(self):
        pass

    @disc_number.setter
    @abstractmethod
    def disc_number(self, value):
        pass

    # 清洗Tag
    def clean_tags(self):
        print("开始清洗音乐文件: {}".format(self.music.filename))
        print("{} tag信息: {}".format(os.path.basename(self.music.filename), self.music))

        # 处理Tag字段中中前后空格
        self.artist = self.artist.strip()
        self.album_artist = self.album_artist.strip()
        self.album = self.album.strip()
        self.title = self.title.strip()
        self.track_number = self.track_number.strip()
        self.date = self.date.strip()
        self.disc_number = self.disc_number.strip()

        # 处理artist和albumartist字段为空的情况
        if self.artist == "" and self.album_artist != "":
            self.artist = self.album_artist
        if self.album_artist == "" and self.artist != "":
            self.album_artist = self.artist

        # 如果tag中的专辑名称，专辑艺术家，歌曲名，音轨号信息存在空数据，则不处理
        if self.album_artist == "" or self.album == "" or self.title == "" or self.track_number == "":
            print("{} tag信息缺失， 忽略清洗！！！".format(os.path.basename(self.music.filename)))
            lack_tag_file_list.append(self.music.filename)
            print("-" * 80)
            return None

        # 处理tracknumber字段，改为两位数字。若使用/分隔，取前面数值，处理 4/16 这样的情况
        track_number = self.track_number.split("/")[0]
        track_number = int(track_number)
        track_number = "{:02d}".format(track_number)
        self.track_number = track_number

        # 处理discnumber字段，若使用/分隔，取前面数值，处理 1/1 这样的情况
        disc_number = self.disc_number.split("/")[0]
        self.disc_number = disc_number

        # 根据IS_TRANSLATE配置，进行简繁转换
        if IS_CC_CONVERT:
            self.title = cc.convert(self.title)
            self.artist = cc.convert(self.artist)
            self.album = cc.convert(self.album)
            self.album_artist = cc.convert(self.album_artist)

        # 清理不必要的key
        self.pop_keys()
        print("{} tag 清洗完成：{}".format(os.path.basename(self.music.filename), self.music))

    # 清空多余key
    @abstractmethod
    def pop_keys(self):
        pass

    # 重命名文件
    def rename_file(self):
        """
        重命名音乐文件
        1. 如果tag中的专辑信息，歌手信息，歌曲名，音轨号信息存在空数据，则不处理
        2. 根据是否有discnumber字段，判断是否需要将discnumber加入到文件名中
        3. 处理new_file_name中windows不支持的字符
        4. 重命名文件，并返回新文件名
        """
        # 如果tag中的专辑信息，歌手信息，歌曲名，音轨号信息存在空数据，则不处理
        if self.album_artist == "" or self.album == "" or self.title == "" or self.track_number == "":
            return None

        # 文件后缀名
        file_suffix = os.path.splitext(self.filename)[1]

        # 如果tag信息中包含则discnumber则需要将discnumber加入到文件名中
        if self.disc_number != "":
            new_file_name = "{}-{} {}{}".format(self.disc_number, self.track_number, self.title, file_suffix)
        else:
            new_file_name = "{}. {}{}".format(self.track_number, self.title, file_suffix)

        # 处理new_file_name中windows不支持的字符
        for k, v in CHAR_REPLACE_DICT.items():
            if k != "." and k in new_file_name:  # 文件名中不需要过滤.
                new_file_name = new_file_name.replace(k, v)

        new_file = os.path.join(os.path.dirname(self.filename), new_file_name)
        os.rename(self.filename, new_file)
        return new_file

    # 移动文件到目标目录
    def move_file(self, file):
        print(file)
        """
        移动音乐文件到目标目录
        1. 处理albumartist和album目录中的特殊字符,并将英文的点替换为下划线
        2. 判断目标目录中albumartist和album目录是否存在，如果不存在则创建
        3. 移动文件到目标目录下面的 专辑艺术家-专辑 目录下，如果文件已经存在，则不移动
        """

        # 处理albumartist和album中的特殊字符
        album_artist = self.album_artist
        # 处理album中的特殊字符
        album = self.album
        for k, v in CHAR_REPLACE_DICT.items():
            if k in album:
                album = album.replace(k, v)
            if k in album_artist:
                album_artist = album_artist.replace(k, v)

        # 判断专辑艺术家，专辑目录是否存在，不存在则创建
        artist_dir = os.path.join(TARGET_DIR, album_artist)
        if not os.path.exists(artist_dir):
            os.mkdir(artist_dir)

        album_dir = os.path.join(artist_dir, album)
        if not os.path.exists(album_dir):
            os.mkdir(album_dir)

        # 移动文件到指定目录,如果文件已经存在则不移动
        if not os.path.exists(os.path.join(album_dir, os.path.basename(file))):
            shutil.move(file, album_dir)
            print("成功移动文件:{} 到目录:{}".format(file, album_dir))
        else:
            print("{} 文件已经存在，不移动".format(os.path.join(album_dir, os.path.basename(file))))
        print("-" * 80)


class FlacCleaner(MusicCleaner):
    def __init__(self, filename):
        super().__init__(filename)
        self.music = FLAC(filename)

    @property
    def title(self):
        key = "title"
        # flac key的值是个list,有这个key则取列表第一个元素
        return self.music[key][0] if key in self.music.keys() else ""

    @title.setter
    def title(self, new_value):
        self.music["title"] = new_value
        self.music.save()

    @property
    def artist(self):
        key = "artist"
        return self.music[key][0] if key in self.music.keys() else ""

    @artist.setter
    def artist(self, new_value):
        self.music["artist"] = new_value
        self.music.save()

    @property
    def album(self):
        key = "album"
        return self.music[key][0] if key in self.music.keys() else ""

    @album.setter
    def album(self, new_value):
        self.music["album"] = new_value
        self.music.save()

    @property
    def track_number(self):
        key = "tracknumber"
        return self.music[key][0] if key in self.music.keys() else ""

    @track_number.setter
    def track_number(self, new_value):
        self.music["tracknumber"] = new_value
        self.music.save()

    @property
    def date(self):
        key = "date"
        return self.music[key][0] if key in self.music.keys() else ""

    @date.setter
    def date(self, new_value):
        self.music["date"] = new_value
        self.music.save()

    @property
    def album_artist(self):
        key = "albumartist"
        return self.music[key][0] if key in self.music.keys() else ""

    @album_artist.setter
    def album_artist(self, new_value):
        self.music["albumartist"] = new_value
        self.music.save()

    @property
    def disc_number(self):
        key = "discnumber"
        return self.music[key][0] if key in self.music.keys() else ""

    @disc_number.setter
    def disc_number(self, new_value):
        self.music["discnumber"] = new_value
        self.music.save()

    def clean_tags(self):
        super().clean_tags()

    def pop_keys(self):
        pop_key_list = []
        for key in self.music.keys():
            if key in FLAC_POP_KEY_LIST:
                pop_key_list.append(key)
            if key.startswith("musicbrainz") or key.startswith("itunes"):
                pop_key_list.append(key)
        for key in pop_key_list:
            self.music.pop(key)
        self.music.save()


class DsfCleaner(MusicCleaner):
    def __init__(self, filename):
        super().__init__(filename)
        self.music = DSF(filename)

    @property
    def title(self):
        return str(self.music["TIT2"]) if "TIT2" in self.music.keys() else ""

    @title.setter
    def title(self, new_value):
        self.music["TIT2"] = TIT2(encoding=3, text=[new_value])
        self.music.save()

    @property
    def artist(self):
        return str(self.music["TPE1"]) if "TPE1" in self.music.keys() else ""

    @artist.setter
    def artist(self, new_value):
        self.music["TPE1"] = TPE1(encoding=3, text=[new_value])
        self.music.save()

    @property
    def album(self):
        return str(self.music["TALB"]) if "TALB" in self.music.keys() else ""

    @album.setter
    def album(self, new_value):
        self.music["TALB"] = TALB(encoding=3, text=[new_value])
        self.music.save()

    @property
    def track_number(self):
        return str(self.music["TRCK"]) if "TRCK" in self.music.keys() else ""

    @track_number.setter
    def track_number(self, new_value):
        self.music["TRCK"] = TRCK(encoding=3, text=[new_value])
        self.music.save()

    @property
    def date(self):
        return str(self.music["TDRC"]) if "TDRC" in self.music.keys() else ""

    @date.setter
    def date(self, new_value):
        self.music["TDRC"] = TDRC(encoding=3, text=[new_value])
        self.music.save()

    @property
    def album_artist(self):
        return str(self.music["TPE2"]) if "TPE2" in self.music.keys() else ""

    @album_artist.setter
    def album_artist(self, new_value):
        self.music["TPE2"] = TPE2(encoding=3, text=[new_value])
        self.music.save()

    @property
    def disc_number(self):
        return str(self.music["TPOS"]) if "TPOS" in self.music.keys() else ""

    @disc_number.setter
    def disc_number(self, new_value):
        self.music["TPOS"] = TPOS(encoding=3, text=[new_value])
        self.music.save()

    def clean_tags(self):
        super().clean_tags()

    def pop_keys(self):
        pop_key_list = []
        for key in self.music.keys():
            if key in DSF_POP_KEY_LIST:
                pop_key_list.append(key)
            if key.startswith("TXXX"):  # 清除DSF用户自定义的key
                pop_key_list.append(key)
        for key in pop_key_list:
            self.music.pop(key)
        self.music.save()


def get_all_music_file() -> List[str]:
    """
    遍历SRC_DIR目录下全部flac文件，并返回文件列表
    """
    music_file_list = []
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            extension = os.path.splitext(file)[1]
            if extension in SUPPORT_MUSIC_TYPE:
                music_file_list.append(os.path.join(root, file))
    return music_file_list


def delete_empty_dir(folder):
    """
    获取目录下所有文件，删除后缀在DELETE_FILE_SUFFIX_LIST中的文件，然后删除空的目录
    """
    # 查找目录下全部文件，得到一个列表
    # 待删除文件列表
    delete_file_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            # 如果file的后缀名在SUFFIX_LIST中，则将文件加入待删除列表
            if os.path.splitext(file)[1].lower() in DELETE_FILE_SUFFIX_LIST:
                # 判断是否是封面文件， 如果不是封面则添加到删除列表中
                if IS_KEEP_SRC_DIR_COVER:
                    if "cover" not in os.path.basename(file).split(".")[0].lower():
                        delete_file_list.append(os.path.join(root, file))
                else:
                    delete_file_list.append(os.path.join(root, file))

    # 删除文件
    for file in delete_file_list:
        print("删除文件:{}".format(file))
        os.remove(file)
    # 删除空目录
    dir_list = []
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            dir_list.append(os.path.join(root, dir))
    dir_list.sort(reverse=True)
    for dir in dir_list:
        if len(os.listdir(dir)) == 0:
            print("删除空目录:{}".format(dir))
            os.rmdir(dir)


if __name__ == '__main__':
    music_file_list = get_all_music_file()
    # 根据专辑名称存放歌曲
    album_music_cleaner_dict = {}
    for music_file in music_file_list:
        print("-"*80)
        print("开始清洗文件: {}".format(music_file))
        if music_file.endswith(".flac"):
            music_cleaner = FlacCleaner(music_file)
        elif music_file.endswith(".dsf"):
            music_cleaner = DsfCleaner(music_file)
        music_cleaner.clean_tags()

        album_music_cleaner_dict.setdefault(music_cleaner.album, []).append(music_cleaner)

    # 开始处理碟号，如果专辑是单张碟，将整张专辑碟号字段清空
    for album, music_cleaner_list in album_music_cleaner_dict.items():
        # 专辑是否是单张碟
        is_album_single_disc = True
        for music_cleaner in music_cleaner_list:
            if str(music_cleaner.disc_number).isdigit():
                if int(music_cleaner.disc_number) > 1:
                    is_album_single_disc = False
                    break
        # 清空单张碟的碟号
        if is_album_single_disc:
            for music_cleaner in music_cleaner_list:
                print("开始清空单碟文件碟号：{}".format(music_cleaner.filename))
                music_cleaner.disc_number = ""

    print("Tag清洗完成，开始文件处理...")
    print("=" * 100)

    music_file_list = get_all_music_file()
    # 排除tag信息不全的文件
    music_file_list = [music_file for music_file in music_file_list if music_file not in lack_tag_file_list]

    for music_file in music_file_list:
        print("开始处理文件: {}".format(music_file))
        if music_file.endswith(".flac"):
            music_cleaner = FlacCleaner(music_file)
        elif music_file.endswith(".dsf"):
            music_cleaner = DsfCleaner(music_file)
        new_file = music_cleaner.rename_file()

        if IS_MOVE_FILE_TO_TARGET_DIR and new_file is not None:
            music_cleaner.move_file(new_file)

    # 清空空目录
    if IS_DELETE_SRC_EMPTY_DIR:
        delete_empty_dir(SRC_DIR)

    print("=" * 100)
    if len(lack_tag_file_list) > 0:
        print("{} 清洗完成， 共有 {} 个文件失败！！！".format(SRC_DIR, len(lack_tag_file_list)))
        print("失败文件列表如下： ")
        for file in lack_tag_file_list:
            print(file)
    else:
        print("{} 清洗完成".format(SRC_DIR))
