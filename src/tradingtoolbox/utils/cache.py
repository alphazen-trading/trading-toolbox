import os
import json
from msgspec.json import decode
import msgspec
import asyncio
import pandas as pd
from datetime import date
from typing import Callable, Optional
from enum import Enum


class FileFormat(Enum):
    JSON = "json"
    PARQUET = "parquet"
    NONE = "none"


class Cache(msgspec.Struct):
    """
    Cache class for handling file-based caching with support for asynchronous data loading.

    Attributes:
        cache_path (str): The path where the cache file is stored.
        method (Optional[Callable]): A callable, typically an async method, to fetch data when the cache doesn't exist or needs to be reloaded.
        date_as_suffix (bool): If True, appends today's date to the cache file name as a suffix.

    Methods:
        get_async(reload=True): Asynchronously retrieves data from the cache. If the cache file doesn't exist, it will fetch data using the provided method and store it in the cache.
        clean_cache(): Deletes the cache file from disk.

    Usage:
    ```py
    async def my_function():
        await asyncio.sleep(5)
        return []

    cache = Cache(
        cache_path=f"./cache/markets_{ex.exchange_name}.json", method=ex.get_contracts
    )
    data = await cache.get_async()

    # Use this if you don't have any other async.io task, otherwise the program will end before `my_function` runs
    await cache.wait_till_complete()
    ```
    """

    # TODO
    # 1. Provide custom method to load the cache instead of assuming it's json
    # 2. allow to pass parameters to the method

    cache_path: str
    """Where you want the file to be stored"""
    method: Optional[Callable] = None
    """A lambda method to run in case the file doesn't exist"""
    date_as_suffix: bool = False
    """If true, will append today's date to the cache file."""
    file_format: FileFormat = FileFormat.JSON
    """Format of the file to read."""
    dump_format: FileFormat = FileFormat.JSON
    """Format of the file to dump to. It might be None if your method already dumps the file."""
    _task: Optional[asyncio.Task] = None

    def __post_init__(self):
        # Custom initialization logic after the msgspec-generated init
        if self.date_as_suffix:
            extension = self.cache_path.split(".")[-1]
            name_without_extension = self.cache_path.replace(f".{extension}", "")
            self.cache_path = f"{name_without_extension}_{date.today().strftime('%Y%m%d')}.{extension}"
        self._ensure_path_exists()

    # ====================== Private Methods ======================= #
    def _read_file(self) -> Optional[dict | pd.DataFrame]:
        if os.path.exists(self.cache_path):
            if self.file_format == FileFormat.JSON:
                with open(self.cache_path, "r") as f:
                    return decode(f.read())
            elif self.file_format == FileFormat.PARQUET:
                return pd.read_parquet(self.cache_path)
        return None

    def _ensure_path_exists(self):
        directory_path = os.path.dirname(self.cache_path)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)

    async def _reload_async(self, **method_kwargs):
        if self.method:
            data = await self.method(**method_kwargs)

            if self.dump_format == FileFormat.JSON:
                with open(self.cache_path, "w") as f:
                    json.dump(data, f, indent=2)
            elif self.dump_format == FileFormat.PARQUET:
                data.to_parquet(self.cache_path, index=False)
            elif self.dump_format == FileFormat.PARQUET:
                pass

    async def wait_till_complete(self):
        """
        Waits for the task to complete.
        Use this if you don't have any other async.io task to avoid the program ending before the method is ran
        """
        if self._task:
            while True:
                if self._task.done():
                    break
                await asyncio.sleep(1)  # Check every second

    @staticmethod
    async def wait_till_all_tasks_complete():
        """
        Waits for all tasks to complete.
        Use this if you don't have any other async.io task to avoid the program ending before the method is ran
        """
        while True:
            pending_tasks = []
            for task in asyncio.all_tasks():
                if not task.done():
                    pending_tasks.append(task)
            if len(pending_tasks) == 2:
                break
            await asyncio.sleep(1)

    # ====================== Public Methods ======================= #
    async def get_async(self, reload=True, **method_kwargs):
        """
        Gets the data from the cache. If it doesn't exist, it will reload it.

        Args:
            reload (bool, optional): Whether to reload the data. Defaults to True.
            **method_kwargs: Keyword arguments to pass to the method.

        Returns:
            dict: The data from the cache.
        """
        data = self._read_file()
        if data is not None:
            if reload:
                self._task = asyncio.create_task(self._reload_async(**method_kwargs))
        else:
            await self._reload_async(**method_kwargs)
            data = self._read_file()
        return data  # type: ignore

    def clean_cache(self):
        """
        Removes the cache file.
        """
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)
