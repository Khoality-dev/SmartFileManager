# Smart File Manager: an effective storage management system

Smart File Manager aims to manage and organize files on your computer, ensuring that frequently accessed files are stored on high-speed storage for quicker access. It also works to minimize data duplication, making file management more efficient.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install .
```

## Usage
### 1. Register data to track
```bash
SmartFileManager register <path_to_file_or_directory>
```

### 2. Optimize storage
```bash
SmartFileManager optimize
```

### 3. Remove data from tracking
```bash
SmartFileManager remove <path_to_file_or_directory>
```

