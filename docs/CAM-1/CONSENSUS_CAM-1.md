# CONSENSUS_CAM-1.md

## 1. 最终需求描述 (Final Requirement Description)

开发一个名为CAM-1的智能预测系统。该系统通过Web界面接收两种化合物的SMILES串、制备技术和重量比，利用一个预训练的机器学习模型进行二元分类预测（是否形成共无定型物），并集成GLM大语言模型对预测结果进行多维度（如静电相互作用、氢键等）的深入分析。系统需提供RESTful API，并具备健壮的异常处理机制。

## 2. 技术实现方案 (Technical Implementation Plan)

- **后端**: 使用Python Flask框架。
- **前端**: 使用标准HTML/CSS/JavaScript。
- **机器学习**: 加载位于项目根目录的 `model.pkl` 文件，该模型依赖 `scikit-learn==1.0.2`。
- **数据预处理**: 调用项目根目录下的 `分子描述符计算及变量构造.py` 模块中的 `main(smile1, smile2, ratio, method)` 函数。该模块依赖 `rdkit-pypi` 和 `pandas`。
- **大语言模型**: 通过API `https://open.bigmodel.cn/api/paas/v4/chat/completions` 与GLM进行交互，API密钥将通过环境变量配置。
- **知识库**: 读取并解析 `D:\dev\工程\learn\1114共无定型物\筛选平台的构建\共无定型物知识库.docx` 文件，作为调用GLM时的上下文。文件为纯文本，使用 `python-docx` 库进行读取。

## 3. 任务边界与验收标准 (Task Scope \u0026 Acceptance Criteria)

### 任务边界

- **范围内**: 
  - 完整的后端API (`/predict`, `/analyze`, `/chat`) 功能实现。
  - 功能性的前端界面，满足数据输入和结果展示。
  - 正确集成 `model.pkl` 和 `分子描述符计算及变量构造.py`。
  - 实现与GLM API的对接和知识库的整合。
  - 完整的异常处理和输入验证。
  - 创建 `requirements.txt` 文件管理依赖。

- **范围外**:
  - 机器学习模型的重新训练或调优。
  - `分子描述符计算及变量构造.py` 和 `共无定型物知识库.docx` 的内容创建。
  - 生产环境的部署和运维。
  - 用户认证系统。

### 验收标准

1.  **C1**: 前端页面可以成功加载，四个输入字段功能正常，提交按钮可以触发对后端的API请求。
2.  **C2**: `/predict` API能够正确接收前端数据，调用预处理脚本和ML模型，并返回 `{"prediction": 0|1, "message": "..."}` 格式的响应。
3.  **C3**: `/analyze` API能够接收前端数据，正确读取知识库，构造Prompt，调用GLM API，并返回 `{"analysis": {"electrostatic": "...", ...}}` 格式的响应。
4.  **C4**: `/chat` API能够接收用户的通用问题，并返回 `{"answer": "..."}` 格式的响应。
5.  **C5**: 对无效SMILES、错误重量比等输入能返回清晰的错误提示。
6.  **C6**: GLM API调用失败时，系统会重试3次（间隔2秒）。
7.  **C7**: 知识库文件读取失败时，系统能继续调用GLM并返回包含警告信息的分析结果。
8.  **C8**: 项目包含 `requirements.txt`，列出所有必要的Python依赖。
9.  **C9**: GLM API密钥通过环境变量进行配置，不会硬编码在代码中。

## 4. 已解决的不确定性 (Resolved Uncertainties)

- **U1**: **预处理脚本调用方式**: 明确为Python模块导入，调用 `main` 函数。
- **U2**: **项目依赖**: 明确为 `Flask`, `rdkit-pypi`, `pandas`, `scikit-learn==1.0.2`, `python-docx`, `joblib`。将创建 `requirements.txt`。
- **U3**: **模型与脚本位置**: 均位于项目根目录。
- **U4**: **GLM API Endpoint**: 确认为 `https://open.bigmodel.cn/api/paas/v4/chat/completions`。
- **U5**: **知识库使用**: 确认为读取`.docx`内容作为GLM的上下文。
- **U6**: **Prompt构造**: 确认使用模板：`"基于以下知识：[...知识库内容...]，请从[分析维度]等角度，分析为什么化合物 [化合物1] 和 [化合物2] [能/不能] 形成共无定型物。"`
- **U7**: **API数据结构**: 确认了 `/predict`, `/analyze`, `/chat` 三个端点的请求和响应JSON结构，分析结果的键将使用英文。
- **U8**: **异常处理策略**: 明确了API失败重试（3次，间隔2秒）和知识库访问失败的备用方案（无上下文调用并返回警告）。