# multimodal-preprocess-kit

[English](README.md) | [简体中文](README.zh-CN.md)

一个与框架无关的聊天机器人多模态预处理策略库：描述重试、待推送消息延迟、安全降级。

**速览（默认配置）：**

| 情况 | 决策 |
| --- | --- |
| 描述失败 | `drop_media` |
| 描述过短，或 `ready` 但不足 40 字 | `retry_caption` |
| 描述还在生成，等待 ≤ 90 秒 | `defer`，返回剩余等待秒数 |
| 描述还在生成，等待 > 90 秒 | `push_without_media` |
| 描述就绪且非空 | `push_now`；截图携带 `"auto"` |
| 没有本地文件，且允许缩略图 | 缩略图兜底 |
| 来自其他消息的媒体 | 默认不借用，除非显式开启 |

## 问题

视觉语言描述往往比消息缓冲慢。机器人可能先说「看不到图」，一秒后又描述出来。截图的文字在「概括」而不是「逐行抄写」时会丢掉。而当原图不可用时，管线容易借用相邻消息的图，在没有任何报错的情况下把错误的图挂到消息上。

## 它不做什么

- 不调用任何模型（视觉、语言或其他）。
- 不连接任何聊天平台，不发起网络 I/O。
- 不存储聊天记录。
- 不读取、解码或上传任何媒体文件。

## 安装

```bash
pip install -e .
```

## 快速开始

```python
from mm_preprocess_kit.models import MediaItem, PolicyConfig
from mm_preprocess_kit.policy import decide

media = MediaItem(id="m1", kind="image", caption_status="pending", received_at=0.0)
decision = decide(media, now=30.0, cfg=PolicyConfig())
print(decision.action, decision.reason, decision.retry_after)  # defer caption_pending 60.0
```

截图会得到 `caption_mode="auto"`。等你的适配层知道真实像素尺寸后，用 `choose_caption_mode(width, height, cfg)` 解析它。

## 策略配置表

| 字段 | 默认值 | 含义 |
| --- | --- | --- |
| `min_caption_chars` | 40 | 去除空白后短于该值的描述视为缺失。 |
| `max_defer_seconds` | 90 | 待推送消息最多延迟多久。 |
| `long_image_min_edge` | 700 | 长边达到该值即选择 `transcribe`。 |
| `long_image_max_edge` | 1400 | 预留：供调用方缩放使用，v0.1 不强制。 |
| `long_image_max_tokens` | 900 | 预留：供调用方预算 token，v0.1 不强制。 |
| `allow_thumbnail_fallback` | True | 没有本地文件时允许缩略图。 |
| `allow_borrow_other_media` | False | 允许借用其他消息的媒体。默认关闭。 |

`long_image_min_edge` 是长边规则，不是面积规则：800×600 的图长边是 800，在默认阈值下会选 `transcribe`。

## 设计取舍

**默认不借图。** 图缺失可以恢复；图错了不能。借用其他消息的媒体可能在无声中把别人的图发出去，所以必须显式开启（`allow_borrow_other_media=True`）。

**宁可回文字，也不阻塞。** 延迟窗口到期后，消息按无媒体推送。继续等待会拖慢后面每一条消息，也会让「看不到图」的答案前后不一致。描述仍然可以稍后作为独立消息补推。

**截图在调用方知道尺寸前保持 `auto`。** `decide` 从不获取像素尺寸，也从不打开文件，所以它返回 `caption_mode="auto"`。适配层拿到真实宽高后，用 `choose_caption_mode(width, height, cfg)` 解析。

**这个库刻意止步的地方。** 生产环境的适配层通常比这四个函数做得多。下面这些缺口是有意的，每一条都会改变你接入的方式：

- **失败处理。** 真实管线往往推送占位文案（「媒体无法描述」），而不是丢弃。如果你的管线如此，把 `caption_status="failed"` 映射为 `push_without_media`；`drop_media` 留给那些确实想丢弃的管线。
- **垃圾描述。** 重试规则只基于长度，所以一段全由占位符组成的描述仍可能通过 40 字检查。在把条目标记为 `ready` 之前，先跑你自己的「这段文字是否有意义」检查。
- **长图门槛。** `should_retry_caption` 对所有描述生效。生产环境可能只对截图或长图重试；只对这些类型调用，而不是无条件调用。
- **缩略图语义。** `can_use_thumbnail` 把 `local_path is None` 视为「没有可用原图」。如果文件存在但无法解码，请传 `None`，而不是传一个稍后会失败的路径。

这个库提供决策词汇；策略细节仍然归适配层所有。

## 测试

```bash
pytest -q
```

## 合规

本库只包含通用的预处理策略，不包含任何平台自动化实现。

## 许可证

MIT
