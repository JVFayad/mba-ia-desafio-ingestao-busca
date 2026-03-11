import runpy
from unittest.mock import MagicMock, patch

import chat as chat_module


class TestMainExitBehavior:
    def test_exits_when_user_types_sair(self, capsys):
        with (
            patch("builtins.input", return_value="sair"),
            patch("chat.search_prompt") as mock_search,
        ):
            chat_module.main()

        mock_search.assert_not_called()
        assert "Encerrando o chat" in capsys.readouterr().out

    def test_exits_case_insensitive_sair(self, capsys):
        with patch("builtins.input", return_value="SAIR"):
            chat_module.main()

        assert "Encerrando o chat" in capsys.readouterr().out

    def test_exits_mixed_case_sair(self, capsys):
        with patch("builtins.input", return_value="Sair"):
            chat_module.main()

        assert "Encerrando o chat" in capsys.readouterr().out


class TestMainResponseHandling:
    def test_prints_question_and_response(self, capsys):
        mock_response = MagicMock()
        mock_response.content = "Esta é a resposta"

        with (
            patch("builtins.input", side_effect=["Qual o tema?", "sair"]),
            patch("chat.search_prompt", return_value=mock_response),
        ):
            chat_module.main()

        out = capsys.readouterr().out
        assert "Qual o tema?" in out
        assert "Esta é a resposta" in out

    def test_prints_error_when_search_returns_none(self, capsys):
        with (
            patch("builtins.input", return_value="alguma pergunta"),
            patch("chat.search_prompt", return_value=None),
        ):
            chat_module.main()

        assert "Não foi possível iniciar o chat" in capsys.readouterr().out

    def test_returns_early_when_search_returns_none(self):
        call_count = {"n": 0}

        def counting_input(_prompt=""):
            call_count["n"] += 1
            return "alguma pergunta"

        with (
            patch("builtins.input", side_effect=counting_input),
            patch("chat.search_prompt", return_value=None),
        ):
            chat_module.main()

        # deve chamar input apenas uma vez e sair, sem pedir nova pergunta
        assert call_count["n"] == 1

    def test_search_called_with_exact_question(self):
        mock_response = MagicMock()
        mock_response.content = "resposta"

        with (
            patch("builtins.input", side_effect=["minha pergunta", "sair"]),
            patch("chat.search_prompt", return_value=mock_response) as mock_search,
        ):
            chat_module.main()

        mock_search.assert_any_call("minha pergunta")

    def test_multiple_questions_loop(self, capsys):
        responses = [MagicMock(content=f"resposta {i}") for i in range(3)]

        with (
            patch("builtins.input", side_effect=["p1", "p2", "p3", "sair"]),
            patch("chat.search_prompt", side_effect=responses),
        ):
            chat_module.main()

        out = capsys.readouterr().out
        assert "resposta 0" in out
        assert "resposta 1" in out
        assert "resposta 2" in out


class TestChatModuleMainEntryPoint:
    def test_runs_main_when_executed_as_script(self, capsys):
        with patch("builtins.input", return_value="sair"):
            runpy.run_path("src/chat.py", run_name="__main__")

        assert "Encerrando o chat" in capsys.readouterr().out
