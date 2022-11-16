import json
import os

from aff_convertor import convert
from utils.file_reader import json_reader, process_directory


def songlist_song(songlist, index):
    song = songlist['songs'][index]
    return song


def packlist_song(packlist, index):
    pack = packlist['packs'][index]
    return pack


if __name__ == '__main__':
    songlist = json_reader('./sum/songlist')
    packlist = json_reader('./sum/packlist')
    # 目录预处理
    process_directory(songlist)
    index = 278
    difficulty = 3
    # 输出目录
    path = './pentiment'
    # 输出文件名前缀
    prefix = 'pentiment'
    # 转换aff文件
    convert(songlist['songs'][index], difficulty, path, prefix)
