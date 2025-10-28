import json
import os

def load_operations_data(file_path):
    """加载操作数据"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('operations', [])

def save_operations_data(file_path, operations_data):
    """保存操作数据"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    data = {
        "metadata": {
            "total_operations": len(operations_data),
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z"
        },
        "operations": operations_data
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)