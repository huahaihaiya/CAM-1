# DESIGN_CAM-1.md

## 1. 整体架构图 (Overall Architecture)

```mermaid
graph TD
    subgraph "用户端 (Client)"
        A[前端界面 (HTML/JS/CSS)]
    end

    subgraph "服务端 (Backend - Flask)"
        B[API网关 (app.py)]
        C[预测模块 (/predict)]
        D[分析模块 (/analyze)]
        E[问答模块 (/chat)]
    end

    subgraph "核心服务 (Core Services)"
        F[数据预处理模块 (分子描述符计算及变量构造.py)]
        G[机器学习模型 (model.pkl)]
        H[GLM服务 (外部API)]
        I[知识库 (共无定型物知识库.docx)]
    end

    A -- JSON/HTTP --\u003e B
    B -- "/predict" --\u003e C
    B -- "/analyze" --\u003e D
    B -- "/chat" --\u003e E

    C --\u003e F
    F --\u003e G
    G -- 预测结果 --\u003e C
    C -- 预测结果 --\u003e A

    D -- 预测结果与原始输入 --\u003e H
    I -- 知识库内容 --\u003e D
    D -- 构造Prompt --\u003e H
    H -- 分析报告 --\u003e D
    D -- 结构化分析 --\u003e A

    E -- 用户问题 --\u003e H
    H -- 回答 --\u003e E
    E -- 回答 --\u003e A
```

## 2. 分层设计和核心组件 (Layered Design \u0026 Core Components)

- **表现层 (Presentation Layer)**: 
  - `前端界面`: 负责用户交互、数据输入和结果的可视化展示。是系统的直接用户入口。

- **应用层 (Application Layer)**:
  - `API网关 (app.py)`: Flask应用实例，负责路由分发，是所有请求的入口点。
  - `预测模块 (/predict)`: 编排数据预处理和机器学习预测流程。
  - `分析模块 (/analyze)`: 编排知识库检索、Prompt构造和GLM调用流程。
  - `问答模块 (/chat)`: 处理通用的问答请求。

- **服务层 (Service Layer)**:
  - `数据预处理模块`: 独立的Python模块，负责将SMILES串转换为模型可接受的数值特征。
  - `机器学习模型`: 预训练的`.pkl`文件，执行核心的二元分类任务。
  - `GLM服务`: 外部HTTP服务，提供先进的自然语言理解和生成能力。

- **数据层 (Data Layer)**:
  - `知识库`: `.docx`文件，为GLM分析提供特定领域的专业知识。

## 3. 模块依赖关系图 (Module Dependency)

```mermaid
graph TD
    app.py --\u003e predict_controller
    app.py --\u003e analyze_controller
    app.py --\u003e chat_controller

    predict_controller --\u003e preprocessing_service
    predict_controller --\u003e ml_model_service

    analyze_controller --\u003e knowledge_service
    analyze_controller --\u003e glm_service

    chat_controller --\u003e glm_service

    preprocessing_service[数据预处理服务] -- "调用" --\u003e M(分子描述符计算及变量构造.py)
    ml_model_service[ML模型服务] -- "加载" --\u003e P(model.pkl)
    knowledge_service[知识库服务] -- "读取" --\u003e D(共无定型物知识库.docx)
    glm_service[GLM服务] -- "HTTP请求" --\u003e G(GLM API)
```

*注：`_controller` 表示控制器，负责处理HTTP请求；`_service` 表示服务，封装具体的业务逻辑。*

## 4. 接口契约定义 (API Contract)

**Base URL**: `http://127.0.0.1:5000`

### 4.1. `/predict`

- **Method**: `POST`
- **Description**: 接收化合物信息，返回机器学习模型的预测结果。
- **Request Body**:
  ```json
  {
    "smiles1": "\u003cSMILES_STRING\u003e",
    "smiles2": "\u003cSMILES_STRING\u003e",
    "method": 1, // 1 for 溶剂法, 2 for 熔融法
    "ratio": 1.5
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "prediction": 1, // 0 or 1
    "message": "能够形成共无定型物"
  }
  ```
- **Error Response (400 Bad Request)**:
  ```json
  {
    "error": "Invalid SMILES string provided."
  }
  ```

### 4.2. `/analyze`

- **Method**: `POST`
- **Description**: 接收化合物信息和预测结果，返回GLM的分析报告。
- **Request Body**:
  ```json
  {
    "smiles1": "\u003cSMILES_STRING\u003e",
    "smiles2": "\u003cSMILES_STRING\u003e",
    "prediction": 1 // 0 or 1
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "analysis": {
      "electrostatic": "...",
      "pi_pi_interaction": "...",
      "hydrogen_bond": "...",
      "hydrophobic_interaction": "...",
      "thermodynamics": "...",
      "kinetics": "..."
    }
  }
  ```
- **Error Response (500 Internal Server Error)**:
  ```json
  {
    "error": "Failed to get analysis from GLM after 3 retries."
  }
  ```

### 4.3. `/chat`

- **Method**: `POST`
- **Description**: 通用问答接口。
- **Request Body**:
  ```json
  {
    "query": "什么是共无定型物?"
  }
  ```
- **Success Response (200 OK)**:
  ```json
  {
    "answer": "共无定型物是..."
  }
  ```

## 5. 数据流向图 (Data Flow Diagram)

```mermaid
sequenceDiagram
    participant User as 用户
    participant FE as 前端界面
    participant BE_Predict as /predict API
    participant BE_Analyze as /analyze API
    participant Preprocessing as 预处理脚本
    participant ML_Model as 机器学习模型
    participant Knowledge as 知识库
    participant GLM as GLM API

    User-\u003e\u003eFE: 1. 输入SMILES, method, ratio
    FE-\u003e\u003eBE_Predict: 2. 发送POST请求
    BE_Predict-\u003e\u003ePreprocessing: 3. 调用main()函数
    Preprocessing--\u003e\u003eBE_Predict: 4. 返回模型输入变量
    BE_Predict-\u003e\u003eML_Model: 5. 加载模型并预测
    ML_Model--\u003e\u003eBE_Predict: 6. 返回预测结果 (0/1)
    BE_Predict--\u003e\u003eFE: 7. 返回JSON响应

    FE-\u003e\u003eBE_Analyze: 8. (根据用户操作)发送POST请求
    BE_Analyze-\u003e\u003eKnowledge: 9. 读取.docx文件内容
    Knowledge--\u003e\u003eBE_Analyze: 10. 返回知识库文本
    BE_Analyze-\u003e\u003eGLM: 11. 构造Prompt并发送API请求
    GLM--\u003e\u003eBE_Analyze: 12. 返回分析文本
    BE_Analyze--\u003e\u003eFE: 13. 返回结构化JSON响应
    FE-\u003e\u003eUser: 14. 展示预测和分析结果
```

## 6. 异常处理策略 (Exception Handling Strategy)

- **输入验证**: 在API控制器层对所有输入（SMILES格式、`ratio` \u003e 0, `method` in [1, 2]）进行严格验证，验证失败则返回`400 Bad Request`。
- **脚本/模型调用失败**: 在服务层使用`try...except`捕获`FileNotFoundError`（模型或脚本不存在）、`ModuleNotFoundError`（依赖缺失）或脚本执行期间的任何异常，记录日志并返回`500 Internal Server Error`。
- **外部API调用失败**: 
  - **GLM API**: 实现一个包装函数，内置重试逻辑（重试3次，间隔2秒）。如果最终失败，记录详细错误日志，并返回`502 Bad Gateway`或`500`。
- **知识库访问失败**: 
  - 如果`.docx`文件不存在或无法读取，捕获异常，记录一个警告级别的日志，然后在没有知识库上下文的情况下继续调用GLM。在返回给前端的响应中可以附加一个警告字段，如 `"warning": "Knowledge base not accessible. Analysis may be less accurate."`。