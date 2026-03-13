# 贪吃蛇 Snake Game

一款画面精美、操作流畅的贪吃蛇游戏，支持简体中文界面。

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)

## 功能特性

- **经典玩法**: 延续经典贪吃蛇游戏操作方式
- **精美界面**: 现代化设计，带有动画效果和渐变色
- **简体中文**: 全界面简体中文支持
- **高分系统**: 记录并保存最高分
- **速度递增**: 随着分数增加，游戏速度逐渐加快
- **跨平台**: 支持 Windows、Linux、macOS 系统

## 操作说明

| 按键 | 功能 |
|------|------|
| 方向键 | 控制蛇的移动方向 |
| P 键 | 暂停/继续游戏 |
| Enter / 空格 | 开始游戏 / 重新开始 |
| ESC | 退出游戏 |

## 运行游戏

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/ganecheng-ai/snake-m25.git
cd snake-m25

# 安装依赖
pip install pygame

# 运行游戏
python src/main.py
```

### 下载预构建版本

前往 [Releases](https://github.com/ganecheng-ai/snake-m25/releases) 页面下载对应平台的预构建版本：

- **Windows**: `.exe` 可执行文件
- **Linux**: `.tar.gz` 压缩包
- **macOS**: `.tar.gz` 压缩包

## 开发

### 环境要求

- Python 3.8+
- pygame >= 2.0.0
- pyinstaller >= 5.0 (用于打包)

### 本地打包

```bash
# 安装打包工具
pip install pyinstaller

# 打包为单个可执行文件
pyinstaller --onefile --name snake-game src/main.py
```

### 运行测试

```bash
# 安装测试依赖（如需要）
pip install pytest

# 运行测试
python tests/test_snake.py
```

## 项目结构

```
snake-m25/
├── src/
│   ├── main.py          # 游戏主程序
│   └── logs/            # 日志文件
├── tests/               # 测试文件
├── .github/
│   └── workflows/       # CI/CD 配置
├── pyproject.toml       # 项目配置
├── SPEC.md              # 打包规范
├── README.md            # 项目说明
├── plan.md              # 开发规划
└── prompt.md            # 开发指令
```

## 日志系统

游戏运行日志保存在程序目录下的 `logs` 文件夹中，日志文件名格式为 `snake_YYYYMMDD.log`。

## 版本历史

### v0.1.0
- 初始版本
- 贪吃蛇核心玩法
- 简体中文界面
- 日志系统
- 最高分记录
- 多平台 CI/CD 构建

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交 Issue 和 Pull Request！