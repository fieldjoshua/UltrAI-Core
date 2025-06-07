from app.utils.stubs import psutil


def test_psutil_stub_virtual_memory():
    vm = psutil.virtual_memory()
    assert vm.total == 0
    assert vm.available == 0
    assert vm.percent == 0.0


def test_psutil_stub_cpu():
    assert psutil.cpu_percent() == 0.0
    assert psutil.cpu_count() == 1
