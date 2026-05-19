### ✅ 已修复问题

1. ~~process_documents() 定义但从未调用 — 语义分片是死代码~~ **已修复**
   - **修复方案**: 在 `rag_service.py` 的 `ingest()` 方法中调用 `process_documents()` 进行语义分片
   - **修改文件**: 
     - `rag_service.py:16` - 导入 `process_documents`
     - `rag_service.py:51-52` - 在 `ingest()` 中先调用 `process_documents(docs)` 获取语义分片，再传给 retriever
   - **效果**: 文档摄入时会先通过 `SemanticChunker` 进行语义分片，保留更好的上下文完整性

### 🔴 严重问题（影响 RAG 正确性） 

 1. reset() 未清理 DocStore — 导致孤儿数据
rag_service.py:68-76 的 reset() 方法只删除了 ChromaDB collection，但 没有清理 LocalFileStore （docstore） 。重置后：

- 向量库已清空
- 但 docstore 中仍残留旧的 parent documents
- 后续 ingest 新文档时，retriever 可能从 docstore 中检索到已不存在的旧 parent document，导致 检索结果不一致或报错 

2. 配置值被硬编码覆盖 — [rag] 配置段无效
config.py:21-24 定义了 RAGSettings （ chunk_size=1000 , chunk_overlap=200 ），但 ingestion.py:21-30 的 get_parent_child_chunks() 硬编码了分片参数 （2000/200 和 400/50），完全忽略了配置文件中的值。

用户修改 config.toml 中的 [rag] 段不会产生任何效果。
 3. ids=None 导致文档重复摄入
rag_service.py:49 中 self.retriever.add_documents(docs, ids=None) 让 ChromaDB 自动生成 ID。同一文档多次上传会产生重复向量， 没有去重机制 ，检索时会返回重复内容。

### 🟡 中等问题（影响质量/可维护性） 
5. RetrievalQA 是已弃用的 Legacy Chain
rag_service.py:56-62 使用 RetrievalQA.from_chain_type() ，这是 LangChain 的 legacy API。现代做法应使用 create_retrieval_chain 或 LCEL (LangChain Expression Language)。虽然当前仍可工作，但未来版本可能移除。

 6. 无自定义 Prompt 模板
RetrievalQA 使用默认 prompt，没有针对使用场景（中文场景 + bge-small-zh-v1.5）定制系统提示词。缺少：

- 角色设定（如"你是一个文档问答助手"）
- 回答约束（如"仅基于检索到的内容回答，不要编造"）
- 中文优化提示
这会导致 LLM 可能产生幻觉或回答与检索内容无关。
 7. ChatOpenAI 参数名已弃用
factory.py:20-23 中使用 openai_api_key 和 openai_api_base ，在较新版本的 langchain-openai 中应改为 api_key 和 base_url 。旧参数可能在未来版本中被移除。
 8. 无对话记忆（Conversation Memory）
RAGService.query() 每次查询都创建新的 RetrievalQA 链， 没有对话历史 。多轮对话时 LLM 无法理解上下文引用（如"它是什么？"），用户体验差。
 9. PDF 文本提取丢失页码元数据
routes.py:39-46 将 PDF 所有页文本拼接为单一字符串， 没有保留页码信息 。检索到内容后无法溯源到具体页码。
 10. 无检索相关性过滤
ParentDocumentRetriever 返回的文档没有相关性分数阈值过滤。低相关度的文档可能被塞入上下文，降低回答质量并浪费 token。

### 🟢 轻微问题 11. st.confirm() 非标准 Streamlit API
frontend/main.py:44 使用了 st.confirm() ，这不是 Streamlit 标准函数。应使用 st.checkbox 或自定义确认对话框。
 12. 查询端点无输入校验
routes.py:63 的 /query 端点没有校验空字符串或纯空白查询，可能导致无意义的 LLM 调用。
 13. 模块级 print 语句
rag_service.py:1-12 和 routes.py:1 使用 print() 做加载日志，应统一使用 logging 模块。

### 📊 RAG 流水线正确性总结
RAG 阶段 状态 说明 Document Loading ✅ 基本正确 支持 txt/md/pdf，但 PDF 无页码元数据 Chunking ✅ 正确 语义分片 + Parent-Child 分片，配置值被忽略 Embedding ✅ 正确 HuggingFace 本地缓存 + 降级下载，normalize_embeddings=True Vector Store ✅ 基本正确 ChromaDB + 持久化，但 reset 不完整 Retrieval ⚠️ 部分正确 Parent-Child 检索可用，但无相关性过滤、无去重 Generation ⚠️ 部分正确 可生成回答，但无自定义 prompt、无对话记忆、使用弃用 API

核心结论 ：RAG 的基本骨架（加载→分片→向量化→检索→生成）是完整的，能跑通基本流程。但存在 3 个严重问题 影响正确性，其中 reset() 不完整是最需要优先修复的。