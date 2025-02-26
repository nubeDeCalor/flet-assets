from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from pathlib import Path
import socket
from threading import Thread


class AssetsServer:
    def __init__(
        self, directory: str = "app/src/assets", mount_path: str = "/", port: int = 1111
    ):
        """
        Static Files server.
        :param directory: Assets path
        :param mount_path: Mount path
        :param port: Deploy Port
        """
        self.app = FastAPI(title="Static Server")
        self.directory = str(Path(directory).resolve())
        self.mount_path = mount_path
        self.port = port
        self.host = self._get_ipv4()
        self.assets = f"http://{self.host}:{self.port}"

        @self.app.get("/")
        async def root():
            return {"message": "Server Files: OK", "status": "ok"}

        self.app.mount(
            path=self.mount_path,
            app=StaticFiles(directory=self.directory, html=True),
            name="StaticFiles",
        )
        self._start_server()

    def _get_ipv4(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def _start_server(self):
        config = uvicorn.Config(
            app=self.app, host="0.0.0.0", port=self.port, log_level="info"
        )
        server = uvicorn.Server(config)
        Thread(target=server.run, daemon=True).start()

        print(f"Files Server mount on: {self.assets}")
        print(f"Files From: {self.directory}\n")
