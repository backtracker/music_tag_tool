import os
import shutil
from abc import abstractmethod, ABC
from mutagen import FileType
from config import *


class MusicCleaner(ABC):
    def __init__(self, music_file, target_dir, is_cc_convert, is_delete_src, is_move_file):
        self.music_file = music_file
        self.target_dir = target_dir
        self.is_cc_convert = is_cc_convert
        self.is_delete_src = is_delete_src
        self.is_move_file = is_move_file
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

    @property
    @abstractmethod
    def genre(self):
        pass

    @genre.setter
    @abstractmethod
    def genre(self, value):
        pass

    # 清洗Tag
    def clean_tags(self):
        print("开始清洗音乐文件: {}".format(self.music.filename))
        print("{} tag信息: {}".format(os.path.basename(self.music.filename), str(self.music)[:1000]))

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
        if self.is_cc_convert:
            self.title = cc.convert(self.title)
            self.artist = cc.convert(self.artist)
            self.album = cc.convert(self.album)
            self.album_artist = cc.convert(self.album_artist)

        # 清理不必要的key
        self.pop_keys()
        print("{} tag 清洗完成：{}".format(os.path.basename(self.music.filename), str(self.music)[:1000]))

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
        file_suffix = os.path.splitext(self.music_file)[1].lower()

        # 如果tag信息中包含则discnumber则需要将discnumber加入到文件名中
        if self.disc_number != "":
            new_file_name = "{}-{} {}{}".format(self.disc_number, self.track_number, self.title, file_suffix)
        else:
            new_file_name = "{}. {}{}".format(self.track_number, self.title, file_suffix)

        # 处理new_file_name中windows不支持的字符
        for k, v in CHAR_REPLACE_DICT.items():
            if k != "." and k in new_file_name:  # 文件名中不需要过滤.
                new_file_name = new_file_name.replace(k, v)

        new_file = os.path.join(os.path.dirname(self.music_file), new_file_name)
        os.rename(self.music_file, new_file)
        return new_file

    # 移动文件到目标目录
    def move_file(self, file):
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
        artist_dir = os.path.join(self.target_dir, album_artist)
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
