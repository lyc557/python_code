#!/usr/bin/env python3
"""
TCP端口转发工具

这是一个简单的TCP端口转发工具，可以将本地端口的流量转发到指定的远程主机和端口。
主要用于以下场景：
1. 访问内网服务：当您需要从外部网络访问内部网络的服务时
2. 端口映射：将服务器上的高端口映射到低端口
3. 简单的负载均衡：将流量转发到不同的后端服务器

使用方法：
    python3 port_forward.py -l <本地端口> -r <远程主机> -p <远程端口>

参数说明：
    -l, --local-port  : 本地监听的端口号，如 8080
    -r, --remote-host : 目标远程主机地址，如 localhost 或 10.0.0.1
    -p, --remote-port : 目标远程主机端口号，如 80

使用示例：
    1. 将本地8080端口转发到远程Web服务器：
       python3 port_forward.py -l 8080 -r example.com -p 80

    2. 转发到本地其他端口：
       python3 port_forward.py -l 9666 -r localhost -p 10088

    3. 转发到内网服务器：
       python3 port_forward.py -l 8080 -r 192.168.1.100 -p 8080

注意事项：
    1. 确保本地端口未被其他程序占用
    2. 需要有适当的网络访问权限
    3. 使用Ctrl+C可以优雅地终止程序
"""

import socket
import sys
import threading
import argparse
import json
import os
import time

# 添加以下代码确保在Windows环境下显示控制台窗口
def ensure_console_window():
    """确保在Windows环境下显示控制台窗口"""
    if sys.platform.startswith('win'):
        try:
            import ctypes
            # 获取控制台窗口句柄
            kernel32 = ctypes.WinDLL('kernel32')
            hwnd = kernel32.GetConsoleWindow()
            
            if hwnd == 0:  # 如果没有控制台窗口
                # 分配新的控制台
                kernel32.AllocConsole()
                
                # 重定向标准输入输出流
                sys.stdout = open('CONOUT$', 'w')
                sys.stderr = open('CONOUT$', 'w')
                sys.stdin = open('CONIN$', 'r')
        except Exception as e:
            print(f"无法创建控制台窗口: {e}")

def load_config(config_file='config.json'):
    """从配置文件加载参数
    
    参数:
        config_file: 配置文件路径，默认为'config.json'
    
    返回:
        包含配置参数的字典，如果配置文件不存在则返回默认值
    """
    default_config = {
        'local_port': 9666,
        'remote_host': 'localhost',
        'remote_port': 10088
    }
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            # 确保配置文件中包含所需的所有参数
            for key in default_config:
                if key not in config:
                    config[key] = default_config[key]
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"加载配置文件失败: {e}\n使用默认配置")
        return default_config

def main():
    """主函数
    
    功能:
        解析命令行参数并启动端口转发服务
        处理键盘中断信号，实现优雅退出
    """
    # 确保控制台窗口可见
    ensure_console_window()
    
    # 加载配置文件
    config = load_config()
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='简单的TCP端口转发工具')
    # 添加本地端口参数
    parser.add_argument('-l', '--local-port', type=int,
                        default=config['local_port'],
                        help='本地监听端口')
    # 添加远程主机地址参数
    parser.add_argument('-r', '--remote-host',
                        default=config['remote_host'],
                        help='远程主机地址')
    # 添加远程主机端口参数
    parser.add_argument('-p', '--remote-port', type=int,
                        default=config['remote_port'],
                        help='远程主机端口')

    # 解析命令行参数
    args = parser.parse_args()

    try:
        # 启动端口转发服务
        start_forwarder(args.local_port, args.remote_host, args.remote_port)
    except KeyboardInterrupt:
        print("\n程序已终止")
        sys.exit(0)

def handle_client(client_socket, remote_host, remote_port):
    """处理客户端连接并转发数据
    
    参数:
        client_socket: 与客户端建立的套接字连接
        remote_host: 目标远程主机地址
        remote_port: 目标远程主机端口
    
    功能:
        为每个客户端连接创建到远程服务器的连接，并建立双向数据转发通道
    """
    try:
        # 创建到远程服务器的连接
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        # 创建两个线程用于双向转发数据
        # 第一个线程负责从客户端到远程服务器的数据转发
        threading.Thread(target=forward_data, args=(client_socket, remote_socket), daemon=True).start()
        # 第二个线程负责从远程服务器到客户端的数据转发
        threading.Thread(target=forward_data, args=(remote_socket, client_socket), daemon=True).start()
    except Exception as e:
        print(f"连接远程服务器失败: {e}")
        client_socket.close()

def forward_data(source, destination):
    """转发数据的函数
    
    参数:
        source: 源套接字，用于接收数据
        destination: 目标套接字，用于发送数据
    
    功能:
        持续监听源套接字的数据，并将接收到的数据转发到目标套接字
        当连接断开或发生错误时自动关闭两个套接字
    """
    try:
        while True:
            # 从源套接字接收数据，最大接收4096字节
            data = source.recv(4096)
            if not data:  # 如果没有接收到数据，说明连接已断开
                break
            destination.send(data)  # 将数据发送到目标套接字
    except Exception as e:
        print(f"数据转发错误: {e}")
    finally:
        # 确保两个套接字都被正确关闭
        source.close()
        destination.close()

def start_forwarder(local_port, remote_host, remote_port):
    """启动端口转发服务
    
    参数:
        local_port: 本地监听端口
        remote_host: 目标远程主机地址
        remote_port: 目标远程主机端口
    
    功能:
        创建本地服务器并监听指定端口
        接受客户端连接并为每个连接创建独立的处理线程
    """
    try:
        # 创建服务器套接字
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置套接字选项，允许地址重用
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定到所有可用接口的指定端口
        server.bind(('0.0.0.0', local_port))
        # 开始监听连接，最大等待连接数为5
        server.listen(5)

        print(f"端口转发已启动: 本地端口 {local_port} -> {remote_host}:{remote_port}")

        while True:
            # 等待并接受新的客户端连接
            client_socket, addr = server.accept()
            print(f"新连接来自: {addr[0]}:{addr[1]}")
            # 为每个客户端创建新的处理线程
            threading.Thread(target=handle_client, 
                           args=(client_socket, remote_host, remote_port),
                           daemon=True).start()

    except Exception as e:
        print(f"服务器错误: {e}")
        sys.exit(1)
    finally:
        server.close()

if __name__ == '__main__':
    main()