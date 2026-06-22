from __future__ import annotations
class PromptBuilder:
    SYSTEM_PROMPT = """
    Bạn là trợ lý pháp lý chuyên hỗ trợ doanh nghiệp vừa và nhỏ tại Việt Nam.

    QUY TẮC:
    1. Chỉ được trả lời dựa trên CONTEXT được cung cấp.
    2. Không được tự suy diễn hoặc sử dụng kiến thức bên ngoài.
    3. Nếu CONTEXT không đủ để trả lời thì phải trả lời: "Tôi không tìm thấy thông tin phù hợp trong dữ liệu hiện có."
    4. Trả lời ngắn gọn, chính xác, rõ ràng.
    5. Nếu có thể, hãy nêu điều luật liên quan.
    """

    def build(self, question: str, chunks: list[dict]) -> str:
        context_parts = []

        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            article_number = metadata.get("article_number", "")
            clause_number = metadata.get("clause_number", 0)

            if clause_number and clause_number > 0:
                location = f"Điều {article_number}, Khoản {clause_number}"
            else:
                location = f"Điều {article_number}"

            context_parts.append(f"""
                Văn bản: {metadata.get("document_title", "")}
                Số hiệu: {metadata.get("so_hieu", "")}
                {location}

                Nội dung: {chunk.get("text", "")}
            """)

        context = "\n\n".join(context_parts)

        prompt = f"""
        {self.SYSTEM_PROMPT}

        ================ CONTEXT ================

        {context}

        ================ QUESTION ================

        {question}

        ================ ANSWER ================
        """

        return prompt.strip()