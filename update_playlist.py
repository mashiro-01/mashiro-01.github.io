#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音乐播放列表更新脚本
使用方法：python update_playlist.py
功能：自动扫描 audios 文件夹并更新 index.html 中的音乐列表
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path


class PlaylistUpdater:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.audio_dir = self.script_dir / 'audios'
        self.index_file = self.script_dir / 'index.html'
        self.backup_dir = self.script_dir / 'backups'

    def create_backup(self):
        """创建备份"""
        self.backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = self.backup_dir / f'index.html.backup.{timestamp}'

        shutil.copy2(self.index_file, backup_path)
        print(f'✓ 备份已创建: {backup_path.name}')

    def scan_audio_files(self):
        """扫描音频文件夹"""
        if not self.audio_dir.exists():
            print('✗ audios 文件夹不存在！')
            return []

        mp3_files = sorted([f for f in self.audio_dir.iterdir() if f.suffix.lower() == '.mp3'])

        if not mp3_files:
            print('⚠ audios 文件夹中没有找到 MP3 文件')
            return []

        print(f'✓ 找到 {len(mp3_files)} 个音频文件:')
        for file in mp3_files:
            print(f'  - {file.name}')

        return mp3_files

    def generate_playlist_code(self, mp3_files):
        """生成音乐列表代码"""
        if not mp3_files:
            return ''

        lines = [f"						'audios/{file.name}'" for file in mp3_files]
        return ',\n'.join(lines)

    def update_index_html(self, mp3_files):
        """更新 index.html"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 生成新的播放列表代码
        new_playlist = f"""const musicFiles = [
{self.generate_playlist_code(mp3_files)}
					];"""

        # 查找并替换音乐列表
        pattern = r'const musicFiles = \[[\s\S]*?\];'
        match = re.search(pattern, content)

        if not match:
            print('✗ 无法在 index.html 中找到 musicFiles 数组！')
            return False

        content = re.sub(pattern, new_playlist, content)

        # 更新播放列表总数显示
        count_pattern = r'this\.playlistInfo\.textContent = `\$\{index \+ 1\} \/ \d+`;'
        new_count = f'this.playlistInfo.textContent = `${{index + 1}} / {len(mp3_files)}`;'
        content = re.sub(count_pattern, new_count, content)

        # 写回文件
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'✓ index.html 已更新，共 {len(mp3_files)} 首歌曲')
        return True

    def run(self):
        """主函数"""
        print('=== 音乐播放列表更新工具 ===\n')

        # 创建备份
        self.create_backup()

        # 扫描音频文件
        mp3_files = self.scan_audio_files()

        if not mp3_files:
            print('\n没有需要更新的文件')
            return

        # 更新 index.html
        if self.update_index_html(mp3_files):
            print('\n✓ 更新完成！')
            print('\n提示：如果出现问题，可以从 backups 文件夹恢复之前的版本')


if __name__ == '__main__':
    try:
        updater = PlaylistUpdater()
        updater.run()
    except Exception as e:
        print(f'\n✗ 发生错误: {e}')
        import traceback
        traceback.print_exc()
