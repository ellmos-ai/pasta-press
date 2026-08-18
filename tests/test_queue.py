import os
import json
import pytest
from pastapress.queue_manager import QueueManager

def test_queue_manager_add_and_pop(tmp_path):
    queue_file = tmp_path / "test_queue.json"
    qm = QueueManager(queue_file=str(queue_file))
    
    assert qm.is_empty()
    
    qm.add({"path": "file1.txt", "overwrite": False})
    qm.add({"path": "file2.txt", "overwrite": True})
    
    assert not qm.is_empty()
    assert len(qm.get_all()) == 2
    
    item = qm.pop()
    assert item["path"] == "file1.txt"
    assert len(qm.get_all()) == 1
    
    # Check persistence
    qm2 = QueueManager(queue_file=str(queue_file))
    assert len(qm2.get_all()) == 1
    assert qm2.pop()["path"] == "file2.txt"
    assert qm2.is_empty()
