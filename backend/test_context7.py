import sys
import context7

print("Testing Context7 module", file=sys.stdout)
client = context7.Context7Client()
print("Context7Client instantiated", file=sys.stdout)

test_text = 'This is a test sentence. Here is another sentence. And a third one for good measure.'
print(f"Input text: {test_text}", file=sys.stdout)

try:
    chunks = client.chunk_text(test_text, chunk_size=30, overlap=5)
    print(f'Number of chunks: {len(chunks)}', file=sys.stdout)
    for i, chunk in enumerate(chunks):
        print(f'Chunk {i+1}: {chunk}', file=sys.stdout)
except Exception as e:
    print(f"Error in chunk_text: {e}", file=sys.stderr)

docs = [
    {'content': 'Embodied intelligence refers to AI systems with physical form that can interact with their environment.', 'source': 'Chapter 1', 'title': 'Introduction to Embodied AI'}
]

try:
    formatted_context = client.format_context(docs)
    print(f'Formatted context: {formatted_context}', file=sys.stdout)
except Exception as e:
    print(f"Error in format_context: {e}", file=sys.stderr)