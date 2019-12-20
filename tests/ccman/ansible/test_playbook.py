# imports - module imports
from ccman.ansible import Playbook

def test_playbook(capsys):
    playbook = Playbook(name = "test.yml")
    playbook.run()

    result   = playbook.run(output = True)
    assert "Hello, World!" in result.output