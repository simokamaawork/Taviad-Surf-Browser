import reflex as rx
import asyncio
from typing import TypedDict, Literal


class DownloadItem(TypedDict):
    id: int
    name: str
    status: Literal["In Progress", "Completed", "Paused", "Cancelled"]
    progress: int
    url: str


class DownloadState(rx.State):
    downloads: list[DownloadItem] = []
    next_download_id: int = 1

    @rx.event(background=True)
    async def start_dummy_download(self):
        async with self:
            download_id = self.next_download_id
            self.next_download_id += 1
            new_download = {
                "id": download_id,
                "name": f"dummy_file_{download_id}.zip",
                "status": "In Progress",
                "progress": 0,
                "url": "/placeholder.svg",
            }
            self.downloads.insert(0, new_download)
        for i in range(101):
            if i > 50:
                async with self:
                    is_paused = any(
                        (
                            d["id"] == download_id and d["status"] == "Paused"
                            for d in self.downloads
                        )
                    )
                if is_paused:
                    while True:
                        await asyncio.sleep(0.5)
                        async with self:
                            is_still_paused = any(
                                (
                                    d["id"] == download_id and d["status"] == "Paused"
                                    for d in self.downloads
                                )
                            )
                            is_cancelled = not any(
                                (d["id"] == download_id for d in self.downloads)
                            )
                        if not is_still_paused or is_cancelled:
                            break
                        if is_cancelled:
                            return
            await asyncio.sleep(0.05)
            async with self:
                found = False
                for d in self.downloads:
                    if d["id"] == download_id:
                        d["progress"] = i
                        found = True
                        break
                if not found:
                    return
        async with self:
            for d in self.downloads:
                if d["id"] == download_id:
                    d["status"] = "Completed"
                    break

    @rx.event
    def pause_download(self, download_id: int):
        for d in self.downloads:
            if d["id"] == download_id and d["status"] == "In Progress":
                d["status"] = "Paused"
                break

    @rx.event
    def resume_download(self, download_id: int):
        for d in self.downloads:
            if d["id"] == download_id and d["status"] == "Paused":
                d["status"] = "In Progress"
                break

    @rx.event
    def cancel_download(self, download_id: int):
        self.downloads = [d for d in self.downloads if d["id"] != download_id]

    @rx.event
    def clear_completed_downloads(self):
        self.downloads = [d for d in self.downloads if d["status"] != "Completed"]