# Typora-uploader

Typora自定义图片上传服务

## Env

第三方库：

```shell
# 图像压缩
pip install Pillow

# 七牛云，可根据需求自行调整
# 七牛SDK-Python
pip install qiniu
```

## Usage

:one:clone代码到本地

:two:更新配置文件config.json

```json
{
  "access_key": "YOUR_ACCESS_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "bucket_name": "YOUR_BUKCET_NAME",
  "domain": "YOUR_DOMAIN",
  "path": "YOUR_PATH",
  "compress": true,
  "quality": 80
}
```

- access_key、secret_key：从对应的图床获取
- bucket_name：存储空间名称
- domain：存储空间绑定的域名
- path：上传到哪个文件夹，例如"images/"。为空则上传到存储空间根目录
- compress：上传前是否压缩。目前只支持`JPEG、JPG、PNG`压缩。
- quality：压缩质量。只对`JPEG、JPG`生效，有损压缩。而`PNG`采用无损压缩

:three:配置Typora

`文件->偏好设置`，选择`图像`，上传服务选择`Custom Command`，命令`python "your_local_path\typora-uploader.py"`。

<img src="https://qiniu.anburger.site/post/image-20250808112047535.png" alt="image-20250808112047535" style="zoom: 45%;" /><img src="https://qiniu.anburger.site/post/image-20250808112605560.png" alt="image-20250808112605560" style="zoom: 55%;" />

配置完成后，可以点击`验证图片上传选项`，它会上传两张默认图像进行测试。

:tada:Congratulations! Typora自定义上传服务配置完成。