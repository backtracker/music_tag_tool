#!/usr/bin/env python3
"""
FLAC音乐tag清洗工具
功能列表：
1. 将被整理的文件移动到目标目录，并根据tag信息创建 歌手—专辑 子文件夹
2. 将音乐文件名和tag转成简体中文
3. 重命名文件名，改为 ”编号-歌曲名.flac“ 或者 ”碟号—音轨号 歌曲名.flac“
4. 只支持flac格式
"""

from opencc import OpenCC
from collections import namedtuple
from mutagen.flac import FLAC
import os
from enum import Enum
import shutil
from typing import List

# 设置简繁转换，如果不想转换，将IS_CC_CONVERT设置为False
# OpenCC  conversion ： 'hk2s', 's2hk', 's2t', 's2tw', 's2twp', 't2hk', 't2s', 't2tw', 'tw2s', and 'tw2sp'
cc = OpenCC('t2s')

IS_CC_CONVERT = True  # 是否需要opencc转换
IS_DELETE_SRC_EMPTY_DIR = True  # 是否清空源目录空文件夹
IS_KEEP_SRC_DIR_COVER = True  # 是否保留封面，根据文件名是"cover"判断封面
IS_MOVE_FILE_TO_TARGET_DIR = True  # 是否移动文件到目标目录

# 源目录
SRC_DIR = "/mnt/hdd3/音乐修复/待整理"
# SRC_DIR = "X:\hdd3\音乐修复\待整理"

# 目标目录
TARGET_DIR = '/mnt/hdd3/音乐修复/已整理'
# TARGET_DIR = 'X:\hdd3\音乐修复\已整理'

# 创建目录中需要的专辑艺术家和专辑名，以及FLAC文件名，将不支持的字符替换为支持的字符
CHAR_REPLACE_DICT = {'.': '_', ':': '：', '?': '？', '"': '“', '|': ' ', '*': '', '<': '', '>': '', '\\': '', '/': ''}

# 需要删除的源文件中的文件后缀名，如果想要保留cover，则需要IS_KEEP_SRC_DIR_COVER设置为True
DELETE_FILE_SUFFIX_LIST = ['.cue', '.log', '.txt', '.m3u', '.m3u8', '.nfo', '.md5', '.jpg', '.png', '.tif', '.gif',
                           '.url']

# tag中需要删除的key, 另外musicbrainz和itunes开头的key也会删除
POP_KEY_LIST = ['author', 'albumartistsort', 'artistsort', 'albumsort', 'arranger', "acoustid_id", "isrc", "length",
                "script", "originalyear", "originaldate", "barcode", "media", "releasecountry", "publisher", "label",
                "releasestatus", "id", "comment", "encoder", "performer", 'discid', 'ctdbtrackconfidence',
                'cdtoc', "album artist", "notes", 'gnid']

# tag信息缺失文件列表
lack_tag_file_list = []


class TagEnum(Enum):
    """
    FLAC tag字段枚举类型
    """
    TITLE = 'title'
    ARTIST = 'artist'
    ALBUM = 'album'
    TRACK_NUMBER = 'tracknumber'
    DATE = 'date'
    ALBUM_ARTIST = 'albumartist'
    DISC_NUMBER = 'discnumber'


# 设置FLAC TAG namedtuple
Tag = namedtuple('Tag', ['title', 'artist', 'album', 'track_number', 'date', 'album_artist', 'disc_number'])


def get_all_flac_file() -> List[str]:
    """
    遍历SRC_DIR目录下全部flac文件，并返回文件列表
    """
    flac_file_list = []
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".flac"):
                flac_file_list.append(os.path.join(root, file))
    return flac_file_list


def get_flac_tag(flac: FLAC) -> Tag:
    """
    获取flac文件的tag信息，并转成TagNamedTuple
    """
    title = __init_flac_tag_value(flac, TagEnum.TITLE.value)
    artist = __init_flac_tag_value(flac, TagEnum.ARTIST.value)
    album = __init_flac_tag_value(flac, TagEnum.ALBUM.value)
    track_number = __init_flac_tag_value(flac, TagEnum.TRACK_NUMBER.value)
    date = __init_flac_tag_value(flac, TagEnum.DATE.value)
    album_artist = __init_flac_tag_value(flac, TagEnum.ALBUM_ARTIST.value)
    disc_number = __init_flac_tag_value(flac, TagEnum.DISC_NUMBER.value)
    return Tag(title=title, artist=artist, album=album, track_number=track_number, date=date,
               album_artist=album_artist, disc_number=disc_number)


def __init_flac_tag_value(flac: FLAC, key):
    """
    初始化tag，如果没有该key则给个空值
    """
    if key in flac.keys():
        return flac[key][0]  # tag key的value是个list,有这个key则取列表第一个元素
    else:
        return ""


def clean_flac_tag(flac: FLAC):
    """
    清洗flac文件tag
    1. 处理Tag字段中中前后空格
    2. 处理artist和albumartist字段为空的情况
    3. 如果tag中的专辑信息，歌手信息，歌曲名，音轨号信息存在空数据，则不处理
    4. 处理tracknumber字段，改为两位数字
    5. 判断tag是否为繁体中文，如果有繁体中文则转换为简体中文
    """
    print("开始清洗flac文件: {}".format(flac.filename))
    tag = get_flac_tag(flac)
    print("{} tag信息: {}".format(os.path.basename(flac.filename), tag))

    # 处理Tag字段中中前后空格
    flac[TagEnum.ARTIST.value] = tag.artist.strip()
    flac[TagEnum.ALBUM_ARTIST.value] = tag.album_artist.strip()
    flac[TagEnum.ALBUM.value] = tag.album.strip()
    flac[TagEnum.TITLE.value] = tag.title.strip()
    flac[TagEnum.DISC_NUMBER.value] = tag.disc_number.strip()
    flac[TagEnum.DATE.value] = tag.date.strip()
    flac[TagEnum.TRACK_NUMBER.value] = tag.track_number.strip()
    flac.save()

    tag = get_flac_tag(flac)  # 获取去除前后空格后的tag

    # 处理artist和albumartist字段为空的情况
    if tag.artist == "" and tag.album_artist != "":
        flac[TagEnum.ARTIST.value] = tag.album_artist
        flac.save()
    if tag.album_artist == "" and tag.artist != "":
        flac[TagEnum.ALBUM_ARTIST.value] = tag.artist
        flac.save()

    tag = get_flac_tag(flac)  # 获取处理artist和albumartist字段为空的情况后的tag

    # 如果tag中的专辑名称，专辑艺术家，歌曲名，音轨号信息存在空数据，则不处理
    if tag.album_artist == "" or tag.album == "" or tag.title == "" or tag.track_number == "":
        print("{} tag信息缺失， 忽略清洗！！！".format(os.path.basename(flac.filename)))
        lack_tag_file_list.append(flac.filename)
        print("-" * 80)
        return None

    # 处理tracknumber字段，改为两位数字。若使用/分隔，取前面数值，处理 4/16 这样的情况
    track_number = tag.track_number.split("/")[0]
    track_number = int(track_number)
    track_number = "{:02d}".format(track_number)
    flac[TagEnum.TRACK_NUMBER.value] = track_number

    # 处理discnumber字段，若使用/分隔，取前面数值，处理 1/1 这样的情况
    disc_number = tag.disc_number.split("/")[0]
    flac[TagEnum.DISC_NUMBER.value] = disc_number

    flac.save()

    # 根据IS_TRANSLATE配置，进行简繁转换
    if IS_CC_CONVERT:
        flac[TagEnum.TITLE.value] = cc.convert(tag.title)
        flac[TagEnum.ARTIST.value] = cc.convert(tag.artist)
        flac[TagEnum.ALBUM.value] = cc.convert(tag.album)
        flac[TagEnum.ALBUM_ARTIST.value] = cc.convert(tag.album_artist)
        flac.save()  # 保存修改后的tag

    # 清理不必要的key
    pop_flac_keys(flac)
    print("{} tag 清洗完成：{}".format(os.path.basename(flac.filename), flac))


def pop_flac_keys(flac: FLAC):
    """
    清理flac文件中不必要的key, 另外musicbrainz和itunes开头的key也默认删除
    """
    for key in POP_KEY_LIST:
        if key in flac.keys():
            flac.pop(key=key)
    # pop musicbrainz和itunes开头的key
    for key in flac.keys():
        if key.startswith("musicbrainz") or key.startswith("itunes"):
            flac.pop(key=key)
    flac.save()


def rename_flac_file(file):
    """
    重命名flac文件
    1. 如果tag中的专辑信息，歌手信息，歌曲名，音轨号信息存在空数据，则不处理
    2. 根据是否有discnumber字段，判断是否需要将discnumber加入到文件名中
    3. 处理new_file_name中windows不支持的字符
    4. 重命名文件，并返回新文件名
    """
    flac = FLAC(file)
    tag = get_flac_tag(flac)
    # 如果tag中的专辑信息，歌手信息，歌曲名，音轨号信息存在空数据，则不处理
    if tag.album_artist == "" or tag.album == "" or tag.title == "" or tag.track_number == "":
        return None

    # 如果tag信息中包含则discnumber则需要将discnumber加入到文件名中
    if tag.disc_number != "":
        new_file_name = "{}-{} {}.flac".format(tag.disc_number, tag.track_number, tag.title)
    else:
        new_file_name = "{}. {}.flac".format(tag.track_number, tag.title)

    # 处理new_file_name中windows不支持的字符
    for k, v in CHAR_REPLACE_DICT.items():
        if k != "." and k in new_file_name:  # 文件名中不需要过滤.
            new_file_name = new_file_name.replace(k, v)

    new_file = os.path.join(os.path.dirname(file), new_file_name)
    os.rename(file, new_file)
    return new_file


def move_flac_file(file):
    """
    移动flac文件到目标目录
    1. 处理albumartist和album目录中的特殊字符,并将英文的点替换为下划线
    2. 判断目标目录中albumartist和album目录是否存在，如果不存在则创建
    3. 移动文件到目标目录下面的 专辑艺术家-专辑 目录下，如果文件已经存在，则不移动
    """
    flac = FLAC(file)
    tag = get_flac_tag(flac)

    # 处理albumartist和album中的特殊字符
    album_artist = tag.album_artist
    # 处理album中的特殊字符
    album = tag.album
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
    flac_file_list = get_all_flac_file()
    for flac_file in flac_file_list:
        print("开始处理文件: {}".format(flac_file))
        flac = FLAC(flac_file)
        clean_flac_tag(flac)
        new_file = rename_flac_file(flac_file)
        if IS_MOVE_FILE_TO_TARGET_DIR and new_file is not None:
            move_flac_file(new_file)

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
