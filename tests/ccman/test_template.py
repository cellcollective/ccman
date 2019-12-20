import ccman

def test_render_template():
    context  = { "name": "John Doe" }
    template = ccman.render_template("test", context)

    assert template == "Hello, {name}!".format(**context)