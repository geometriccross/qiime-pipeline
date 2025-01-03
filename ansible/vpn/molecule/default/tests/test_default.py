def test_hello_world_output(host):
    # /tmp/hello.txt が存在し、"Hello World"を含むか確認
    f = host.file("/tmp/hello.txt")
    assert f.exists, "File /tmp/hello.txt does not exist"
    assert f.contains("hello"), "File /tmp/hello.txt does not contain expected string"

