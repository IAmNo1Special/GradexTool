import re

path = r"f:\projects\Revomon\GradexTool\tests\mods\core\test_health.py"
with open(path, encoding="utf-8") as f:
    text = f.read()

test = """
    @pytest.mark.asyncio
    async def test_spawn_background_task_success(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)
        async def my_task():
            return 42

        task = cog._spawn_background_task(my_task())
        await task
        assert task.result() is None # wrapper returns None

    @pytest.mark.asyncio
    async def test_spawn_background_task_cancelled(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)
        async def my_task():
            raise asyncio.CancelledError()

        task = cog._spawn_background_task(my_task())
        await task

    @pytest.mark.asyncio
    async def test_spawn_background_task_exception_no_handler(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)
        async def my_task():
            raise Exception("Fail")

        with patch("mods.core.health.logger") as mock_logger:
            task = cog._spawn_background_task(my_task())
            await task
            mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_spawn_background_task_exception_with_handler(self, mock_bot: Any) -> None:
        cog = HealthCog(mock_bot)
        async def my_task():
            raise Exception("Fail")

        mock_handler = AsyncMock()
        task = cog._spawn_background_task(my_task(), on_error=mock_handler)
        await task
        mock_handler.assert_called_once()
"""

text = re.sub(
    r"    @pytest\.mark\.asyncio\n    async def test_create_task_success.*?mock_handler\.assert_called_once\(\)\n",
    test,
    text,
    flags=re.DOTALL,
)

with open(path, "w", encoding="utf-8") as f:
    f.write(text)

print("Done")
