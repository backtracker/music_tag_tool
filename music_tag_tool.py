#!/usr/bin/env python3
import os
from typing import List
from cleaner.flac_cleaner import FlacCleaner
from cleaner.dsf_cleaner import DsfCleaner
from config import *


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
        print("-" * 80)
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