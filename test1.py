import pymupdf4llm
import pathlib

md_text = pymupdf4llm.to_markdown("atomic-habits/atomic-habits.pdf")


# now work with the markdown text, e.g. store as a UTF8-encoded file
pathlib.Path("output.txt").write_bytes(md_text.encode())

