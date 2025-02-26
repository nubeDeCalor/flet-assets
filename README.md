```markdown
# **StaticServer Documentation** 🚀

The `StaticServer` class is designed to simplify debugging for mobile devices (iOS/Android) in Flet apps. It serves static files (like images, icons, or text files) from your computer, making them accessible to mobile devices during development. 📱💻

---

## **Why Use StaticServer?** 🤔
When developing for mobile:
- Direct file paths from your computer won’t work on devices. 🚫
- StaticServer hosts your files locally, providing a URL (`server.assets`) that devices can access. 🌐
- Perfect for debugging and testing assets on real devices. 🛠️

---

## **How to Use It** 🛠️

### **1. Installation**
pip install flet-staticserver
from flet_staticserver import StaticServer
```

---

### **2. Basic Setup**
Start the server and use it in your Flet app:

```python
import flet as ft
from serve_files import StaticServer

# Initialize the server 🎬
server = StaticServer()

def main(page: ft.Page):
    # Access files using server.assets 🖼️
    page.add(
        ft.Image(src=f"{server.assets}/icon.png"),
        ft.Text(f"Access files at: {server.assets}")
    )

# Run your Flet app 🚀
ft.app(main)
```

---

### **3. Customization Options** ⚙️
Customize the server to fit your needs:
- **Change the folder**: Serve files from a specific directory.
- **Change the port**: Use a different port if needed.

```python
server = StaticServer(
    directory="path/to/your/assets",  # 🗂️ Custom folder
    port=2222                        # 🚪 Custom port
)
```

---

### **4. Accessing Files** 📂
Once the server is running, access your files like this:
- **File in root**: `{server.assets}/file.txt`
- **File in subfolder**: `{server.assets}/images/photo.jpg`

Example:
```python
ft.Image(src=f"{server.assets}/images/icon.png")
```

---

## **How It Works** 🧙‍♂️
- The server runs in the background using **FastAPI** and **UVicorn**. ⚡
- It automatically detects your machine's IPv4 address, so devices on the same network can access the files. 🌐
- Files are served dynamically, making debugging seamless. 🛠️

---

## **Example Use Case** 🖼️
Display an image from your `assets` folder on a mobile device:

```python
import flet as ft
from serve_files import StaticServer

# Start the server 🎬
server = StaticServer()

def main(page: ft.Page):
    # Display an image from the server 🖼️
    page.add(
        ft.Image(src=f"{server.assets}/icon.png"),
        ft.Text("Your image is live!")
    )

# Run the app 🚀
ft.app(main)
```

---

## **Why It’s Useful** ❤️
- Solves the problem of inaccessible local files on mobile devices. 📱
- Simplifies debugging and testing during development. 🛠️
- Works seamlessly with Flet apps. 🎯

---

## **Final Notes** 📝
- The server stops automatically when your app closes.
- Use `server.assets` to get the base URL for your files.
- Happy debugging! 😄👨‍💻👩‍💻

---

**Enjoy building and debugging your Flet apps!** 🎉