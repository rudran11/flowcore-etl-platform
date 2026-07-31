import os
import base64
import tempfile
import pytest

from flowcore_connector_local.source import LocalSourcePlugin
from flowcore_connector_local.destination import LocalDestinationPlugin
from flowcore_shared.plugins.cdk.messages import MessageType, FlowCoreMessage, RecordMessage

def test_local_source_destination_e2e():
    source = LocalSourcePlugin()
    destination = LocalDestinationPlugin()
    
    with tempfile.TemporaryDirectory() as src_dir, tempfile.TemporaryDirectory() as dest_dir:
        # Create some files in source
        with open(os.path.join(src_dir, "test1.txt"), "w") as f:
            f.write("Hello ")
            f.write("World!")
            
        with open(os.path.join(src_dir, "test2.bin"), "wb") as f:
            f.write(os.urandom(1024 * 1024)) # 1MB random data
            
        # Add a subfolder
        os.makedirs(os.path.join(src_dir, "sub"))
        with open(os.path.join(src_dir, "sub", "test3.txt"), "w") as f:
            f.write("Subfolder content")
            
        # Read from source
        src_config = {"directory": src_dir, "chunk_size": 100 * 1024} # 100KB chunks
        messages = list(source.read(src_config))
        
        # We should have more messages than files because of chunks
        records = [m for m in messages if m.type == MessageType.RECORD]
        state_msgs = [m for m in messages if m.type == MessageType.STATE]
        
        assert len(records) > 3
        assert len(state_msgs) == 1
        
        # Write to destination
        dest_config = {"directory": dest_dir}
        dest_messages = list(destination.write(dest_config, None, iter(messages)))
        
        # Verify files are reconstructed
        assert os.path.exists(os.path.join(dest_dir, "test1.txt"))
        assert os.path.exists(os.path.join(dest_dir, "test2.bin"))
        assert os.path.exists(os.path.join(dest_dir, "sub", "test3.txt"))
        
        with open(os.path.join(dest_dir, "test1.txt"), "r") as f:
            assert f.read() == "Hello World!"
            
        with open(os.path.join(dest_dir, "sub", "test3.txt"), "r") as f:
            assert f.read() == "Subfolder content"
            
        # Verify file sizes
        assert os.path.getsize(os.path.join(dest_dir, "test2.bin")) == 1024 * 1024
