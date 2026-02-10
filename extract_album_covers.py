#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频文件专辑封面提取脚本
功能：从 MP3/FLAC 等音频文件的元数据中提取专辑封面图片
使用方法：python extract_album_covers.py
依赖：pip install mutagen
"""

import os
import sys
from pathlib import Path

# 尝试导入 mutagen 库
try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, APIC, ID3NoHeaderError
    from mutagen.flac import FLAC
    from mutagen.mp4 import MP4
except ImportError:
    print('✗ 缺少依赖库')
    print('\n请先安装 mutagen 库：')
    print('  pip install mutagen')
    print('\n或者在 Windows 上运行：')
    print('  python -m pip install mutagen')
    sys.exit(1)


class AlbumCoverExtractor:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.audio_dir = self.script_dir / 'audios'
        self.cover_dir = self.audio_dir  # 封面保存在同一目录

    def extract_cover_from_mp3(self, mp3_path):
        """从 MP3 文件提取封面"""
        try:
            audio = MP3(mp3_path, ID3=ID3)

            if not audio.tags:
                print(f'  ⚠ {mp3_path.name}: 没有 ID3 标签')
                return False

            apic_frames = audio.tags.getall('APIC')

            if not apic_frames:
                print(f'  ⚠ {mp3_path.name}: 没有内嵌封面')
                return False

            apic = apic_frames[0]

            # 确定图片扩展名
            mime_type = apic.mime
            if mime_type in ['image/jpeg', 'image/jpg']:
                ext = 'jpg'
            elif mime_type == 'image/png':
                ext = 'png'
            elif mime_type == 'image/gif':
                ext = 'gif'
            else:
                ext = 'jpg'  # 默认

            mp3_name = mp3_path.stem
            cover_path = self.cover_dir / f'{mp3_name}.{ext}'

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

    def extract_cover_from_flac(self, flac_path):
        """从 FLAC 文件提取封面"""
        try:
            audio = FLAC(flac_path)

            if not audio.pictures:
                print(f'  ⚠ {flac_path.name}: 没有内嵌封面')
                return False

            # 获取第一张封面
            picture = audio.pictures[0]

            # 确定图片扩展名
            if picture.mime == 'image/jpeg':
                ext = 'jpg'
            elif picture.mime == 'image/png':
                ext = 'png'
            elif picture.mime == 'image/gif':
                ext = 'gif'
            else:
                ext = 'jpg'

            flac_name = flac_path.stem
            cover_path = self.cover_dir / f'{flac_name}.{ext}'

            with open(cover_path, 'wb') as f:
                f.write(picture.data)

            print(f'  ✓ {flac_path.name} → {cover_path.name}')
            return True

        except Exception as e:
            print(f'  ✗ {flac_path.name}: 提取失败 - {str(e)}')
            return False

    def extract_cover_from_mp4(self, mp4_path):
        """从 M4A/MP4 文件提取封面"""
        try:
            audio = MP4(mp4_path)

            # MP4 的封面存储在 'covr' 键中
            if 'covr' not in audio:
                print(f'  ⚠ {mp4_path.name}: 没有内嵌封面')
                return False

            cover_data = audio['covr'][0]

            mp4_name = mp4_path.stem
            cover_path = self.cover_dir / f'{mp4_name}.jpg'

            with open(cover_path, 'wb') as f:
                f.write(cover_data)

            print(f'  ✓ {mp4_path.name} → {cover_path.name}')
            return True

        except Exception as e:
            print(f'  ✗ {mp4_path.name}: 提取失败 - {str(e)}')
            return False

    def extract_cover(self, audio_path):
        """根据文件类型提取封面"""
        suffix = audio_path.suffix.lower()

        if suffix in ['.mp3', '.mp2', '.mp1']:
            return self.extract_cover_from_mp3(audio_path)
        elif suffix == '.flac':
            return self.extract_cover_from_flac(audio_path)
        elif suffix in ['.m4a', '.m4b', '.m4p', '.mp4']:
            return self.extract_cover_from_mp4(audio_path)
        else:
            print(f'  ⚠ {audio_path.name}: 不支持的格式 ({suffix})')
            return False

    def extract_all_covers(self):
        """提取所有音频文件的封面"""
        if not self.audio_dir.exists():
            print(f'✗ audios 文件夹不存在：{self.audio_dir}')
            return

        # 查找所有支持的音频文件
        audio_extensions = ['mp3', 'MP3', 'flac', 'FLAC', 'm4a', 'M4A', 'ogg', 'OGG', 'wav', 'WAV']
        audio_files = []

        for ext in audio_extensions:
            audio_files.extend(self.audio_dir.glob(f'*.{ext}'))

        # 去重（Windows 不区分大小写，可能导致重复）
        seen = set()
        unique_files = []
        for f in audio_files:
            # 使用小写路径作为唯一标识
            lower_path = str(f).lower()
            if lower_path not in seen:
                seen.add(lower_path)
                unique_files.append(f)

        audio_files = unique_files

        if not audio_files:
            print('✗ audios 文件夹中没有找到支持的音频文件')
            return

        print(f'=== 专辑封面提取工具 ===')
        print(f'支持的格式: MP3, FLAC, M4A, OGG, WAV')
        print(f'找到 {len(audio_files)} 个音频文件\n')

        success_count = 0
        fail_count = 0

        for audio_file in audio_files:
            if self.extract_cover(audio_file):
                success_count += 1
            else:
                fail_count += 1

        print(f'\n=== 提取完成 ===')
        print(f'✓ 成功: {success_count} 个')
        print(f'✗ 失败: {fail_count} 个')


def main():
    # 运行提取器
    extractor = AlbumCoverExtractor()
    extractor.extract_all_covers()

    print('\n提示：')
    print('- 提取的封面图片保存在 audios 文件夹中')
    print('- 封面文件名与音频文件名相同')
    print('- 支持的音频格式：MP3, FLAC, M4A, OGG, WAV')


if __name__ == '__main__':
    main()
