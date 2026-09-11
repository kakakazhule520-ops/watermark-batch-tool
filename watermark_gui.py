#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import zipfile
import threading
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import scrolledtext


class WatermarkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 批量图片水印工具 v1.0")
        self.root.geometry("800x900")
        self.root.resizable(True, True)
        
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.supported_formats = ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp']
        self.watermark_styles = {
            '紧迫感': {'position': 'bottom_right', 'color': (255, 0, 0), 'angle': 0},
            '优雅感': {'position': 'center', 'color': (200, 200, 200), 'angle': -45},
            '警告感': {'position': 'top_left', 'color': (255, 255, 0), 'angle': 0},
            '品牌感': {'position': 'bottom_center', 'color': (100, 100, 100), 'angle': 0}
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="🎨 批量图片水印工具", font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # 主容器
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 左侧配置面板
        left_frame = ttk.LabelFrame(main_frame, text="⚙️ 配置设置", padding=15)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 源文件夹选择
        ttk.Label(left_frame, text="📁 源文件夹：", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar(value="选择包含图片的文件夹...")
        source_btn = ttk.Button(left_frame, text="🔍 浏览", command=self.select_source_folder)
        source_btn.grid(row=0, column=1, sticky=tk.E, pady=5)
        ttk.Label(left_frame, textvariable=self.source_var, foreground="blue").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        # 输出文件夹选择
        ttk.Label(left_frame, text="📤 输出文件夹：", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value="选择输出文件夹...")
        output_btn = ttk.Button(left_frame, text="🔍 浏览", command=self.select_output_folder)
        output_btn.grid(row=2, column=1, sticky=tk.E, pady=5)
        ttk.Label(left_frame, textvariable=self.output_var, foreground="blue").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=3)
        
        # 水印文字
        ttk.Label(left_frame, text="📝 水印文字：", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.watermark_text = ttk.Entry(left_frame, width=30)
        self.watermark_text.insert(0, f"© {datetime.now().year}")
        self.watermark_text.grid(row=4, column=1, sticky=tk.EW, pady=5)
        
        # 水印样式
        ttk.Label(left_frame, text="🎨 水印样式：", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky=tk.W, pady=5)
        self.style_var = tk.StringVar(value="紧迫感")
        style_combo = ttk.Combobox(left_frame, textvariable=self.style_var, 
                                   values=list(self.watermark_styles.keys()), state="readonly", width=27)
        style_combo.grid(row=5, column=1, sticky=tk.EW, pady=5)
        
        # 水印大小
        ttk.Label(left_frame, text="📏 水印大小：", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=5)
        size_frame = ttk.Frame(left_frame)
        size_frame.grid(row=6, column=1, sticky=tk.EW, pady=5)
        
        self.size_var = tk.StringVar(value="50")
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, 
                                  values=["30 (小)", "50 (中)", "80 (大)"], state="readonly", width=12)
        size_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(size_frame, text="px").pack(side=tk.LEFT, padx=5)
        
        # 透明度
        ttk.Label(left_frame, text="💧 透明度：", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=5)
        alpha_frame = ttk.Frame(left_frame)
        alpha_frame.grid(row=7, column=1, sticky=tk.EW, pady=5)
        
        self.alpha_var = tk.StringVar(value="179")
        alpha_combo = ttk.Combobox(alpha_frame, textvariable=self.alpha_var, 
                                   values=["128 (低)", "179 (中)", "230 (高)"], state="readonly", width=12)
        alpha_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(alpha_frame, text="(0-255)").pack(side=tk.LEFT, padx=5)
        
        # 输出格式
        ttk.Label(left_frame, text="🖼️  输出格式：", font=("Arial", 10, "bold")).grid(row=8, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="原格式")
        format_combo = ttk.Combobox(left_frame, textvariable=self.format_var, 
                                    values=["PNG", "JPG", "原格式"], state="readonly", width=27)
        format_combo.grid(row=8, column=1, sticky=tk.EW, pady=5)
        
        # 跳过第一张
        self.skip_first_var = tk.BooleanVar(value=True)
        skip_cb = ttk.Checkbutton(left_frame, text="⏭️  跳过每个文件夹的第一张图片", variable=self.skip_first_var)
        skip_cb.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 右侧日志面板
        right_frame = ttk.LabelFrame(main_frame, text="📋 处理日志", padding=15)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(right_frame, height=30, width=40, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部按钮
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="🚀 开始处理", command=self.start_processing)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(button_frame, text="🗑️  清空日志", command=lambda: self.log_text.delete(1.0, tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = ttk.Button(button_frame, text="❌ 退出", command=self.root.quit)
        quit_btn.pack(side=tk.RIGHT, padx=5)
        
        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=5)
        
        # 配置grid权重
        left_frame.columnconfigure(1, weight=1)
    
    def log(self, message):
        """添加日志消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def select_source_folder(self):
        """选择源文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        if folder:
            self.source_var.set(folder)
            self.log(f"✅ 已选择源文件夹: {folder}")
    
    def select_output_folder(self):
        """选择输出文件夹"""
        folder = filedialog.askdirectory(title="选择输出文件夹")
        if folder:
            self.output_var.set(folder)
            self.log(f"✅ 已选择输出文件夹: {folder}")
    
    def get_watermark_settings(self):
        """获取水印设置"""
        size_str = self.size_var.get().split()[0]
        alpha_str = self.alpha_var.get().split()[0]
        
        return {
            'text': self.watermark_text.get(),
            'font_size': int(size_str),
            'alpha': int(alpha_str),
            'style': self.style_var.get(),
            'output_format': None if self.format_var.get() == "原格式" else self.format_var.get().lower(),
            'skip_first': self.skip_first_var.get()
        }
    
    def add_watermark(self, image_path, output_path, watermark_settings):
        """给图片添加水印"""
        try:
            img = Image.open(image_path).convert('RGBA')
            txt_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
            txt_draw = ImageDraw.Draw(txt_layer)
            
            config = self.watermark_styles[watermark_settings['style']]
            
            font_size = watermark_settings['font_size']
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            text = watermark_settings['text']
            bbox = txt_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
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
            color = config['color'] + (watermark_settings['alpha'],)
            txt_draw.text(position, text, font=font, fill=color)
            
            img = Image.alpha_composite(img, txt_layer)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            output_format = watermark_settings['output_format']
            if output_format:
                output_path = os.path.splitext(output_path)[0] + f'.{output_format}'
            
            img.save(output_path, quality=95)
            return True
        except Exception as e:
            self.log(f"❌ 处理失败: {e}")
            return False
    
    def process_folder(self, folder_path, watermark_settings, output_folder):
        """处理单个文件夹"""
        self.log(f"\n📂 处理文件夹: {os.path.basename(folder_path)}")
        
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(Path(folder_path).glob(f'*.{ext}'))
            image_files.extend(Path(folder_path).glob(f'*.{ext.upper()}'))
        
        image_files = sorted(set(image_files))
        
        if not image_files:
            self.log(f"⚠️  文件夹内没有找到支持的图片格式")
            return None
        
        self.log(f"找到 {len(image_files)} 张图片")
        
        temp_folder = f"{folder_path}_watermarked_temp"
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
        os.makedirs(temp_folder)
        
        processed_count = 0
        
        for idx, image_file in enumerate(image_files):
            if idx == 0 and watermark_settings['skip_first']:
                self.log(f"⏭️  跳过第一张: {image_file.name}")
                shutil.copy(image_file, os.path.join(temp_folder, image_file.name))
                continue
            
            output_path = os.path.join(temp_folder, image_file.name)
            status = self.add_watermark(str(image_file), output_path, watermark_settings)
            
            if status:
                processed_count += 1
                self.log(f"✅ {image_file.name}")
            else:
                self.log(f"❌ {image_file.name}")
        
        # 创建ZIP
        self.log(f"📦 创建压缩包...")
        zip_path = os.path.join(output_folder, f"{os.path.basename(folder_path)}_watermarked.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(temp_folder):
                file_path = os.path.join(temp_folder, file)
                arcname = os.path.join(os.path.basename(folder_path), file)
                zipf.write(file_path, arcname)
        
        self.log(f"✅ 压缩包已保存: {zip_path}")
        shutil.rmtree(temp_folder)
        
        return zip_path
    
    def start_processing(self):
        """开始处理"""
        source = self.source_var.get()
        output = self.output_var.get()
        
        if source == "选择包含图片的文件夹..." or output == "选择输出文件夹...":
            messagebox.showerror("错误", "请先选择源文件夹和输出文件夹！")
            return
        
        if not os.path.isdir(source):
            messagebox.showerror("错误", "源文件夹不存在！")
            return
        
        if not os.path.isdir(output):
            messagebox.showerror("错误", "输出文件夹不存在！")
            return
        
        self.start_btn.config(state=tk.DISABLED)
        self.progress.start()
        
        # 在线程中处理以避免界面卡顿
        thread = threading.Thread(target=self.process_thread, args=(source, output))
        thread.start()
    
    def process_thread(self, source, output):
        """处理线程"""
        try:
            self.log("="*50)
            self.log("🚀 开始处理")
            self.log("="*50)
            
            watermark_settings = self.get_watermark_settings()
            
            # 检查源是否是单个文件夹还是包含多个文件夹
            folders_to_process = []
            
            # 检查源文件夹中是否有图片
            has_images = False
            for ext in self.supported_formats:
                if list(Path(source).glob(f'*.{ext}')) or list(Path(source).glob(f'*.{ext.upper()}')):
                    has_images = True
                    break
            
            if has_images:
                # 源文件夹本身包含图片
                folders_to_process = [source]
            else:
                # 查找源文件夹内的子文件夹
                for item in os.listdir(source):
                    item_path = os.path.join(source, item)
                    if os.path.isdir(item_path):
                        folders_to_process.append(item_path)
            
            if not folders_to_process:
                self.log("❌ 未找到包含图片的文件夹")
            else:
                for folder in folders_to_process:
                    self.process_folder(folder, watermark_settings, output)
            
            self.log("\n" + "="*50)
            self.log("✅ 所有任务完成！")
            self.log(f"📂 输出文件夹: {output}")
            self.log("="*50)
            
            messagebox.showinfo("完成", "所有图片处理完成！\n压缩包已保存到输出文件夹。")
        
        except Exception as e:
            self.log(f"❌ 处理出错: {e}")
            messagebox.showerror("错误", f"处理出错: {e}")
        
        finally:
            self.progress.stop()
            self.start_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkGUI(root)
    root.mainloop()
