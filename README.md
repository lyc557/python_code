# TCP端口转发工具

这是一个简单但功能强大的TCP端口转发工具，可以将本地端口的流量转发到指定的远程主机和端口。该工具使用Python编写，支持配置文件和命令行参数，适用于多种网络场景。

## 功能特点

- 支持本地端口到远程主机端口的TCP流量转发
- 支持配置文件和命令行参数两种配置方式
- 支持多客户端并发连接
- 实现了双向数据转发
- 优雅的错误处理和程序退出机制

## 主要应用场景

1. 访问内网服务：当需要从外部网络访问内部网络的服务时
2. 端口映射：将服务器上的高端口映射到低端口
3. 简单的负载均衡：将流量转发到不同的后端服务器

## 使用方法

### 独立可执行文件方式（无需Python环境）

我们提供了打包好的独立可执行文件，无需安装Python环境即可运行：

1. 从dist目录下载适合您系统的可执行文件：
   - macOS/Linux: `port_forward`
   - Windows: `port_forward.exe`

2. 直接运行可执行文件：
   - macOS/Linux: 在终端中运行 `./port_forward`
   - Windows: 双击 `port_forward.exe`

命令行参数使用方式：
```bash
# macOS/Linux
./port_forward -l <本地端口> -r <远程主机> -p <远程端口>

# Windows
port_forward.exe -l <本地端口> -r <远程主机> -p <远程端口>
```

### Python脚本方式

如果您已安装Python环境，也可以直接运行Python脚本：

1. 确保系统已安装Python 3.x版本
2. 克隆或下载本项目代码
3. 安装依赖包（如果有）：
   ```bash
   pip install -r requirements.txt
   ```

#### 命令行方式

基本命令格式：
```bash
python3 port_forward.py -l <本地端口> -r <远程主机> -p <远程端口>
```

参数说明：
- `-l, --local-port`：本地监听的端口号，如 8080
- `-r, --remote-host`：目标远程主机地址，如 localhost 或 10.0.0.1
- `-p, --remote-port`：目标远程主机端口号，如 80

使用示例：
1. 将本地8080端口转发到远程Web服务器：
   ```bash
   python3 port_forward.py -l 8080 -r example.com -p 80
   ```

2. 转发到本地其他端口：
   ```bash
   python3 port_forward.py -l 8080 -r localhost -p 3000
   ```

3. 转发到内网服务器：
   ```bash
   python3 port_forward.py -l 8080 -r 192.168.1.100 -p 8080
   ```

#### 配置文件方式

1. 创建或修改 `config.json` 文件：
```json
{
    "local_port": 9666,
    "remote_host": "127.0.0.1",
    "remote_port": 10088
}
```

2. 直接运行程序，它会自动加载配置文件：
```bash
# 独立可执行文件
./port_forward  # macOS/Linux
port_forward.exe  # Windows

# Python脚本
python3 port_forward.py
```

## 注意事项

1. 确保本地端口未被其他程序占用
2. 需要有适当的网络访问权限
3. 使用Ctrl+C可以优雅地终止程序
4. 如果配置文件不存在或格式错误，程序会使用默认配置

## 默认配置

如果没有提供命令行参数且配置文件不可用，程序将使用以下默认配置：
- 本地端口：9666
- 远程主机：localhost
- 远程端口：10088

## 错误处理

程序会处理以下常见错误：
- 端口被占用
- 远程服务器连接失败
- 配置文件读取错误
- 网络传输错误

## 许可证

本项目采用MIT许可证。欢迎使用和改进。