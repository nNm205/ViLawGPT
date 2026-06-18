from dataclasses import dataclass

@dataclass
class VbplDocument:
    doc_id: str
    thuoc_tinh: dict
    content_html: str

    @classmethod
    def from_detail(cls, detail: dict):
        return cls(
            doc_id=str(
                detail.get("doc_id")
                or detail.get("thuoc_tinh", {}).get("id", "")
            ),
            thuoc_tinh=detail.get("thuoc_tinh", {}),
            content_html=detail.get("noi_dung", {}).get(
                "content_html", ""
            ),
        )

    @property
    def so_hieu(self):
        return self.thuoc_tinh.get("so_hieu", "")

    @property
    def ten_van_ban(self):
        return self.thuoc_tinh.get("ten_van_ban", "")

    @property
    def header(self):
        return f"{self.so_hieu}\n{self.ten_van_ban}".strip()