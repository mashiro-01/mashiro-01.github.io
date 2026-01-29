#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MP3 专辑封面提取脚本
功能：从 MP3 文件的 ID3 标签中提取专辑封面图片
使用方法：python extract_album_covers.py
依赖：pip install mutagen
"""

import os
import sys
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, ID3NoHeaderError


class AlbumCoverExtractor:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.audio_dir = self.script_dir / 'audios'
        self.cover_dir = self.audio_dir  # 封面保存在同一目录

    def extract_cover_from_mp3(self, mp3_path):
        """从单个 MP3 文件提取封面"""
        try:
            # 读取 MP3 文件
            audio = MP3(mp3_path, ID3=ID3)

            # 检查是否有 ID3 标签
            if not audio.tags:
                print(f'  ⚠ {mp3_path.name}: 没有 ID3 标签')
                return False

            # 查找 APIC 帧（专辑封面）
            apic_frames = audio.tags.getall('APIC')

            if not apic_frames:
                print(f'  ⚠ {mp3_path.name}: 没有内嵌封面')
                return False

            # 获取第一个封面（通常只有一个）
            apic = apic_frames[0]

            # 确定图片扩展名
            mime_type = apic.mime
            if mime_type == 'image/jpeg' or mime_type == 'image/jpg':
                ext = 'jpg'
            elif mime_type == 'image/png':
                ext = 'png'
            elif mime_type == 'image/gif':
                ext = 'gif'
            else:
                ext = 'jpg'  # 默认

            # 生成封面文件名（与 MP3 文件同名）
            mp3_name = mp3_path.stem  # 不含扩展名的文件名
            cover_path = self.cover_dir / f'{mp3_name}.{ext}'

            # 保存封面图片
            with open(cover_path, 'wb') as f:
                f.write(apic.data)

            print(f'  ✓ {mp3_path.name} → {cover_path.name}')
            return True

        except ID3NoHeaderError:
            print(f'  ✗ {mp3_path.name}: 不是有效的 MP3 文件')
            return False
        except Exception as e:
            print(f'  ✗ {mp3_path.name}: 提取失败 - {str(e)}')
            return False

    def extract_all_covers(self):
        """提取所有 MP3 文件的封面"""
        if not self.audio_dir.exists():
            print(f'✗ audios 文件夹不存在：{self.audio_dir}')
            return

        # 查找所有 MP3 文件（统一转为小写去重）
        mp3_files = list(self.audio_dir.glob('*.mp3')) + list(self.audio_dir.glob('*.MP3'))

        # 去重（Windows 不区分大小写，可能导致重复）
        seen = set()
        unique_files = []
        for f in mp3_files:
            # 使用小写路径作为唯一标识
            lower_path = str(f).lower()
            if lower_path not in seen:
                seen.add(lower_path)
                unique_files.append(f)

        mp3_files = unique_files

        if not mp3_files:
            print('✗ audios 文件夹中没有找到 MP3 文件')
            return

        print(f'=== 专辑封面提取工具 ===')
        print(f'找到 {len(mp3_files)} 个 MP3 文件\n')

        success_count = 0
        fail_count = 0

        for mp3_file in mp3_files:
            if self.extract_cover_from_mp3(mp3_file):
                success_count += 1
            else:
                fail_count += 1

        print(f'\n=== 提取完成 ===')
        print(f'✓ 成功: {success_count} 个')
        print(f'✗ 失败: {fail_count} 个')


def main():
    # 检查依赖
    try:
        import mutagen
    except ImportError:
        print('✗ 缺少依赖库')
        print('\n请先安装 mutagen 库：')
        print('  pip install mutagen')
        print('\n或者在 Windows 上运行：')
        print('  python -m pip install mutagen')
        sys.exit(1)

    # 运行提取器
    extractor = AlbumCoverExtractor()
    extractor.extract_all_covers()


if __name__ == '__main__':
    main()
