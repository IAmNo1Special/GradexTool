path = r"f:\projects\Revomon\GradexTool\tests\mods\core\test_health.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

test = """
    @pytest.mark.asyncio
    async def test_create_task_success(self) -> None:
        async def my_task():
            return 42

        task = HealthCog.create_task(my_task())
        await task
        assert task.result() is None # wrapper returns None

    @pytest.mark.asyncio
    async def test_create_task_cancelled(self) -> None:
        async def my_task():
            raise asyncio.CancelledError()

        task = HealthCog.create_task(my_task())
        await task

    @pytest.mark.asyncio
    async def test_create_task_exception_no_handler(self) -> None:
        async def my_task():
            raise Exception("Fail")

        with patch("mods.core.health.logger") as mock_logger:
            task = HealthCog.create_task(my_task())
            await task
            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_exception_with_handler(self) -> None:
        async def my_task():
            raise Exception("Fail")

        mock_handler = AsyncMock()
        task = HealthCog.create_task(my_task(), on_error=mock_handler)
        await task
        mock_handler.assert_called_once()
"""

text = text.replace("class TestHealthCogLogic:", "class TestHealthCogLogic:" + test)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
