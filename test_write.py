import os

def test_write():
    try:
        # Try to create a test file
        test_file = 'test_write.txt'
        with open(test_file, 'w') as f:
            f.write('This is a test file.')
        
        # Verify the file was created
        if os.path.exists(test_file):
            print(f"Successfully created and wrote to {test_file}")
            print(f"File content: {open(test_file).read()}")
            os.remove(test_file)  # Clean up
            return True
        else:
            print("Failed to create test file")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing file write permissions...\n")
    if test_write():
        print("\nFile write test completed successfully!")
    else:
        print("\nFile write test failed.")
