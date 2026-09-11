#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from datetime import datetime


class WatermarkTool:
    def __init__(self):
        self.supported_formats = ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp']
        self.watermark_styles = {
            '1': '紧迫感',
            '2': '优雅感',
            '3': '警告感',
            '4': '品牌感'
        }
        
    def get_folder_list(self):
        """获取当前目录下的所有文件夹"""
        folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
        return sorted(folders)
    
    def select_folders(self):
        """交互式选择要处理的文件夹"""
        folders = self.get_folder_list()
        
        if not folders:
            print("❌ 当前目录下没有找到文件夹")
            return []
        
        print("\n📁 找到的文件夹列表：")
        for idx, folder in enumerate(folders, 1):
            print(f"  {idx}. {folder}")
        
        print("\n请输入要处理的文件夹编号（用逗号分隔，如：1,3,5 或输入 'all' 处理全部）")
        choice = input(">>> ").strip()
        
        selected = []
        if choice.lower() == 'all':
            selected = folders
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                selected = [folders[i] for i in indices if 0 <= i < len(folders)]
            except (ValueError, IndexError):
                print("❌ 输入格式错误")
                return []
        
        return selected
    
    def select_watermark_settings(self):
        """选择水印设置"""
        print("\n" + "="*50)
        print("🎨 水印设置")
        print("="*50)
        
        # 选择水印样式
        print("\n选择水印样式：")
        for key, value in self.watermark_styles.items():
            print(f"  {key}. {value}")
        
        style_choice = input("请选择（1-4）>>> ").strip()
        watermark_style = self.watermark_styles.get(style_choice, '紧迫感')
        
        # 输入水印文字
        watermark_text = input(f"\n输入水印文字（当前样式：{watermark_style}）>>> ").strip()
        if not watermark_text:
            watermark_text = f"© {datetime.now().year}"
        
        # 选择水印大小
        print("\n水印大小选择：")
        print("  1. 小 (30px)")
        print("  2. 中 (50px)")
        print("  3. 大 (80px)")
        print("  4. 自定义")
        
        size_choice = input("请选择（1-4）>>> ").strip()
        size_map = {'1': 30, '2': 50, '3': 80}
        if size_choice == '4':
            try:
                font_size = int(input("输入字体大小（像素）>>> ").strip())
            except ValueError:
                font_size = 50
        else:
            font_size = size_map.get(size_choice, 50)
        
        # 选择透明度
        print("\n透明度选择：")
        print("  1. 低 (50%)")
        print("  2. 中 (70%)")
        print("  3. 高 (90%)")
        print("  4. 自定义")
        
        alpha_choice = input("请选择（1-4）>>> ").strip()
        alpha_map = {'1': 128, '2': 179, '3': 230}
        if alpha_choice == '4':
            try:
                alpha = int(input("输入透明度（0-255，0为完全透明）>>> ").strip())
                alpha = max(0, min(255, alpha))
            except ValueError:
                alpha = 179
        else:
            alpha = alpha_map.get(alpha_choice, 179)
        
        # 选择输出格式
        print("\n输出格式选择：")
        print("  1. PNG")
        print("  2. JPG")
        print("  3. 保持原格式")
        
        format_choice = input("请选择（1-3）>>> ").strip()
        output_format = {'1': 'png', '2': 'jpg', '3': None}.get(format_choice, None)
        
        return {
            'text': watermark_text,
            'font_size': font_size,
            'alpha': alpha,
            'style': watermark_style,
            'output_format': output_format
        }
    
    def get_watermark_position_and_color(self, style):
        """根据样式获取水印位置和颜色"""
        style_config = {
            '紧迫感': {
                'position': 'bottom_right',
                'color': (255, 0, 0),  # 红色
                'angle': 0
            },
            '优雅感': {
                'position': 'center',
                'color': (200, 200, 200),  # 灰色
                'angle': -45
            },
            '警告感': {
                'position': 'top_left',
                'color': (255, 255, 0),  # 黄色
                'angle': 0
            },
            '品牌感': {
                'position': 'bottom_center',
                'color': (100, 100, 100),  # 深灰色
                'angle': 0
            }
        }
        return style_config.get(style, style_config['紧迫感'])
    
    def add_watermark(self, image_path, output_path, watermark_settings):
        """给单张图片添加水印"""
        try:
            # 打开图片
            img = Image.open(image_path).convert('RGBA')
            
            # 创建透明层用于绘制水印
            txt_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_layer)
            
            # 获取样式配置
            config = self.get_watermark_position_and_color(watermark_settings['style'])
            
            # 尝试使用系统字体，如果不存在则使用默认字体
            font_size = watermark_settings['font_size']
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # 获取文本尺寸
            text = watermark_settings['text']
            bbox = txt_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 确定水印位置
            img_width, img_height = img.size
            position_map = {
                'top_left': (10, 10),
                'top_right': (img_width - text_width - 10, 10),
                'bottom_left': (10, img_height - text_height - 10),
                'bottom_right': (img_width - text_width - 10, img_height - text_height - 10),
                'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
                'bottom_center': ((img_width - text_width) // 2, img_height - text_height - 10)
            }
            
            position = position_map.get(config['position'], position_map['bottom_right'])
            
            # 绘制水印文字
            color = config['color'] + (watermark_settings['alpha'],)
            txt_draw.text(position, text, font=font, fill=color)
            
            # 合并图层
            img = Image.alpha_composite(img, txt_layer)
            
            # 转换回原始模式
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # 保存图片
            output_format = watermark_settings['output_format']
            if output_format:
                output_path = os.path.splitext(output_path)[0] + f'.{output_format}'
            
            img.save(output_path, quality=95)
            return True
        except Exception as e:
            print(f"  ❌ 处理失败：{e}")
            return False
    
    def process_folder(self, folder_path, watermark_settings):
        """处理单个文件夹内的所有图片"""
        print(f"\n📂 处理文件夹: {folder_path}")
        
        # 获取所有图片文件
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(Path(folder_path).glob(f'*.{ext}'))
            image_files.extend(Path(folder_path).glob(f'*.{ext.upper()}'))
        
        image_files = sorted(set(image_files))  # 去重并排序
        
        if not image_files:
            print(f"  ⚠️  文件夹内没有找到支持的图片格式")
            return []
        
        print(f"  找到 {len(image_files)} 张图片")
        
        # 创建临时文件夹
        temp_folder = f"{folder_path}_watermarked_temp"
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)
        
        processed_files = []
        
        # 处理图片（跳过第一张）
        for idx, image_file in enumerate(image_files):
            if idx == 0:
                print(f"  ⏭️  跳过第一张: {image_file.name}")
                shutil.copy(image_file, os.path.join(temp_folder, image_file.name))
                processed_files.append(image_file.name)
                continue
            
            output_path = os.path.join(temp_folder, image_file.name)
            status = self.add_watermark(str(image_file), output_path, watermark_settings)
            
            if status:
                processed_files.append(image_file.name)
                print(f"  ✅ {image_file.name}")
            else:
                print(f"  ❌ {image_file.name}")
        
        return temp_folder, processed_files
    
    def create_zip(self, temp_folder, output_path, folder_name):
        """创建ZIP压缩包"""
        zip_path = os.path.join(output_path, f"{folder_name}_watermarked.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(temp_folder):
                file_path = os.path.join(temp_folder, file)
                arcname = os.path.join(folder_name, file)
                zipf.write(file_path, arcname)
        
        return zip_path
    
    def select_output_folder(self):
        """选择输出文件夹"""
        print("\n" + "="*50)
        print("📤 输出设置")
        print("="*50)
        
        folders = [f for f in os.listdir('.') if os.path.isdir(f) and not f.startswith('.')]
        folders.insert(0, '创建新文件夹')
        
        print("\n输出文件夹选择：")
        for idx, folder in enumerate(folders, 1):
            print(f"  {idx}. {folder}")
        
        choice = input("请选择（或输入自定义路径）>>> ").strip()
        
        try:
            idx = int(choice) - 1
            if idx == -1:
                output_folder = input("输入新文件夹名称 >>> ").strip()
                if not output_folder:
                    output_folder = "watermarked_output"
            else:
                output_folder = folders[idx]
        except ValueError:
            output_folder = choice if choice else "watermarked_output"
        
        os.makedirs(output_folder, exist_ok=True)
        return output_folder
    
    def run(self):
        """主程序"""
        print("\n" + "="*50)
        print("🎨 批量图片水印工具 v1.0")
        print("="*50)
        
        # 选择文件夹
        selected_folders = self.select_folders()
        if not selected_folders:
            print("❌ 没有选择任何文件夹")
            return
        
        # 选择水印设置
        watermark_settings = self.select_watermark_settings()
        
        # 选择输出文件夹
        output_folder = self.select_output_folder()
        
        print("\n" + "="*50)
        print("🚀 开始处理")
        print("="*50)
        
        # 处理每个文件夹
        for folder in selected_folders:
            result = self.process_folder(folder, watermark_settings)
            if result:
                temp_folder, processed_files = result
                
                # 创建ZIP文件
                print(f"  📦 创建压缩包...")
                zip_path = self.create_zip(temp_folder, output_folder, folder)
                print(f"  ✅ 压缩包已保存: {zip_path}")
                
                # 清理临时文件夹
                shutil.rmtree(temp_folder)
        
        print("\n" + "="*50)
        print("✅ 所有任务完成！")
        print(f"📂 输出文件夹: {output_folder}")
        print("="*50 + "\n")


if __name__ == "__main__":
    tool = WatermarkTool()
    tool.run()
