class PromptBuilder:
    SYSTEM_PROMPT = """
    Bạn là trợ lý pháp lý chuyên hỗ trợ doanh nghiệp vừa và nhỏ tại Việt Nam.

    QUY TẮC:
    1. Chỉ trả lời dựa trên CONTEXT được cung cấp.
    2. Không được tự suy diễn.
    3. Nếu CONTEXT không chứa thông tin để trả lời thì nói:
    "Tôi không tìm thấy thông tin phù hợp trong dữ liệu hiện có."
    4. Trả lời ngắn gọn, rõ ràng.
    """

    def build(self, question: str, chunks: list[str]) -> str:
        context = "\n\n".join(chunks)
        prompt = f"""
        {self.SYSTEM_PROMPT}

        CONTEXT:
        {context}

        QUESTION:
        {question}

        ANSWER:
        """

        return prompt