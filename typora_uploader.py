# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import json
import sys
import os
import tempfile
from qiniu import Auth, put_file
from PIL import Image

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("错误：找不到配置文件 config.json")
        sys.exit(1)
    except json.JSONDecodeError:
        print("错误：配置文件 config.json 格式不正确")
        sys.exit(1)

def compress_image(file_path, quality=80):
    """压缩图片，保持原格式，并返回临时文件路径"""
    try:
        img = Image.open(file_path)
        original_format = img.format or 'JPEG' # 如果格式未知，默认为JPEG
        
        # 获取原始文件扩展名
        _, ext = os.path.splitext(file_path)
        if not ext: # 如果没有扩展名，根据图片格式来定
            ext = f".{original_format.lower()}"

        # 创建一个与原文件同扩展名的临时文件
        temp_fd, temp_path = tempfile.mkstemp(suffix=ext)
        os.close(temp_fd)

        # 根据不同格式应用不同压缩参数
        save_options = {}
        if original_format in ['JPEG', 'JPG']:
            save_options['quality'] = quality
            save_options['format'] = 'JPEG'
        elif original_format == 'PNG':
            save_options['optimize'] = True # 无损压缩
            save_options['format'] = 'PNG'
        else: # 其他格式（如GIF, WEBP等）直接保存
            save_options['format'] = original_format

        img.save(temp_path, **save_options)
        return temp_path
    except Exception as e:
        print(f"压缩图片失败: {e}")
        # 如果压缩失败，返回原图路径，避免上传中断
        return file_path

def upload_to_qiniu(access_key, secret_key, bucket_name, domain, file_to_upload, original_filename, remote_path=""):
    """上传单个文件到七牛云"""
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 使用原始文件名构建在七牛云上保存的 key
    key = f"{remote_path}{original_filename}" if remote_path else original_filename

    # 生成上传 Token
    token = q.upload_token(bucket_name, key, 3600)

    # 上传处理后（可能被压缩）的文件
    ret, info = put_file(token, key, file_to_upload)

    if ret is not None and ret['key'] == key:
        # 上传成功，返回 URL
        # 确保域名末尾没有 /，路径开头没有 /
        return f"{domain.rstrip('/')}/{key.lstrip('/')}"
    else:
        # 上传失败
        print(f"上传失败: {info}")
        return None

def main():
    """主函数"""
    # 从命令行参数获取图片路径
    image_paths = sys.argv[1:]

    if not image_paths:
        print("没有需要上传的图片。")
        print("用法: python typora_uploader.py [image_path1] [image_path2] ...")
        sys.exit(1)

    # 加载配置
    config = load_config()
    access_key = config.get('access_key')
    secret_key = config.get('secret_key')
    bucket_name = config.get('bucket_name')
    domain = config.get('domain')
    remote_path = config.get('path', '') # 默认为空字符串
    compress = config.get('compress', False) # 默认不压缩
    quality = config.get('quality', 80) # 默认压缩质量为80

    if not all([access_key, secret_key, bucket_name, domain]):
        print("错误：配置文件不完整，请检查 access_key, secret_key, bucket_name, domain 是否都已配置。")
        sys.exit(1)
        
    if "YOUR_ACCESS_KEY" in access_key:
        print("请先在 config.json 中配置您的七牛云信息。")
        sys.exit(1)

    uploaded_urls = []
    for img_path in image_paths:
        if not os.path.exists(img_path):
            print(f"警告：文件不存在，跳过 {img_path}")
            continue
        
        file_to_upload = img_path
        temp_file_to_delete = None
        original_filename = os.path.basename(img_path)

        if compress:
            compressed_path = compress_image(img_path, quality)
            # 只有当压缩成功且生成了新文件时才更新
            if compressed_path and compressed_path != img_path:
                file_to_upload = compressed_path
                temp_file_to_delete = compressed_path
        
        url = upload_to_qiniu(access_key, secret_key, bucket_name, domain, file_to_upload, original_filename, remote_path)
        if url:
            uploaded_urls.append(url)
        
        # 清理临时文件
        if temp_file_to_delete:
            os.remove(temp_file_to_delete)

    # Typora 要求将上传后的 URL 打印到标准输出
    if uploaded_urls:
        print("\n".join(uploaded_urls))

if __name__ == '__main__':
    main()
