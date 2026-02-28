import hashlib
import  os

CHUNK_SIZE = 524288

def split_file (filepath) :
    chunks = []

    with open(filepath, 'rb') as file:
        while True:
            chunk = file.read(CHUNK_SIZE)
            if not chunk:
                break
            chunks.append(chunk)

    print(f"File split into {len(chunks)} chunks")

    return chunks

def reassemble_chunks (chunks, output_path) :
    with open(output_path, 'wb') as chunked_file:
        for chunk in chunks:
            chunked_file.write(chunk)
    print(f"File reassembled as '{output_path}' chunks.")

def hash_file(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as file:
        while True:
            block =  file.read(4096)
            if not block :
                break
            sha.update(block)
    return sha.hexdigest()

if __name__ == "__main__":
    original_file = "testfile.bin"
    rebuilt_file = "rebuilt.bin"

    if not os.path.exists(original_file) :
        print(f"File '{original_file}' does not exist.")
        exit(1)
    print("Splitting file...")
    chunks = split_file(original_file)

    print(f"Reassembling file...")
    reassemble_chunks(chunks, rebuilt_file)
