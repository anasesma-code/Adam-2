from types import SimpleNamespace as NS

import comparador


class FakeStream:
    def __init__(self, msg):
        self.msg = msg

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        yield NS(type="content_block_start", content_block=NS(type="server_tool_use", name="web_search"))

    def get_final_message(self):
        return self.msg


class FakeClient:
    def __init__(self, msgs):
        self.msgs = list(msgs)
        self.calls = []
        self.beta = NS(messages=NS(stream=self._stream))

    def _stream(self, **kw):
        self.calls.append(kw)
        return FakeStream(self.msgs.pop(0))


def test_resume_pause_turn_y_devuelve_texto():
    pausa = NS(stop_reason="pause_turn", content=[NS(type="server_tool_use")])
    final = NS(stop_reason="end_turn", content=[NS(type="text", text="**Más barato: Dia**")])
    client = FakeClient([pausa, final])
    messages = [{"role": "user", "content": comparador._pregunta("leche", "28001")}]

    texto = comparador.consultar(client, messages)

    assert texto == "**Más barato: Dia**"
    assert len(client.calls) == 2
    assert [m["role"] for m in messages] == ["user", "assistant"]
    assert len(messages[1]["content"]) == 2
    assert client.calls[0]["fallbacks"] == "default"
    assert "28001" in messages[0]["content"]


def test_rechazo():
    client = FakeClient([NS(stop_reason="refusal", content=[])])
    assert "No he podido" in comparador.consultar(client, [{"role": "user", "content": "x"}])
