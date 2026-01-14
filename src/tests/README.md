# gRPC Service Test Suite

基于 pytest 框架的 gRPC 服务测试项目，使用 Allure 生成测试报告。

## 目录结构

```
tests/
├── conftest.py              # pytest fixture 配置
├── pytest.ini               # pytest 配置
├── requirements.txt         # Python 依赖
├── test_greeter_service.py  # 测试用例
├── setup.sh                 # 环境安装脚本
├── run_tests.sh             # 运行测试脚本
├── generate_proto.sh        # 生成 gRPC 代码脚本
├── proto/                   # proto 文件目录
├── generated/               # 生成的 Python gRPC 代码
└── reports/                 # 测试报告目录
```

## 环境准备

### 1. 安装 Python 依赖

```bash
# 方式1: 使用 setup.sh (推荐，会创建虚拟环境)
./setup.sh

# 方式2: 直接安装
pip3 install -r requirements.txt
```

### 2. 安装 Allure Commandline

**注意**: `apt install allure` 安装的是游戏，不是报告工具！

```bash
# 方式1: 安装到系统目录 (需要 sudo)
cd /tmp
wget https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz
tar -xzf allure-2.24.0.tgz
sudo mv allure-2.24.0 /opt/allure
sudo ln -sf /opt/allure/bin/allure /usr/local/bin/allure

# 方式2: 安装到用户目录 (无需 sudo)
cd /tmp
wget https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.tgz
tar -xzf allure-2.24.0.tgz
mv allure-2.24.0 ~/allure
echo 'export PATH="$HOME/allure/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 验证安装
allure --version
```

### 3. 生成 Python gRPC 代码

```bash
./generate_proto.sh
```

## 启动 gRPC 服务器

运行测试前需要先启动 gRPC 服务器：

```bash
# 从项目根目录
cd /home/xxf/opensrc/grpc-test
./build/grpctest_app

# 或指定监听地址
./build/grpctest_app 0.0.0.0:50051
```

## 运行测试

### 使用 run_tests.sh

```bash
# 运行全部测试
./run_tests.sh

# 运行 smoke 测试
./run_tests.sh --smoke

# 运行回归测试
./run_tests.sh --regression

# 运行性能测试
./run_tests.sh --performance

# 指定服务器地址
./run_tests.sh --host 192.168.1.100 --port 50051

# 测试后自动打开报告
./run_tests.sh --open
```

### 直接使用 pytest

```bash
# 运行全部测试
python3 -m pytest -v --alluredir=./reports/allure-results

# 运行指定标记的测试
python3 -m pytest -v -m smoke --alluredir=./reports/allure-results
python3 -m pytest -v -m regression --alluredir=./reports/allure-results
python3 -m pytest -v -m performance --alluredir=./reports/allure-results

# 指定服务器地址
python3 -m pytest -v --grpc-host=localhost --grpc-port=50051 --alluredir=./reports/allure-results
```

## 生成 Allure 报告

### 方式1: allure serve (推荐)

启动临时 Web 服务器并自动打开浏览器：

```bash
allure serve ./reports/allure-results
```

### 方式2: 生成静态报告

```bash
# 生成 HTML 报告
allure generate ./reports/allure-results -o ./reports/allure-report --clean

# 打开报告
allure open ./reports/allure-report
```

## 测试用例说明

| 类别 | 测试用例 | 标记 | 说明 |
|------|----------|------|------|
| Greeter Service | test_say_hello_basic | smoke | 基本 SayHello 调用 |
| | test_say_hello_empty_name | regression | 空名称测试 |
| | test_say_hello_unicode | regression | Unicode 字符测试 |
| | test_say_hello_special_chars | regression | 特殊字符测试 |
| | test_say_hello_long_name | regression | 长字符串测试 |
| | test_say_hello_multiple_calls | regression | 多次调用测试 |
| Connection | test_server_connectivity | smoke | 服务器连接测试 |
| | test_invalid_server_connection | regression | 无效地址测试 |
| Performance | test_single_call_latency | performance | 单次调用延迟 |
| | test_throughput | performance | 吞吐量测试 |

## 测试标记

- `smoke`: 快速冒烟测试，验证基本功能
- `regression`: 完整回归测试
- `performance`: 性能测试

## 自定义配置

### 修改默认服务器地址

编辑 `conftest.py` 中的默认值：

```python
parser.addoption(
    "--grpc-host",
    action="store",
    default="localhost",  # 修改默认主机
    help="gRPC server host"
)
parser.addoption(
    "--grpc-port",
    action="store",
    default="50051",  # 修改默认端口
    help="gRPC server port"
)
```

### 添加新的测试用例

在 `test_greeter_service.py` 中添加新的测试方法，使用 Allure 装饰器：

```python
@allure.story("SayHello RPC")
@allure.title("测试标题")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.regression
def test_new_case(self, greeter_stub):
    with allure.step("步骤描述"):
        # 测试代码
        pass
```
