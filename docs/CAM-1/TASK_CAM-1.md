# TASK_CAM-1.md

## 1. 任务依赖图 (Task Dependency Graph)

```mermaid
graph TD
    T1[T1: 环境与项目设置] --\u003e T2
    T1 --\u003e T4

    T2[T2: 预处理与ML服务实现] --\u003e T3
    T3[T3: /predict端点实现]

    T4[T4: 知识库与GLM服务实现] --\u003e T5
    T4 --\u003e T6

    T5[T5: /analyze端点实现]
    T6[T6: /chat端点实现]

    T3 --\u003e T7
    T5 --\u003e T7
    T6 --\u003e T7

    T7[T7: 前端界面开发与集成]

    T1 --\u003e T8
    T2 --\u003e T8
    T3 --\u003e T8
    T4 --\u003e T8
    T5 --\u003e T8
    T6 --\u003e T8
    T7 --\u003e T8

    T8[T8: 单元与集成测试]
```

## 2. 原子任务拆分 (Atomic Task Breakdown)

### **T1: 环境与项目设置 (Environment \u0026 Project Setup)**
- **输入契约**: `CONSENSUS_CAM-1.md` 中确定的技术栈和依赖。
- **实现约束**: 
  - 创建Flask项目的基础目录结构 (e.g., `app.py`, `controllers/`, `services/`, `static/`, `templates/`)。
  - 创建 `requirements.txt` 文件并填入所有Python依赖: `Flask`, `rdkit-pypi`, `pandas`, `scikit-learn==1.0.2`, `python-docx`, `joblib`, `python-dotenv`。
  - 创建 `.env` 文件用于存放 `GLM_API_KEY`，并创建 `.gitignore` 文件以忽略 `.env` 和 `__pycache__` 等。
- **输出契约**: 一个可运行的、空的Flask应用；包含所有依赖的 `requirements.txt`；配置好环境变量加载。
- **依赖关系**: 无前置任务。

### **T2: 预处理与ML服务实现 (Preprocessing \u0026 ML Service)**
- **输入契约**: `分子描述符计算及变量构造.py` 脚本；`model.pkl` 模型文件；T1完成的项目结构。
- **实现约束**: 
  - 创建 `services/ml_service.py`。
  - 在服务中实现一个函数，用于加载 `model.pkl` 模型 (使用 `joblib` 或 `pickle`)。
  - 在服务中实现一个函数，用于调用 `分子描述符计算及变量构造.py` 中的 `main` 函数，并返回模型所需的输入数据。
  - 包含完整的异常处理（文件未找到、模块导入错误等）。
- **输出契约**: 一个可以被控制器调用的、封装了预处理和模型预测逻辑的服务模块。
- **依赖关系**: T1。

### **T3: /predict端点实现 (/predict Endpoint)**
- **输入契约**: `DESIGN_CAM-1.md` 中定义的 `/predict` 接口契约；T2完成的服务。
- **实现约束**: 
  - 创建 `controllers/predict_controller.py`。
  - 实现 `/predict` 路由和处理函数。
  - 对请求体中的 `smiles1`, `smiles2`, `method`, `ratio` 进行验证。
  - 调用 `ml_service` 中的函数完成预测。
  - 按照契约格式化JSON响应。
- **输出契约**: 一个功能完整的 `/predict` API端点。
- **依赖关系**: T2。

### **T4: 知识库与GLM服务实现 (Knowledge \u0026 GLM Service)**
- **输入契约**: `共无定型物知识库.docx` 文件路径；GLM API Endpoint和密钥；T1完成的项目结构。
- **实现约束**: 
  - 创建 `services/glm_service.py`。
  - 实现一个函数，使用 `python-docx` 读取并返回知识库的纯文本内容。需处理文件不存在的异常。
  - 实现一个函数，负责调用GLM API。该函数应包含重试逻辑（3次，间隔2秒），并能处理HTTP请求错误。
  - 从 `.env` 文件中安全地读取API密钥。
- **输出契约**: 一个封装了知识库访问和GLM API调用的服务模块。
- **依赖关系**: T1。

### **T5: /analyze端点实现 (/analyze Endpoint)**
- **输入契约**: `DESIGN_CAM-1.md` 中定义的 `/analyze` 接口契约；T4完成的服务。
- **实现约束**: 
  - 创建 `controllers/analyze_controller.py`。
  - 实现 `/analyze` 路由和处理函数。
  - 调用 `glm_service` 获取知识库内容。
  - 根据 `CONSENSUS_CAM-1.md` 中定义的模板构造Prompt。
  - 调用 `glm_service` 与GLM API交互。
  - 解析GLM返回的文本，并格式化为契约中定义的结构化JSON响应。
- **输出契约**: 一个功能完整的 `/analyze` API端点。
- **依赖关系**: T4。

### **T6: /chat端点实现 (/chat Endpoint)**
- **输入契约**: `DESIGN_CAM-1.md` 中定义的 `/chat` 接口契约；T4完成的服务。
- **实现约束**: 
  - 创建 `controllers/chat_controller.py`。
  - 实现 `/chat` 路由和处理函数。
  - 直接调用 `glm_service` 与GLM API交互，无需知识库上下文。
  - 按照契约格式化JSON响应。
- **输出契约**: 一个功能完整的 `/chat` API端点。
- **依赖关系**: T4。

### **T7: 前端界面开发与集成 (Frontend Development)**
- **输入契约**: `DESIGN_CAM-1.md` 中定义的API契约；T3, T5, T6完成的API端点。
- **实现约束**: 
  - 创建 `templates/index.html` 文件。
  - 使用HTML表单创建四个输入字段和提交按钮。
  - 使用JavaScript (AJAX/Fetch API) 异步调用 `/predict` 和 `/analyze` 端点。
  - 实现简单的结果展示逻辑，将返回的预测和分析数据显示在页面上。
  - 实现基本的输入验证（如字段非空）。
- **输出契约**: 一个可以与后端API完整交互的功能性Web界面。
- **依赖关系**: T3, T5, T6。

### **T8: 单元与集成测试 (Unit \u0026 Integration Testing)**
- **输入契约**: 所有已完成的功能模块和服务 (T2-T7)。
- **实现约束**: 
  - 使用 `unittest` 或 `pytest` 框架。
  - 为 `services` 中的核心逻辑编写单元测试（例如，测试GLM重试机制、知识库读取失败的备用方案）。
  - 为 `controllers` 编写集成测试，模拟HTTP请求并验证响应是否符合预期（覆盖成功和失败场景）。
- **输出契约**: 一套可自动运行的测试用例，确保代码质量和系统稳定性。
- **依赖关系**: T1, T2, T3, T4, T5, T6, T7。