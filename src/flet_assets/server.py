from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
from pathlib import Path
import socket
from threading import Thread
import os
import sys
import time
from typing import Optional, Union, Dict, Any
import logging
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)


class AssetsServer:
    """
    A robust static file server implementation for serving assets in web applications.
    
    This server utilizes FastAPI and Uvicorn to create a high-performance static file 
    server that runs in a separate thread. It automatically detects the local IP address,
    handles directory validation, and provides colorful terminal feedback.
    
    Attributes:
        app (FastAPI): The FastAPI application instance.
        directory (str): The absolute path to the directory containing static files.
        mount_path (str): The URL path where the static files will be served from.
        port (int): The port number the server will listen on.
        host (str): The detected local IP address for network access.
        assets (str): The complete URL to access the assets (http://{host}:{port}).
        is_running (bool): Flag indicating if the server is currently running.
        
    Examples:
        Basic usage:
        >>> server = AssetsServer(directory="./static", port=8080)
        
        Custom mount path:
        >>> server = AssetsServer(
        ...     directory="./public/assets", 
        ...     mount_path="/static", 
        ...     port=3000
        ... )
    """

    def __init__(
        self, 
        directory: str = "/", 
        mount_path: str = "/", 
        port: int = 1111,
        verbose: bool = True
    ):
        """
        Initialize the static file server with specified configuration.
        
        Args:
            directory (str): Path to the directory containing static files.
                Defaults to "/" (root path, but you can give .../assets).
            mount_path (str): URL path where static files will be mounted.
                Defaults to "/" (root path).
            port (int): Port number to use for the server.
                Defaults to 1111.
            verbose (bool): Enable detailed logging and colorful output.
                Defaults to True.
        
        Raises:
            FileNotFoundError: If the specified directory does not exist.
            PermissionError: If the application lacks permission to access the directory.
            OSError: If the specified port is already in use or cannot be bound.
        """
        # Initialize colorama for cross-platform colored output
        colorama.init(autoreset=True)
        
        # Set up logging
        self._setup_logging(verbose)
        
        # Store configuration
        self.app = FastAPI(title="Assets Server")
        self.verbose = verbose
        self.is_running = False
        
        # Validate and set directory
        try:
            self._validate_directory(directory)
            self.directory = str(Path(directory).resolve())
        except (FileNotFoundError, PermissionError) as e:
            self._log_error(f"Directory error: {str(e)}")
            raise
        
        # Set up server configuration
        self.mount_path = self._normalize_mount_path(mount_path)
        self.port = self._validate_port(port)
        
        try:
            self.host = self._get_ipv4()
        except OSError as e:
            self._log_error(f"Network error: Unable to determine IP address - {str(e)}")
            self.host = "localhost"  # Fallback to localhost
            
        # Construct the assets URL
        self.assets = f"http://{self.host}:{self.port}"
        
        # Set up routes
        self._setup_routes()
        
        # Start server
        try:
            self._start_server()
        except Exception as e:
            self._log_error(f"Server startup error: {str(e)}")
            raise RuntimeError(f"Failed to start server: {str(e)}") from e

    def _setup_logging(self, verbose: bool) -> None:
        """
        Configure the logging system.
        
        Args:
            verbose (bool): Whether to enable detailed logging.
        """
        level = logging.INFO if verbose else logging.WARNING
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        )
        self.logger = logging.getLogger("AssetsServer")

    def _validate_directory(self, directory: str) -> None:
        """
        Validate that the provided directory exists and is accessible.
        
        Args:
            directory (str): Path to the directory to validate.
            
        Raises:
            FileNotFoundError: If the directory doesn't exist.
            PermissionError: If the directory isn't accessible.
        """
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory '{directory}' does not exist")
        if not path.is_dir():
            raise FileNotFoundError(f"Path '{directory}' is not a directory")
        if not os.access(path, os.R_OK):
            raise PermissionError(f"No read permission for directory '{directory}'")

    def _normalize_mount_path(self, mount_path: str) -> str:
        """
        Ensure the mount path starts with a forward slash.
        
        Args:
            mount_path (str): The mount path to normalize.
            
        Returns:
            str: The normalized mount path.
        """
        return f"/{mount_path.lstrip('/')}"

    def _validate_port(self, port: int) -> int:
        """
        Validate that the provided port is within a valid range.
        
        Args:
            port (int): Port number to validate.
            
        Returns:
            int: The validated port number.
            
        Raises:
            ValueError: If the port is outside the valid range.
        """
        if not (1024 <= port <= 65535):
            self._log_warning(f"Port {port} is outside recommended range (1024-65535)")
            if port < 1 or port > 65535:
                raise ValueError(f"Port must be between 1 and 65535, got {port}")
        return port

    def _get_ipv4(self) -> str:
        """
        Detect the local IPv4 address for network access.
        
        Returns:
            str: The detected IPv4 address.
            
        Raises:
            OSError: If unable to determine the IP address.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Connect to Google DNS to determine the active network interface
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ip
        except OSError as e:
            # Fall back to localhost if we can't determine IP
            self._log_warning(f"Could not determine network IP: {e}")
            return "localhost"
        finally:
            s.close()

    def _setup_routes(self) -> None:
        """
        Set up the FastAPI routes and static file handlers.
        """
        # Root endpoint for health checks
        @self.app.get("/")
        async def root() -> Dict[str, str]:
            return {
                "message": "Assets Server: Online",
                "status": "ok",
                "version": "1.0.0",
                "serving_from": self.directory,
                "mount_path": self.mount_path
            }
            
        # Error handler for 404 Not Found
        @self.app.exception_handler(404)
        async def not_found_handler(request, exc) -> JSONResponse:
            return JSONResponse(
                status_code=404,
                content={
                    "error": "Not Found",
                    "message": f"The requested resource '{request.url.path}' was not found",
                    "status": "error"
                }
            )
            
        # Mount static files
        try:
            self.app.mount(
                path=self.mount_path,
                app=StaticFiles(directory=self.directory, html=True),
                name="StaticFiles",
            )
        except Exception as e:
            self._log_error(f"Failed to mount static files: {str(e)}")
            raise RuntimeError(f"Could not mount static files: {str(e)}") from e

    def _start_server(self) -> None:
        """
        Start the Uvicorn server in a separate thread.
        
        Raises:
            RuntimeError: If the server fails to start.
        """
        # Create a configuration for the Uvicorn server
        config = uvicorn.Config(
            app=self.app,
            host="0.0.0.0",  # Listen on all available interfaces
            port=self.port,
            log_level="info" if self.verbose else "warning"
        )
        
        # Create the server
        server = uvicorn.Server(config)
        
        # Start the server in a separate thread
        server_thread = Thread(target=server.run, daemon=True)
        server_thread.start()
        
        # Wait briefly to ensure the server starts
        time.sleep(0.5)
        
        # Check if server started successfully (best effort)
        if server_thread.is_alive():
            self.is_running = True
            self._log_success()
        else:
            raise RuntimeError("Server failed to start")

    def _log_success(self) -> None:
        """
        Display a colorful success message in the terminal.
        """
        if not self.verbose:
            return
            
        border = Fore.CYAN + "=" * 60
        
        print("\n" + border)
        print(Fore.GREEN + Style.BRIGHT + "✓ ASSETS SERVER SUCCESSFULLY STARTED")
        print(border + "\n")
        
        print(Fore.YELLOW + Style.BRIGHT + "SERVER INFORMATION:")
        print(Fore.WHITE + f"  • {Fore.CYAN}Assets URL:     {Fore.GREEN}{self.assets}")
        print(Fore.WHITE + f"  • {Fore.CYAN}Mount Path:     {Fore.GREEN}{self.mount_path}")
        print(Fore.WHITE + f"  • {Fore.CYAN}Local IP:       {Fore.GREEN}{self.host}")
        print(Fore.WHITE + f"  • {Fore.CYAN}Port:           {Fore.GREEN}{self.port}")
        print(Fore.WHITE + f"  • {Fore.CYAN}Directory:      {Fore.GREEN}{self.directory}")
        
        # Show some files in the directory (up to 5)
        try:
            files = list(Path(self.directory).glob("*"))[:5]
            if files:
                print("\n" + Fore.YELLOW + Style.BRIGHT + "FILES AVAILABLE:")
                for file in files:
                    print(Fore.WHITE + f"  • {Fore.CYAN}{file.name}")
                if len(list(Path(self.directory).glob("*"))) > 5:
                    print(Fore.WHITE + f"  • {Fore.CYAN}... and more")
        except Exception:
            pass
            
        print("\n" + border)
        print(Fore.GREEN + f"Files are served at: {self.assets}")
        print(border + "\n")

    def _log_error(self, message: str) -> None:
        """
        Log an error message with color formatting.
        
        Args:
            message (str): The error message to log.
        """
        self.logger.error(message)
        if self.verbose:
            print(f"\n{Fore.RED}{Style.BRIGHT}ERROR: {message}{Style.RESET_ALL}\n")

    def _log_warning(self, message: str) -> None:
        """
        Log a warning message with color formatting.
        
        Args:
            message (str): The warning message to log.
        """
        self.logger.warning(message)
        if self.verbose:
            print(f"{Fore.YELLOW}WARNING: {message}{Style.RESET_ALL}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current server status.
        
        Returns:
            dict: A dictionary containing server status information.
        """
        return {
            "running": self.is_running,
            "url": self.assets,
            "directory": self.directory,
            "mount_path": self.mount_path,
            "port": self.port,
            "host": self.host
        }