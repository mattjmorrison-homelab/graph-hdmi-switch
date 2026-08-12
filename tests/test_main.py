from homelab_hdmi_switch.main import main


def test_main() -> None:
    assert "hello" == main()
