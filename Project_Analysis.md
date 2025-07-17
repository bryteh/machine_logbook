# Context
Filename: Project_Analysis.md
Created On: 2024-12-30
Created By: AI
Associated Protocol: RIPER-5 + Multidimensional + Agent Protocol

# Task Description
Complete analysis and documentation of the machine_maintenance_logbook project folder to understand its purpose, architecture, and functionality.

# Project Overview
The machine_maintenance_logbook is a comprehensive web-based system for tracking machine issues, downtime, and maintenance activities in a CNC machining factory environment.

---
*The following sections are maintained by the AI during protocol execution*
---

# Analysis (Populated by RESEARCH mode)

## Project Architecture
这是一个全栈Web应用程序，包含以下核心组件：

### 1. 后端架构 (Django REST API)
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: PostgreSQL (连接到现有的 `erabase_db` 数据库)
- **AI集成**: OpenAI GPT-4o-mini 用于自动生成摘要和标题
- **OCR支持**: Tesseract.js/pytesseract 用于从图像中提取警报代码
- **文件存储**: 本地文件系统 (可扩展到S3)

### 2. 前端架构 (React + TypeScript)
- **框架**: React 18 + TypeScript + Vite
- **路由**: React Router DOM
- **UI框架**: Tailwind CSS
- **图表**: Recharts
- **HTTP客户端**: Axios
- **图标**: Lucide React

### 3. 数据库设计
**现有表 (只读):**
- `manufacturing_department` - 制造部门定义
- `manufacturing_machine` - 机器设备定义

**新建表 (Django管理):**
- `issues_issue` - 机器问题追踪
- `issues_remedy` - 解决方案/维修记录
- `issues_attachment` - 文件附件

## 核心功能特性

### 1. 机器问题追踪
- 记录机器故障和问题
- 分类管理 (警报、机械、电气、质量等)
- 优先级设置 (低、中、高、关键)
- 状态追踪 (开放、进行中、暂停、已解决、已关闭)
- 停机时间自动计算

### 2. AI增强功能
- **自动摘要**: GPT-4o-mini 自动生成问题描述摘要
- **智能标题**: 基于问题内容自动生成标题
- **OCR识别**: 从上传图像中自动提取警报代码
- **智能分类**: 辅助问题分类和处理

### 3. 文件管理
- **支持格式**: 图片 (JPG, PNG, GIF)、视频 (MP4, MOV, AVI)
- **大小限制**: 每个文件最大10MB
- **分类存储**: 按年/月/日组织文件结构
- **用途分类**: 警报屏幕、手册、其他

### 4. 维修记录管理
- 详细的维修解决方案记录
- 外部技术人员联系信息
- 成本追踪 (人工成本、零件成本)
- 维修后机器可运行状态

### 5. 仪表板和报告
- 实时统计和趋势分析
- 停机时间监控
- 机器状态概览
- 成本分析

## 技术集成亮点

### 1. ERP系统集成
- 连接到现有的 `erabase_db` PostgreSQL数据库
- 读取真实的制造部门和机器数据
- 无缝集成现有的ERP工作流程

### 2. 智能化特性
- OpenAI API集成用于文本处理
- OCR技术用于图像文字识别
- 自动化数据处理和分析

### 3. 用户体验优化
- 响应式设计
- 现代化UI界面
- 实时数据更新
- 移动端友好

## 部署和配置

### 开发环境
- 后端: `http://localhost:8000`
- 前端: `http://localhost:5173`
- 数据库: PostgreSQL erabase_db

### 生产部署
- WSGI部署支持 (Gunicorn, uWSGI)
- 静态文件收集
- 环境变量配置
- 安全设置优化

## 文件结构概览
```
project/
├── django_backend/          # Django后端API
│   ├── issues/             # 核心应用模块
│   ├── machine_logbook/    # Django项目设置
│   ├── media/              # 文件上传存储
│   └── requirements.txt    # Python依赖
├── src/                    # React前端源码
│   ├── components/         # 可复用组件
│   ├── pages/             # 页面组件
│   └── services/          # API服务
├── package.json           # Node.js依赖
└── vite.config.ts         # Vite构建配置
``` 