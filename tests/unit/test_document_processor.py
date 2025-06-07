from app.services.document_processor import document_processor


def test_process_text_file(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("line1\n" * 15)
    result = document_processor.process_document(str(file))
    assert "chunks" in result
    assert isinstance(result["chunks"], list)
    assert any("line1" in chunk["text"] for chunk in result["chunks"])


def test_process_unknown_file_type():
    result = document_processor.process_document("file.unknown")
    assert "chunks" in result
    assert all("Mock content" in chunk["text"] for chunk in result["chunks"])
