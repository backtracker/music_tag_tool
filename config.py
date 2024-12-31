from opencc import OpenCC

# 设置简繁转换，如果不想转换，将IS_CC_CONVERT设置为False
# OpenCC  conversion ： 'hk2s', 's2hk', 's2t', 's2tw', 's2twp', 't2hk', 't2s', 't2tw', 'tw2s', and 'tw2sp'
cc = OpenCC('t2s')

IS_CC_CONVERT = True  # 是否需要opencc转换
IS_DELETE_SRC_EMPTY_DIR = True  # 是否清空源目录空文件夹
IS_KEEP_SRC_DIR_COVER = True  # 是否保留封面，根据文件名是"cover"判断封面
IS_MOVE_FILE_TO_TARGET_DIR = True  # 是否移动文件到目标目录

# 源目录
SRC_DIR = r"音乐修复\待整理"

# 目标目录
TARGET_DIR = r'音乐修复\已整理'


# 支持清洗的音乐类型
SUPPORT_MUSIC_TYPE = ['.flac', '.dsf']

# 创建目录中需要的专辑艺术家和专辑名，以及FLAC文件名，将不支持的字符替换为支持的字符
CHAR_REPLACE_DICT = {'.': '_', ':': '：', '?': '？', '"': '“', '|': ' ', '*': '', '<': '', '>': '', '\\': '', '/': ''}

# 需要删除的源文件中的文件后缀名，如果想要保留cover，则需要IS_KEEP_SRC_DIR_COVER设置为True
DELETE_FILE_SUFFIX_LIST = ['.cue', '.log', '.txt', '.m3u', '.m3u8', '.nfo', '.md5', '.jpg', '.png', '.tif', '.gif',
                           '.url']

# tag中需要删除的key
POP_KEY_LIST = {
    "FLAC": ['author', 'albumartistsort', 'artistsort', 'albumsort', 'arranger', "acoustid_id", "isrc",
             "length",
             "script", "originalyear", "originaldate", "barcode", "media", "releasecountry", "publisher",
             "label",
             "releasestatus", "id", "comment", "encoder", "performer", 'discid', 'ctdbtrackconfidence',
             'cdtoc', "album artist", "notes", 'gnid'],
    "DSF": ['TSO2', 'TSOP', 'TSRC', 'TMED']
}

# tag信息缺失文件列表
lack_tag_file_list = []
