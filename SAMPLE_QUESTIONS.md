# CA3101 Sample Questions - All Units & Validation Types

## Legend
- VALID: Passes all layers, gets answer (may include corrections)
- WARNING: In syllabus but poor quality
- REJECTED: Gibberish or critical incorrect facts (hardcoded in Layer 2)
- OUT_OF_SYLLABUS: Not DS-related OR DS but not in CA3101

## Unit 1: Introduction
VALID: "What is Big O notation?"
WARNING: "Tell me everything about data structures"
REJECTED: "asdfghjkl"
OUT_OF_SYLLABUS: "What is AWS S3?"

## Unit 2: Arrays & Linked Lists
VALID: "What is the difference between arrays and linked lists?"
VALID: "Explain doubly linked list"
VALID: "Linked list search is O(1)" (Layer 3 corrects to O(n))
WARNING: "Which is better array or linked list?"
REJECTED: "qwertyuiop"
OUT_OF_SYLLABUS: "What is a rope data structure?"

## Unit 3: Stacks & Queues
VALID: "What is a stack and its operations?"
VALID: "Explain priority queue"
WARNING: "What is the best queue implementation?"
REJECTED: "Stack is FIFO" (hardcoded rule catches this)
REJECTED: "Queue is LIFO" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "What is Kafka queue?"

## Unit 4: Trees
VALID: "What is AVL tree rotation?"
VALID: "Explain binary search tree"
VALID: "What is a B-tree?"
WARNING: "Which tree is best?"
REJECTED: "Trees have cycles" (hardcoded rule catches this)
REJECTED: "Binary search is O(n^2)" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "What is a red-black tree?"

## Unit 5: Graphs
VALID: "Explain BFS algorithm"
VALID: "What is Dijkstra algorithm?"
VALID: "Explain Kruskal algorithm"
VALID: "Dijkstra is O(n^3)" (Layer 3 corrects complexity)
WARNING: "Which graph algorithm is best?"
REJECTED: "asdfasdf"
OUT_OF_SYLLABUS: "What is GraphQL?"

## Unit 6: Heaps
VALID: "What is a heap data structure?"
VALID: "Explain min-heap and max-heap"
VALID: "Heap sort is O(n)" (Layer 3 corrects to O(n log n))
WARNING: "Which heap is better?"
REJECTED: "tyuityui"
OUT_OF_SYLLABUS: "What is a Fibonacci heap?"

## Unit 7: Hashing
VALID: "What is hashing and hash function?"
VALID: "Explain collision resolution"
VALID: "What is linear probing?"
VALID: "Hashing is O(n^2)" (Layer 3 corrects to O(1) average)
WARNING: "Which hashing technique is best?"
REJECTED: "fghjfghj"
OUT_OF_SYLLABUS: "What is a bloom filter?"

## Unit 8: Sorting
VALID: "What is bubble sort?"
VALID: "Explain quicksort algorithm"
VALID: "What is merge sort?"
VALID: "Quicksort is O(n^3)" (Layer 3 corrects to O(n log n))
WARNING: "Which sorting is best?"
REJECTED: "Bubble sort is O(n log n)" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "How to use Arrays.sort() in Java?"

## Unit 9: Searching
VALID: "What is binary search?"
VALID: "Explain linear search"
VALID: "Linear search is O(1)" (Layer 3 corrects to O(n))
WARNING: "Which search is best?"
REJECTED: "Binary search is O(n)" (hardcoded rule catches this)
OUT_OF_SYLLABUS: "What is Elasticsearch?"

## Unit 10: Recursion
VALID: "What is recursion?"
VALID: "Explain Tower of Hanoi"
WARNING: "Is recursion better than iteration?"
REJECTED: "poiupoiu"
OUT_OF_SYLLABUS: "What is tail call optimization?"

## Notes on Incorrect Facts Handling

### Rejected by Layer 2 (8 hardcoded patterns):
1. "Binary search is O(n^2)" or O(n^3) or O(n)
2. "Stack is FIFO"
3. "Queue is LIFO"
4. "Trees have cycles"
5. "Linked list search is O(1)"
6. "Bubble sort is O(n log n)"

### Corrected by Layer 3 (Educational approach):
- "Heap sort is O(n)" → Corrects to O(n log n)
- "Quicksort is O(n^3)" → Corrects to O(n log n)
- "Hashing is O(n^2)" → Corrects to O(1) average
- "Dijkstra is O(n^3)" → Corrects to O(V^2) or O(E log V)
- "Linear search is O(1)" → Corrects to O(n)
- And many other incorrect complexity claims

This hybrid approach:
- Catches critical conceptual errors (LIFO/FIFO, cycles in trees)
- Lets LLM educate students on complexity mistakes
- Provides flexibility without maintaining 100+ hardcoded rules
