# Sydney SWE / Fullstack 求职路线图（基于当前能力 & JD Gap Analysis）

## 当前定位（你已经具备的能力）

你已经不是“零基础 candidate”。

你目前已经具备：

### Frontend

- React
- Next.js（App Router）
- TypeScript
- Tailwind CSS
- Responsive Design 基础

### Backend

- Django
- Django REST Framework
- RESTful API 设计
- JWT/Auth
- Google OAuth
- PostgreSQL

### 工程能力

- Git/GitHub
- Docker 基础
- Linux 基础
- API Contract Design
- ERD / DB Design

### AI / Modern Stack

- Dify
- RAG 概念
- AI Agent Integration
- Streaming Response
- Context Management

---

# 你的核心问题（不是不会技术）

你现在真正缺少的是：

## 1. 工程成熟度

你会“做功能”。

但需要提升到：

- scalable
- maintainable
- production-ready

---

## 2. 项目完成度

目前项目更像：

- student project
- engineering prototype

而不是：

- startup MVP
- enterprise-ready application

---

## 3. 商业级工程实践

包括：

- testing
- deployment
- CI/CD
- monitoring
- accessibility
- performance optimisation

---

# 目标（未来 4~6 个月）

目标不是：

❌ 学 20 个框架

目标是：

✅ 把现有能力工程化

---

# 最重要路线（按优先级排序）

---

# PHASE 1 — 把 Homey 做成 Production-Level 项目（最高优先级）

## 为什么最重要

这是你未来最强的 portfolio。

你现在最缺：

- “真实产品感”

而不是：

- “更多 tutorial”

---

# 必做功能

## Authentication

- Email/password auth
- Google OAuth
- Refresh token
- HttpOnly cookie
- CSRF protection
- Email verification
- Password reset

---

## Role System

- Tenant
- Landlord
- Admin

权限隔离：

- admin-only API
- landlord-only listing management
- tenant-only save/apply/report

---

## Listing Lifecycle

实现完整状态：

- draft
- pending_review
- approved
- rejected
- archived

---

## Admin Dashboard

必须有：

- pending review page
- approve/reject actions
- report management
- listing moderation

---

## Search / Filter / Pagination

必须后端实现：

- keyword search
- filter
- pagination
- ordering

---

## Error Handling

必须认真做：

- loading states
- empty states
- error states
- retry logic
- skeleton UI

---

## Mobile Responsive

必须认真适配。

很多 candidate 不会真正 responsive。

---

## Accessibility（WCAG）

至少做到：

- semantic html
- aria-label
- keyboard navigation
- contrast awareness

---

## Image Upload（非常重要）

使用：

- AWS S3
- presigned URL

不要存数据库。

---

## AI Feature（你的差异化）

你的优势。

建议：

### AI Rent Risk Analysis

功能：

- 分析价格是否高于市场
- RAG comparison
- AI summary

技术：

- Dify / OpenAI
- Retrieval
- AI workflow
- async processing

---

# PHASE 2 — Frontend Engineering 深度（极重要）

---

# 你需要加强

## 1. Component Architecture

学习：

- feature folder structure
- reusable component patterns
- composition patterns
- design system
- variants system

目标：
让代码像真实公司项目。

---

## 2. State Management

必须熟：

### React Query / TanStack Query

学习：

- caching
- invalidation
- optimistic update
- mutation lifecycle

---

### Zustand（推荐）

学习：

- global state
- lightweight store design

---

## 3. Performance Optimisation

必须掌握：

- memo
- useMemo
- useCallback
- lazy loading
- dynamic import
- image optimisation
- bundle splitting

---

## 4. Rendering Strategy

真正理解：

- SSR
- CSR
- ISR
- hydration

---

# PHASE 3 — Testing（你的重要短板）

---

# Frontend Testing

## 必学：

### Jest + React Testing Library

学习：

- render
- screen queries
- userEvent
- async testing
- mock api

---

# E2E Testing

推荐：

## Playwright（优先）

实现：

- login flow
- create listing
- upload image
- admin approve
- search/filter

---

# Backend Testing

继续加强：

### Django TestCase

重点：

- API test
- permission test
- serializer validation
- mock external services

---

# PHASE 4 — DevOps & Cloud（巨大加分项）

---

# AWS（非常重要）

必须熟：

## S3

- image upload
- presigned URL

---

## EC2

- backend deployment

---

## RDS

- managed PostgreSQL

---

## CloudFront（加分）

- CDN
- image delivery

---

# Docker

做到：

- frontend
- backend
- postgres
- redis

全部 compose。

---

# CI/CD

GitHub Actions：

必须实现：

- lint
- test
- build
- docker build

进阶：

- auto deploy

---

# PHASE 5 — AI Engineering（你的未来优势）

---

# 你已经领先很多人

因为你已经在接触：

- AI Agent
- RAG
- Dify
- Context Management

---

# 下一步重点

## 真正工程化 AI 系统

学习：

### RAG Architecture

- chunking
- retrieval
- embedding
- vector db

---

### Streaming

- SSE
- partial response

---

### AI Workflow

- async jobs
- tool calling
- orchestration

---

### Evaluation

- hallucination reduction
- prompt quality
- grounding

---

# 你目前最值得补的技术栈（优先级）

## Tier 1（必须）

- React Query
- Playwright
- AWS S3
- CI/CD
- Component Architecture
- Frontend Performance
- Accessibility

---

## Tier 2（强烈建议）

- Zustand
- Redis
- Celery
- Docker Compose
- EC2 deployment
- RDS

---

## Tier 3（未来加分）

- Kubernetes
- Terraform
- GitOps
- Microservices

---

# 你的 Resume 未来应该呈现什么感觉

目标不是：

❌ “我会 React Django”

而是：

✅ “我能独立构建 production-ready SaaS product”

---

# Sydney Market 真正喜欢的人

不是：

- LeetCode machine
- tutorial collector

而是：

## 能真正 ship product 的人

尤其现在 AI 时代。

---

# 你现在和强 candidate 的差距

主要不是：

❌ 智商
❌ 学历
❌ 技术理解

而是：

## 工程成熟度 + 完成度

这是可以靠项目练出来的。

---

# 最终目标（你未来简历应该达到）

看到你项目的人会觉得：

> “这个人真的做过真实产品。”

而不是：

> “这个人跟着教程做了个 clone。”
