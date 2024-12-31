# !/usr/bin/env python3
import click
import os
from typing import List
from cleaner.flac_cleaner import FlacCleaner
from cleaner.dsf_cleaner import DsfCleaner
from config import *


def get_all_music_file(dir) -> List[str]:
    """
    遍历SRC_DIR目录下全部flac文件，并返回文件列表
    """
    music_file_list = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            extension = os.path.splitext(file)[1]
            if extension in SUPPORT_MUSIC_TYPE:
                music_file_list.append(os.path.join(root, file))
    return music_file_list


def delete_empty_dir(folder, is_keep_cover):
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
                if is_keep_cover:
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


@click.command()
@click.option('-s', '--src_dir', default=SRC_DIR, help='源目录')
@click.option('-t', '--target_dir', default=TARGET_DIR, help='目标目录')
@click.option('-c', '--is_cc_convert', default=IS_CC_CONVERT,
              help="是否需要opencc转换")
@click.option('-d', '--is_delete_src', default=IS_DELETE_SRC, help='是否清空源目录空文件夹')
@click.option('-m', '--is_move_file', default=IS_MOVE_FILE, help='是否移动文件到目标目录')
@click.option('-k', '--is_keep_cover', default=IS_KEEP_COVER, help='是否保留封面，根据文件名是"cover"判断封面')
def run(src_dir, target_dir, is_cc_convert, is_delete_src, is_move_file, is_keep_cover):
    """
    音乐 tag 清洗工具。 对音乐文件进行批量操作前，务必复制小部分音乐文件进行小范围测试！！！
    修改confiy.py中SRC_DIR和TARGET_DIR，运行main.py脚本进行音乐Tag清洗
    """
    music_file_list = get_all_music_file(src_dir)
    # 根据专辑名称存放歌曲
    album_music_cleaner_dict = {}
    for music_file in music_file_list:
        print("-" * 80)
        print("开始清洗文件: {}".format(music_file))
        if music_file.endswith(".flac"):
            music_cleaner = FlacCleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
        elif music_file.endswith(".dsf"):
            music_cleaner = DsfCleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
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
                print("开始清空单碟文件碟号：{}".format(music_cleaner.music_file))
                music_cleaner.disc_number = ""

    print("Tag清洗完成，开始文件处理...")
    print("=" * 100)

    music_file_list = get_all_music_file(src_dir)
    # 排除tag信息不全的文件
    music_file_list = [music_file for music_file in music_file_list if music_file not in lack_tag_file_list]

    for music_file in music_file_list:
        print("开始处理文件: {}".format(music_file))
        if music_file.endswith(".flac"):
            music_cleaner = FlacCleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
        elif music_file.endswith(".dsf"):
            music_cleaner = DsfCleaner(music_file)
        new_file = music_cleaner.rename_file()

        if is_move_file and new_file is not None:
            music_cleaner.move_file(new_file)

    # 清空空目录
    if is_delete_src:
        delete_empty_dir(src_dir, is_keep_cover)

    print("=" * 100)
    if len(lack_tag_file_list) > 0:
        print("{} 清洗完成， 共有 {} 个文件失败！！！".format(src_dir, len(lack_tag_file_list)))
        print("失败文件列表如下： ")
        for file in lack_tag_file_list:
            print(file)
    else:
        print("{} 清洗完成".format(src_dir))


if __name__ == '__main__':
    run()
