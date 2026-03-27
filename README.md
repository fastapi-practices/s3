## S3

此插件提供了兼容 S3 协议的存储能力，支持多存储配置动态管理。

### 依赖

使用 uv：

```bash
uv add opendal
```

### 使用步骤

#### 第一步：创建 S3 存储配置

```http
POST /api/v1/s3/storages
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "MinIO本地",
  "endpoint": "http://192.168.1.100:9000",
  "access_key": "minioadmin",
  "secret_key": "minioadmin",
  "bucket": "my-bucket",
  "prefix": null,
  "region": "us-east-1"
}
```

#### 第二步：上传文件

```http
POST /api/v1/s3/files/upload?storage=1
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <文件>
```

返回示例：
```json
{
  "code": 200,
  "data": {
    "url": "/my-bucket/filename.pdf"
  }
}
```

### 配置字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| name | ✓ | 存储名称 |
| endpoint | ✓ | S3 服务地址 |
| access_key | ✓ | Access Key ID |
| secret_key | ✓ | Secret Access Key |
| bucket | ✓ | 存储桶名称 |
| prefix | | 文件前缀/路径 |
| region | | 区域，MinIO 默认 `us-east-1` |
| remark | | 备注说明 |

### API 接口

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | /api/v1/s3/storages | 分页获取存储列表 | 登录即可 |
| GET | /api/v1/s3/storages/all | 获取所有存储 | 登录即可 |
| GET | /api/v1/s3/storages/{id} | 获取存储详情 | 登录即可 |
| POST | /api/v1/s3/storages | 创建存储 | s3:storage:add |
| PUT | /api/v1/s3/storages/{id} | 更新存储 | s3:storage:edit |
| DELETE | /api/v1/s3/storages | 批量删除存储 | s3:storage:del |
| POST | /api/v1/s3/files/upload | 上传文件 | s3:file:upload |

### 权限配置

需要在菜单权限中添加以下权限码：

- `s3:storage:add` - 创建存储
- `s3:storage:edit` - 编辑存储
- `s3:storage:del` - 删除存储
- `s3:file:upload` - 上传文件

### 支持的存储服务

- AWS S3
- 阿里云 OSS
- 腾讯云 COS
- MinIO
- Cloudflare R2
- 其他兼容 S3 协议的服务

### MinIO 配置示例

```json
{
  "name": "MinIO本地",
  "endpoint": "http://192.168.1.100:9000",
  "access_key": "minioadmin",
  "secret_key": "minioadmin",
  "bucket": "my-bucket",
  "region": "us-east-1"
}
```

### 阿里云 OSS 配置示例

```json
{
  "name": "阿里云OSS",
  "endpoint": "https://oss-cn-hangzhou.aliyuncs.com",
  "access_key": "your_access_key_id",
  "secret_key": "your_secret_access_key",
  "bucket": "my-bucket",
  "region": "cn-hangzhou"
}
```

### 腾讯云 COS 配置示例

```json
{
  "name": "腾讯云COS",
  "endpoint": "https://cos.ap-guangzhou.myqcloud.com",
  "access_key": "your_secret_id",
  "secret_key": "your_secret_key",
  "bucket": "my-bucket-1250000000",
  "region": "ap-guangzhou"
}
```
